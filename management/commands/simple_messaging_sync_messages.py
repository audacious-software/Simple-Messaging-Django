# pylint: disable=no-member, line-too-long, superfluous-parens

import datetime
import importlib
import json
import mimetypes

from io import BytesIO

import requests

from django.conf import settings
from django.core import files
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments, handle_logging

from ...decorators import log_scheduled_event
from ...models import OutgoingMessage, OutgoingMessageMedia, IncomingMessage, IncomingMessageMedia

class Command(BaseCommand):
    help = 'Queries cloud servers (where applicable to synchronize message transcripts'

    @add_qs_arguments
    def add_arguments(self, parser):
        parser.add_argument('--since-minutes', required=False, type=int, default=60, help='Backward querying time window from this parameter (in minmutes) to now.')
        parser.add_argument('--process', action='store_true', help='Indicates whether messaages should just be stored in the transcript list or fully processed (e.g. sent to dialog system).')

    @handle_logging
    @handle_schedule
    @handle_lock
    @log_scheduled_event
    def handle(self, *args, **options): # pylint: disable=too-many-locals, too-many-branches, too-many-statements, too-many-nested-blocks
        since_minutes = options.get('since_minutes', 60)
        process = options.get('process', False)

        now = timezone.now()

        start = now - datetime.timedelta(seconds=(60 * since_minutes))

        messages = []

        for app in settings.INSTALLED_APPS:
            try:
                response_module = importlib.import_module('.simple_messaging_api', package=app)

                module_messages = response_module.fetch_sync_messages(since=start)

                messages.extend(module_messages)
            except ImportError:
                pass
            except AttributeError:
                pass

        messages.sort(key=lambda message: message['sent'])

        for message in messages: # pylint: disable=too-many-nested-blocks
            if message['direction'] == 'incoming':
                found = None

                start_window = message['sent'] - datetime.timedelta(seconds=(60 * 60))
                end_window = message['sent'] + datetime.timedelta(seconds=(60 * 60))

                for incoming_message in IncomingMessage.objects.filter(receive_date__gte=start_window, receive_date__lte=end_window):
                    metadata = json.loads(incoming_message.transmission_metadata)

                    for id_field, id_value in message.get('id', {}).items():
                        existing_value = metadata.get(id_field, None)

                        if existing_value is not None:
                            if isinstance(existing_value, (list, tuple,)) and (id_value in existing_value):
                                found = incoming_message.pk
                            elif id_value == existing_value:
                                found = incoming_message.pk

                    if found is not None:
                        break

                if found is None:
                    new_message = IncomingMessage()

                    new_message.sender = message.get('from', None)
                    new_message.recipient = message.get('to', None)

                    new_message.receive_date = message.get('sent', None)
                    new_message.message = message.get('message', None)

                    transmission_metadata = {}

                    for id_field, id_value in message.get('id', {}).items():
                        transmission_metadata[id_field] = id_value

                    transmission_metadata['sync_data'] = message
                    transmission_metadata['sync_date'] = timezone.now()

                    new_message.transmission_metadata = json.dumps(transmission_metadata, indent=2, cls=DjangoJSONEncoder)

                    new_message.save()

                    for media_ref in message.get('media', []):
                        media_obj = IncomingMessageMedia(message=new_message)

                        media_obj.content_url = media_ref.get('url', None)
                        media_obj.content_type = media_ref.get('content_type', None)

                        media_obj.save()

                        media_response = requests.get(media_obj.content_url, timeout=120)

                        if media_response.status_code != requests.codes.ok:
                            continue

                        filename = media_obj.content_url.split('/')[-1]

                        extension = mimetypes.guess_extension(media_obj.content_type)

                        if extension is not None:
                            if extension == '.jpe':
                                extension = '.jpg'

                        filename += extension

                        file_bytes = BytesIO()
                        file_bytes.write(media_response.content)

                        media_obj.content_file.save(filename, files.File(file_bytes))
                        media_obj.save()

                    if process is False:
                        for app in settings.INSTALLED_APPS:
                            try:
                                response_module = importlib.import_module('.simple_messaging_api', package=app)

                                response_module.process_incoming_message(new_message)
                            except ImportError:
                                pass
                            except AttributeError:
                                pass
            else:
                found = None

                start_window = message['sent'] - datetime.timedelta(seconds=(60 * 60))
                end_window = message['sent'] + datetime.timedelta(seconds=(60 * 60))

                for outgoing_message in OutgoingMessage.objects.filter(sent_date__gte=start_window, sent_date__lte=end_window):
                    metadata = json.loads(outgoing_message.transmission_metadata)

                    for id_field, id_value in message.get('id', {}).items():
                        existing_value = metadata.get(id_field, None)

                        if existing_value is not None:
                            if isinstance(existing_value, (list, tuple,)) and (id_value in existing_value):
                                found = outgoing_message.pk
                            elif id_value == existing_value:
                                found = outgoing_message.pk

                    if found is not None:
                        break

                if found is None:
                    new_message = OutgoingMessage()

                    new_message.destination = message.get('to', None)

                    new_message.send_date = message.get('sent', None)
                    new_message.sent_date = message.get('sent', None)

                    new_message.message = message.get('message', None)

                    transmission_metadata = {}

                    for id_field, id_value in message.get('id', {}).items():
                        transmission_metadata[id_field] = id_value

                    transmission_metadata['sync_data'] = message
                    transmission_metadata['sync_date'] = timezone.now()

                    new_message.transmission_metadata = json.dumps(transmission_metadata, indent=2, cls=DjangoJSONEncoder)

                    new_message.save()

                    for media_ref in message.get('media', []):
                        media_obj = OutgoingMessageMedia(message=new_message)

                        media_url = media_ref.get('url', None)

                        media_obj.content_type = media_ref.get('content_type', None)

                        media_obj.save()

                        media_response = requests.get(media_url, timeout=120)

                        if media_response.status_code != requests.codes.ok:
                            continue

                        filename = media_url.split('/')[-1]

                        extension = mimetypes.guess_extension(media_obj.content_type)

                        if extension is not None:
                            if extension == '.jpe':
                                extension = '.jpg'

                        filename += extension

                        file_bytes = BytesIO()
                        file_bytes.write(media_response.content)

                        media_obj.content_file.save(filename, files.File(file_bytes))
                        media_obj.save()
