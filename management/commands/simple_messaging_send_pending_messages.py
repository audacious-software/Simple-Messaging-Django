# pylint: disable=no-member, line-too-long

from django.core.management.base import BaseCommand
from django.utils import timezone

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments, handle_logging

from ...decorators import log_scheduled_event
from ...models import OutgoingMessage

class Command(BaseCommand):
    help = 'Transmits unsent pending messages'

    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_logging
    @handle_schedule
    @handle_lock
    @log_scheduled_event
    def handle(self, *args, **options):
        now = timezone.now()

        for pending in OutgoingMessage.objects.filter(send_date__lte=now, sent_date=None, errored=False):
            pending.transmit()
