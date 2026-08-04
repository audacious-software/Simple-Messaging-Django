# pylint: disable=line-too-long

import importlib

import phonenumbers

from django.conf import settings
from django.urls import reverse

def dashboard_actions(metadata):
    actions = []

    phone = metadata.get('phone', metadata.get('phone_number', None))

    if phone is not None:
        try:
            parsed = phonenumbers.parse(phone, settings.PHONE_REGION)

            formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

            actions.append({
                'name': 'Send Text Message',
                'url': '%s?identifier=%s' % (reverse('simple_messaging_ui'), formatted),
                'icon': 'forum',
            })
        except phonenumbers.NumberParseException:
            pass

    return actions

def dashboard_additional_columns(obj=None):
    if obj is None:
        return [{
            'name': 'Unread'
        }]

    column_values = []

    phone_number = obj.get('phone_number', None)

    if phone_number is not None:
        try:
            parsed = phonenumbers.parse(phone_number, settings.PHONE_REGION)

            formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

            unread_count = 0

            for app in settings.INSTALLED_APPS:
                try:
                    messaging_module = importlib.import_module('.simple_messaging_api', package=app)

                    unread_count = messaging_module.new_message_count(formatted)
                except ImportError:
                    pass
                except AttributeError:
                    pass

            when = 0

            for app in settings.INSTALLED_APPS:
                try:
                    messaging_module = importlib.import_module('.simple_messaging_api', package=app)

                    when = messaging_module.fetch_last_console_view(formatted)
                except ImportError:
                    pass
                except AttributeError:
                    pass

            column_values.append({
                'display': '%s' % unread_count,
                'action': '%s?identifier=%s&when=%s' % (reverse('simple_messaging_ui'), formatted, when),
                'align': 'center',
            })
        except phonenumbers.NumberParseException:
            column_values.append({
                'display': '',
                'action': None
            })
    else:
        column_values.append({
            'display': '',
            'action': None
        })

    return column_values
