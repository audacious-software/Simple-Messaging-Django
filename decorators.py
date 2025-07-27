# pylint: disable=pointless-string-statement

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


'''
Logs timestamp to Nagios monitoring system for last run of scheduled job.
'''
def log_scheduled_event(handle):
    def wrapper(self, *args, **options):
        try:
            from nagios_monitor.models import ScheduledEvent # pylint: disable=import-error, import-outside-toplevel

            event_name = self.__module__.split('.').pop()

            try:
                event_prefix = settings.SITE_URL.split('//')[1].replace('/', '').replace('.', '-')
            except AttributeError:
                try:
                    event_prefix = settings.ALLOWED_HOSTS[0].replace('.', '-')
                except IndexError:
                    event_prefix = 'simple_messaging_scheduled_event'

            event_prefix = slugify(event_prefix)

            ScheduledEvent.log_event(event_prefix + '_' + event_name, timezone.now())

        except ImportError:
            # nagios_monitor app not installed
            pass

        handle(self, *args, **options)

    return wrapper
