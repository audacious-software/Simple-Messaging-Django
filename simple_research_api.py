import phonenumbers

from django.conf import settings
from django.urls import reverse

def dashboard_actions(metadata):
    actions = []

    phone = metadata.get('phone', metadata.get('phone_number', None))

    if phone is not None:
        parsed = phonenumbers.parse(phone, settings.PHONE_REGION)

        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        actions.append({
            'name': 'Send Text Message',
            'url': '%s?identifier=%s' % (reverse('simple_messaging_ui'), formatted),
            'icon': 'forum',
        })

    return actions
