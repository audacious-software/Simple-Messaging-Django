# pylint: disable=no-member, line-too-long

import binascii
import json
import logging

import requests
import six

from nacl.signing import SigningKey

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments

from ...decorators import log_scheduled_event

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

class Command(BaseCommand):
    help = 'Diagnostic command for retrieving short URLs created by this client'

    @add_qs_arguments
    def add_arguments(self, parser):
        pass

    @handle_schedule
    @handle_lock
    @log_scheduled_event
    def handle(self, *args, **options):
        if hasattr(settings, 'SHORT_URL_SIGNING_KEY') and hasattr(settings, 'SHORT_URL_FETCH_URL'):
            signing_key = SigningKey(binascii.unhexlify(settings.SHORT_URL_SIGNING_KEY))

            signature_value = timezone.now().isoformat()[:16]

            signature = binascii.b2a_hex(signing_key.sign(signature_value.encode('utf-8')).signature)

            payload = {
                'signature': signature,
            }

            fetch_request = requests.post(settings.SHORT_URL_FETCH_URL, data=payload, timeout=120)

            if fetch_request.status_code >= 200 and fetch_request.status_code < 300:
                response = fetch_request.json()

                six.print_('Response: %s' % json.dumps(response, indent=2))
