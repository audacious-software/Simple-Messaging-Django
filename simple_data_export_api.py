# pylint: disable=line-too-long, no-member

import csv
import io
import os
import tempfile

from .models import IncomingMessage, OutgoingMessage

def export_data_sources(params=None):
    if params is None:
        params = {}

    phone_numbers = []

    for incoming in IncomingMessage.objects.all():
        sender = incoming.current_sender()

        if (sender in phone_numbers) is False:
            phone_numbers.append(sender)

    for outgoing in OutgoingMessage.objects.all():
        destination = outgoing.current_destination()

        if (destination in phone_numbers) is False:
            phone_numbers.append(destination)

    return phone_numbers

def export_data_types():
    return [
        ('simple_messaging.conversation_transcripts', 'Conversation Transcripts',),
    ]

def compile_data_export(data_type, data_sources, start_time=None, end_time=None, custom_parameters=None): # pylint: disable=too-many-locals, unused-argument, too-many-branches
    if data_type == 'simple_messaging.conversation_transcripts':
        filename = tempfile.gettempdir() + os.path.sep + 'simple_messaging.conversation_transcripts' + '.txt'

        with io.open(filename, 'w', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter='\t')

            writer.writerow([
                'Sender',
                'Recipient',
                'Timestamp',
                'Direction',
                'Message',
                'Error',
            ])

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

                    message = {
                        'sender': 'System',
                        'recipient': destination,
                        'timestamp': outgoing.sent_date.isoformat(),
                        'direction': 'to-recipient',
                        'message': outgoing.message,
                        'error': outgoing.errored,
                    }

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

                    message = {
                        'sender': sender,
                        'recipient': 'System',
                        'timestamp': incoming.receive_date.isoformat(),
                        'direction': 'to-system',
                        'message': incoming.message,
                        'error': False,
                    }

                    source_messages[sender].append(message)

            for source in data_sources:
                if source in source_messages:
                    source_messages[sender].sort(key=lambda message: message['timestamp'])

                    for message in source_messages[sender]:
                        row = []

                        row.append(message['sender'])
                        row.append(message['recipient'])
                        row.append(message['timestamp'])
                        row.append(message['direction'])
                        row.append(message['message'])
                        row.append(str(message['error']))

                        writer.writerow(row)

        return filename

    return None
