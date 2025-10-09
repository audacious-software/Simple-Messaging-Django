# pylint: disable=line-too-long, no-member, len-as-condition, import-outside-toplevel

import datetime

import pytz

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import IncomingMessage, OutgoingMessage

def dashboard_signals():
    return [{
        'name': 'Daily Message Traffic',
        'refresh_interval': 900,
        'configuration': {
            'widget_columns': 6,
            'active': True
        }
    }]

def dashboard_template(signal_name):
    if signal_name == 'Daily Message Traffic':
        return 'dashboard/simple_dashboard_widget_daily_message_traffic.html'

    return None

def update_dashboard_signal_value(signal_name): # pylint: disable=too-many-locals
    try:
        from simple_dashboard.models import DashboardSignal

        if signal_name == 'Daily Message Traffic':
            start_date = None

            first_outgoing = OutgoingMessage.objects.all().order_by('send_date').first()

            if first_outgoing is not None:
                start_date = first_outgoing.send_date

            first_incoming = IncomingMessage.objects.all().order_by('receive_date').first()

            if first_incoming is not None and first_incoming.receive_date < start_date:
                start_date = first_incoming.receive_date

            here_tz = pytz.timezone(settings.TIME_ZONE)

            today = timezone.now().astimezone(here_tz).date()

            if start_date is None:
                start_date = timezone.now() - datetime.timedelta(days=7)

            start_date = start_date.astimezone(here_tz).date()

            signal = DashboardSignal.objects.filter(name='Daily Message Traffic').first()

            if signal is not None:
                window_size = signal.configuration.get('window_size', 60)

                window_start = today - datetime.timedelta(days=window_size)

                start_date = max(start_date, window_start)

            messages = []

            while start_date <= today:
                day_start = datetime.time(0, 0, 0, 0)

                lookup_start = here_tz.localize(datetime.datetime.combine(start_date, day_start))

                day_end = datetime.time(23, 59, 59, 999999)

                lookup_end = here_tz.localize(datetime.datetime.combine(start_date, day_end))

                day_log = {
                    'date': start_date.isoformat(),
                    'incoming_count': IncomingMessage.objects.filter(receive_date__gte=lookup_start, receive_date__lte=lookup_end).count(),
                    'outgoing_count': OutgoingMessage.objects.filter(sent_date__gte=lookup_start, sent_date__lte=lookup_end, errored=False).count(),
                    'error_count': OutgoingMessage.objects.filter(sent_date__gte=lookup_start, sent_date__lte=lookup_end, errored=True).count(),
                }

                messages.append(day_log)

                start_date += datetime.timedelta(days=1)

            return messages
    except ImportError:
        pass

    return None

def fetch_dashboard_widget(widget_name):
    if widget_name == 'simple_messaging_broadcast_message':
        return render_to_string('dashboard/widgets/simple_messaging_broadcast_message.html')

    return None


def dashboard_pages():
    return [{
        'title': 'Messages Log',
        'icon': 'forum',
        'url': reverse('dashboard_messages_log'),
    }, {
        'title': 'Phone Lookup',
        'icon': 'travel_explore',
        'url': reverse('dashboard_lookup'),
    }]
