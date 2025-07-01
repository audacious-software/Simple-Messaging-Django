# pylint: disable=no-member, line-too-long

import datetime
import importlib
import logging
import json

import arrow
import phonenumbers
import pytz

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from .models import IncomingMessage, OutgoingMessage, OutgoingMessageMedia, fetch_messages, fetch_destination_proxy

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

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
def simple_messaging_ui(request): # pylint:disable=too-many-branches, too-many-statements
    context = {
        'identifier': request.GET.get('identifier', ''),
        'media_enabled': True,
    }

    precomposed = []

    channels = []

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

            if response_module.simple_messaging_media_enabled(None):
                context['media_enabled'] = True
        except ImportError:
            pass
        except AttributeError:
            pass

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            channels.extend(response_module.simple_messaging_fetch_active_channels())
        except ImportError:
            pass
        except AttributeError:
            pass

    custom_ui = None

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            app_custom_ui = response_module.simple_messaging_custom_console_ui(context)

            if app_custom_ui is not None:
                if custom_ui is None:
                    custom_ui = app_custom_ui
                else:
                    custom_ui += app_custom_ui
        except ImportError:
            pass
        except AttributeError:
            pass

    custom_title = None

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            custom_title = response_module.simple_messaging_custom_title(context)
        except ImportError:
            pass
        except AttributeError:
            pass

    if len(precomposed) > 0: # pylint: disable=len-as-condition
        context['precomposed'] = precomposed

    if len(channels) == 0: # pylint: disable=len-as-condition
        channels.append(['simple_messaging_ui_default', 'Default Channel'])

    context['channels'] = channels
    context['custom_ui'] = custom_ui
    context['custom_title'] = custom_title

    if len(channels) == 1:
        context['channel_class'] = 'col-md-12'
    elif len(channels) == 2:
        context['channel_class'] = 'col-md-6'
    elif len(channels) == 3:
        context['channel_class'] = 'col-md-4'
    elif len(channels) == 4:
        context['channel_class'] = 'col-md-3'
    elif len(channels) < 7:
        context['channel_class'] = 'col-md-2'
    else:
        context['channel_class'] = 'col-md-1'

    return render(request, 'simple_messaging_ui.html', context)

@staff_member_required
def simple_messaging_messages_json(request): # pylint: disable=too-many-branches
    messages = []

    phone = request.POST.get('phone', request.GET.get('phone', ''))
    since = float(request.POST.get('since', request.GET.get('since', '0')))

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

    destination = phone

    try:
        if hasattr(settings, 'PHONE_REGION'):
            parsed = phonenumbers.parse(phone, settings.PHONE_REGION)

            destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass

    for message in IncomingMessage.objects.filter(receive_date__gt=start_time):
        if message.current_sender() == destination:
            media_urls = message.media_urls()

            messages.append({
                'direction': 'from-user',
                'channel': 'simple_messaging_ui_default',
                'sender': destination,
                'message': message.current_message(),
                'timestamp': arrow.get(message.receive_date).float_timestamp,
                'media_urls': media_urls,
                'message_id': message.pk,
            })

    for message in OutgoingMessage.objects.filter(sent_date__gt=start_time):
        if message.current_destination() == destination:
            messages.append({
                'direction': 'from-system',
                'channel': 'simple_messaging_ui_default',
                'recipient': destination,
                'message': message.current_message(),
                'timestamp': arrow.get(message.sent_date).float_timestamp,
                'media_urls': message.media_urls(),
                'message_id': message.pk,
            })

    for app in settings.INSTALLED_APPS:
        try:
            message_module = importlib.import_module('.simple_messaging_api', package=app)

            message_module.update_last_console_view(phone)
        except ImportError:
            pass
        except AttributeError:
            pass

    for app in settings.INSTALLED_APPS:
        try:
            message_module = importlib.import_module('.simple_messaging_api', package=app)

            message_module.annotate_console_messages(messages)
        except ImportError:
            pass
        except AttributeError:
            pass

    return HttpResponse(json.dumps(messages, indent=2), content_type='application/json', status=200)

@staff_member_required
def simple_messaging_send_json(request): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
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

        destination = phone

        try:
            if hasattr(settings, 'PHONE_REGION'):
                parsed = phonenumbers.parse(phone, settings.PHONE_REGION)
                destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            pass

        outgoing = OutgoingMessage.objects.create(destination=destination, send_date=timezone.now(), message=message)

        transmission_metadata = {
            'message_channel': request.POST.get('channel', None)
        }

        outgoing.transmission_metadata = json.dumps(transmission_metadata, indent=2)
        outgoing.save()

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

        for app in settings.INSTALLED_APPS:
            if real_phone is None:
                try:
                    message_module = importlib.import_module('.simple_messaging_api', package=app)

                    real_phone = message_module.annotate_messsage(outgoing, request.POST)
                except ImportError:
                    pass
                except AttributeError:
                    pass

        call_command('simple_messaging_send_pending_messages')

        outgoing = OutgoingMessage.objects.get(pk=outgoing.pk)

        if outgoing.errored is False:
            result['success'] = True
        else:
            result['error'] = 'Unable to send message, please investigate.'

    return HttpResponse(json.dumps(result, indent=2), content_type='application/json', status=200)

@staff_member_required
def simple_messaging_lookup(request): # pylint: disable=too-many-locals
    return render(request, 'simple_messaging_lookup.html')

@staff_member_required
def simple_messaging_lookup_json(request): # pylint: disable=too-many-locals
    results = []

    phone_numbers = request.POST.get('numbers', request.GET.get('numbers', '')).splitlines()

    phone_numbers = list(filter(lambda x: x.strip() != '', phone_numbers)) # pylint: disable=deprecated-lambda

    for app in settings.INSTALLED_APPS:
        if len(phone_numbers) > 0: # pylint: disable=len-as-condition
            try:
                message_module = importlib.import_module('.simple_messaging_api', package=app)

                results.extend(message_module.lookup_numbers(phone_numbers))
            except ImportError:
                pass
            except AttributeError:
                pass

    return HttpResponse(json.dumps(results, indent=2), content_type='application/json', status=200)

@staff_member_required
def dashboard_lookup(request):
    context = {}

    return render(request, 'dashboard/dashboard_messages_lookup.html', context=context)

@staff_member_required
def dashboard_messages_log(request, start=None):
    context = {}

    if start is None:
        return redirect('dashboard_messages_log', start=timezone.now().isoformat())

    context['messages'] = fetch_messages()

    return render(request, 'dashboard/dashboard_messages_log.html', context=context)

@never_cache
@staff_member_required
def dashboard_broadcast(request): # pylint: disable=invalid-name
    if request.method == 'POST':
        identifiers = json.loads(request.POST.get('identifiers', '[]'))
        message = request.POST.get('message', None)
        when = request.POST.get('when', '')

        if message is not None and message.strip() != '':
            for identifier in identifiers:
                destination = fetch_destination_proxy(identifier)

                when_send = timezone.now()

                if when != '':
                    when_send = pytz.timezone(destination.fetch_tz()).localize(datetime.datetime.strptime(when, '%Y-%m-%dT%H:%M'))

                outgoing = OutgoingMessage.objects.create(destination=destination.fetch_destination(), send_date=when_send, message=message)
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

            response_json = {
                'message': 'Message broadcast scheduled.',
                'reset': True,
                'reload': True
            }

            return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

        response_json = {
            'message': 'No message provided. None sent.',
            'reset': True,
            'reload': False
        }

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseRedirect(reverse('dashboard_messages_log_now'))
