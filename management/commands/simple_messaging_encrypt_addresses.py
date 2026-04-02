# pylint: disable=no-member, line-too-long

import importlib

from django.conf import settings
from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock

from ...models import IncomingMessage, OutgoingMessage

class Command(BaseCommand):
    help = 'Encrypts any cleartext phone numbers if suitable key is present.'

    @handle_lock
    def handle(self, *args, **options):
        for message in OutgoingMessage.objects.all():
            message.encrypt_destination()

        for message in IncomingMessage.objects.all():
            message.encrypt_sender()

        for app in settings.INSTALLED_APPS:
            try:
                message_module = importlib.import_module('.simple_messaging_api', package=app)

                message_module.encrypt_addresses()
            except ImportError:
                pass
            except AttributeError:
                pass
