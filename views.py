# pylint: disable=no-member, line-too-long

import importlib
import json

import arrow
import phonenumbers

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import IncomingMessage, OutgoingMessage, OutgoingMessageMedia

@csrf_exempt
def incoming_message_request(request):
    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            response = response_module.process_incoming_request(request)

            if response is not None:
                return response
        except ImportError:
            pass
        except AttributeError:
            pass

    raise Http404("No module found to process incoming message.")

@staff_member_required
def simple_messaging_ui(request):
    context = {
        'identifier': request.GET.get('identifier', ''),
        'media_enabled': False,
    }

    precomposed = []

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            precomposed.extend(response_module.simple_messaging_precomposed_messages())
        except ImportError:
            pass
        except AttributeError:
            pass

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            if response_module.simple_messaging_media_enabled():
                context['media_enabled'] = True
        except ImportError:
            pass
        except AttributeError:
            pass

    if len(precomposed) > 0: # pylint: disable=len-as-condition
        context['precomposed'] = precomposed

    return render(request, 'simple_messaging_ui.html', context)

@staff_member_required
def simple_messaging_messages_json(request): # pylint: disable=too-many-branches
    messages = []

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        since = float(request.POST.get('since', '0'))

        start_time = arrow.get(since).datetime

        real_phone = None

        for app in settings.INSTALLED_APPS:
            if real_phone is None:
                try:
                    message_module = importlib.import_module('.simple_messaging_api', package=app)

                    real_phone = message_module.fetch_phone_number(phone)
                except ImportError:
                    pass
                except AttributeError:
                    pass

        if real_phone is not None:
            phone = real_phone

        try:
            parsed = phonenumbers.parse(phone, settings.PHONE_REGION)

            destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

            for message in IncomingMessage.objects.filter(receive_date__gt=start_time):
                if message.current_sender() == destination:
                    media_urls = message.media_urls()

                    messages.append({
                        'direction': 'from-user',
                        'sender': destination,
                        'message': message.current_message(),
                        'timestamp': arrow.get(message.receive_date).float_timestamp,
                        'media_urls': media_urls,
                    })

            for message in OutgoingMessage.objects.filter(sent_date__gt=start_time):
                media_urls = message.media_urls()

                if message.current_destination() == destination:
                    messages.append({
                        'direction': 'from-system',
                        'recipient': destination,
                        'message': message.current_message(),
                        'timestamp': arrow.get(message.sent_date).float_timestamp,
                        'media_urls': media_urls,
                    })

            for app in settings.INSTALLED_APPS:
                try:
                    message_module = importlib.import_module('.simple_messaging_api', package=app)

                    message_module.update_last_console_view(phone)
                except ImportError:
                    pass
                except AttributeError:
                    pass

        except phonenumbers.NumberParseException:
            pass

    return HttpResponse(json.dumps(messages, indent=2), content_type='application/json', status=200)

@staff_member_required
def simple_messaging_send_json(request): # pylint: disable=too-many-locals
    result = {
        'success': False
    }

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')

        real_phone = None

        for app in settings.INSTALLED_APPS:
            if real_phone is None:
                try:
                    message_module = importlib.import_module('.simple_messaging_api', package=app)

                    real_phone = message_module.fetch_phone_number(phone)
                except ImportError:
                    pass
                except AttributeError:
                    pass

        if real_phone is not None:
            phone = real_phone

        parsed = phonenumbers.parse(phone, settings.PHONE_REGION)
        destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        outgoing = OutgoingMessage.objects.create(destination=destination, send_date=timezone.now(), message=message)
        outgoing.encrypt_message()
        outgoing.encrypt_destination()

        outgoing_files = []

        for key in request.FILES.keys():
            outgoing_files.append(request.FILES[key])

        index_counter = 0

        for outgoing_file in outgoing_files:
            media = OutgoingMessageMedia(message=outgoing)

            media.content_type = outgoing_file.content_type
            media.index = index_counter

            media.save()

            index_counter += 1

            media.content_file.save(outgoing_file.name, outgoing_file)

        call_command('simple_messaging_send_pending_messages')

        outgoing = OutgoingMessage.objects.get(pk=outgoing.pk)

        if outgoing.errored is False:
            result['success'] = True
        else:
            result['error'] = 'Unable to send message, please investigate.'

    return HttpResponse(json.dumps(result, indent=2), content_type='application/json', status=200)
