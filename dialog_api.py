# pylint: disable=line-too-long,no-member

import datetime

import phonenumbers

from django.conf import settings
from django.utils import timezone

from .models import OutgoingMessage

def evaluate_launch_keyword_context(sender, context):
    if 'not_messaged_in_seconds' in context:
        seconds_since = context.get('not_messaged_in_seconds', None)

        if isinstance(seconds_since, (int, float)):
            since = timezone.now() - datetime.timedelta(seconds=seconds_since)

            destination = sender

            try:
                parsed = phonenumbers.parse(sender, settings.PHONE_REGION)

                destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.NumberParseException:
                pass

            messages = OutgoingMessage.models.messages_to_destination(destination, since=since, include_unsent=False)

            if len(messages) > 0: # pylint: disable=len-as-condition
                return False

            return True

        return False

    return True
