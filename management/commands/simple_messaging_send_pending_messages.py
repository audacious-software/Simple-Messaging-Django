# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...decorators import handle_lock, log_scheduled_event

from ...models import OutgoingMessage

class Command(BaseCommand):
    help = 'Transmits unsent pending messages'

    @handle_lock
    @log_scheduled_event
    def handle(self, *args, **options):
        now = timezone.now()

        for pending in OutgoingMessage.objects.filter(send_date__lte=now, sent_date=None, errored=False):
            pending.transmit()
