# pylint: disable=no-member, line-too-long

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
