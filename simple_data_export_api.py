# pylint: disable=line-too-long, no-member

import io
import importlib
import json
import os
import tempfile

import phonenumbers
import pytz

from django.conf import settings
from django.db import connection

from simple_data_export.utils import fetch_export_identifier, UnicodeWriter # pylint: disable=import-error

from .models import IncomingMessage, OutgoingMessage

def export_data_sources(params=None): # pylint: disable=too-many-branches
    if params is None:
        params = {}

    data_sources = []

    incomings = IncomingMessage.objects.all()

    if connection.vendor != 'sqlite':
        incomings = IncomingMessage.objects.distinct('lookup_key')

    for incoming in incomings:
        if incoming.lookup_key is not None:
            sender = incoming.current_sender()

            if (sender in data_sources) is False:
                data_sources.append(sender)

    if connection.vendor != 'sqlite':
        for incoming in IncomingMessage.objects.filter(lookup_key=None):
            sender = incoming.current_sender()

            if (sender in data_sources) is False:
                data_sources.append(sender)

    outgoings = OutgoingMessage.objects.all()

    if connection.vendor != 'sqlite':
        outgoings = OutgoingMessage.objects.distinct('lookup_key')

    for outgoing in outgoings:
        if outgoing.lookup_key is not None:
            destination = outgoing.current_destination()

            if (destination in data_sources) is False:
                data_sources.append(destination)

    if connection.vendor != 'sqlite':
        for outgoing in OutgoingMessage.objects.filter(lookup_key=None):
            destination = outgoing.current_destination()

            if (destination in data_sources) is False:
                data_sources.append(destination)

    return data_sources

def export_data_types():
    return [
        ('simple_messaging.conversation_transcripts', 'Conversation Transcripts',),
    ]

def compile_data_export(data_type, data_sources, start_time=None, end_time=None, custom_parameters=None): # pylint: disable=too-many-locals, unused-argument, too-many-branches, too-many-statements
    here_tz = pytz.timezone(settings.TIME_ZONE)

    if data_type == 'simple_messaging.conversation_transcripts':
        filename = tempfile.gettempdir() + os.path.sep + 'simple_messaging.conversation_transcripts' + '.txt'

        with io.open(filename, 'wb') as outfile:
            writer = UnicodeWriter(outfile, delimiter='\t')

            headers = [
                'Sender',
                'Recipient',
                'Timestamp',
                'Direction',
                'Message',
                'Error',
            ]

            extra_fields = []

            for app in settings.INSTALLED_APPS:
                try:
                    response_module = importlib.import_module('.simple_data_export_api', package=app)

                    extra_fields.extend(response_module.simple_data_export_fields(data_type))
                except ImportError:
                    pass
                except AttributeError:
                    pass

            headers.extend(extra_fields)

            writer.writerow(headers)

            source_messages = {}

            outgoing_query = OutgoingMessage.objects.exclude(sent_date=None)

            if start_time is not None:
                outgoing_query = outgoing_query.filter(sent_date__gte=start_time)

            if end_time is not None:
                outgoing_query = outgoing_query.filter(sent_date__lte=end_time)

            for outgoing in outgoing_query:
                destination = outgoing.current_destination()

                if destination in data_sources:
                    if (destination in source_messages) is False:
                        source_messages[destination] = []

                    transmission_metadata = json.loads(outgoing.transmission_metadata)

                    message = {
                        'sender': 'System',
                        'recipient': fetch_export_identifier(destination),
                        'raw_recipient': destination,
                        'timestamp': outgoing.sent_date.astimezone(here_tz).isoformat(),
                        'datetime': outgoing.sent_date.astimezone(here_tz),
                        'direction': 'to-recipient',
                        'message': outgoing.message.replace('\r', ' ').replace('\n', ' '),
                        'channel': transmission_metadata.get('message_channel', None),
                        'error': outgoing.errored,
                        'id': outgoing.pk,
                    }

                    for app in settings.INSTALLED_APPS:
                        try:
                            response_module = importlib.import_module('.simple_data_export_api', package=app)

                            message.update(response_module.simple_data_export_field_values(data_type, message, extra_fields))
                        except ImportError:
                            pass
                        except AttributeError:
                            pass

                    source_messages[destination].append(message)

            incoming_query = IncomingMessage.objects.exclude(receive_date=None)

            if start_time is not None:
                incoming_query = incoming_query.filter(receive_date__gte=start_time)

            if end_time is not None:
                incoming_query = incoming_query.filter(receive_date__lte=end_time)

            for incoming in incoming_query:
                sender = incoming.current_sender()

                if sender in data_sources:
                    if (sender in source_messages) is False:
                        source_messages[sender] = []

                    transmission_metadata = json.loads(incoming.transmission_metadata)

                    message = {
                        'sender': fetch_export_identifier(sender),
                        'raw_sender': sender,
                        'recipient': 'System',
                        'timestamp': incoming.receive_date.astimezone(here_tz).isoformat(),
                        'datetime': incoming.receive_date.astimezone(here_tz),
                        'direction': 'to-system',
                        'message': incoming.message.replace('\r', ' ').replace('\n', ' '),
                        'channel': transmission_metadata.get('message_channel', None),
                        'error': False,
                        'id': incoming.pk,
                    }

                    for app in settings.INSTALLED_APPS:
                        try:
                            response_module = importlib.import_module('.simple_data_export_api', package=app)

                            message.update(response_module.simple_data_export_field_values(data_type, message, extra_fields))
                        except ImportError:
                            pass
                        except AttributeError:
                            pass

                    source_messages[sender].append(message)

            for source in data_sources:
                if source in source_messages:
                    source_messages[source].sort(key=lambda message: message['timestamp'])

                    for message in source_messages[source]:
                        row = []

                        row.append(message['sender'])
                        row.append(message['recipient'])
                        row.append(message['timestamp'])
                        row.append(message['direction'])
                        row.append(message['message'])
                        row.append(str(message['error']))

                        for extra_field in extra_fields:
                            row.append(str(message.get(extra_field, '')))

                        writer.writerow(row)

        return filename

    return None

def obfuscate_identifier(identifier):
    if settings.SIMPLE_DATA_EXPORTER_OBFUSCATE_IDENTIFIERS: # pylint: disable=too-many-nested-blocks
        try:
            number = phonenumbers.parse(identifier, settings.SIMPLE_MESSAGING_COUNTRY_CODE)

            formatted = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

            if phonenumbers.is_valid_number(number):
                if number.country_code == 1:
                    new_formatted = ''

                    for i in range(0, len(formatted)): # pylint: disable=consider-using-enumerate
                        if i in (2, 3, 4, 5, 6,):
                            new_formatted += 'X'
                        else:
                            new_formatted += formatted[i]

                    return new_formatted

            new_formatted = ''

            for i in range(0, len(formatted)): # pylint: disable=consider-using-enumerate
                if i < (len(formatted) - 5):
                    new_formatted += 'X'
                else:
                    new_formatted += formatted[i]

            return new_formatted

        except phonenumbers.phonenumberutil.NumberParseException:
            pass

    return None
