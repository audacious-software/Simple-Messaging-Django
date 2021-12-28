# pylint: disable=no-member

import json

from .models import OutgoingMessage

def issues():
    error_count = 0

    for message in OutgoingMessage.objects.filter(errored=True):
        try:
            metadata = json.loads(message.transmission_metadata)

            if ('error_handled' in metadata) is False:
                error_count += 1
        except ValueError:
            pass

    detected_issues = []

    if error_count > 0:
        detected_issues.append(('Unhandled errored messages: %d' % error_count))

    return detected_issues
