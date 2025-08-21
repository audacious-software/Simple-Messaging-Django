import binascii
import json

import requests

from future.moves.urllib.parse import urlparse
from nacl.signing import SigningKey

from django.conf import settings

def fetch_short_url_metadata(outgoing_message):
    return {
        'simple_messaging.OutgoingMessage': '%s:%s' % (settings.ALLOWED_HOSTS[0], outgoing_message.pk,)
    }

def shorten_url(long_url, tracking_code=None, metadata=None): # pylint: disable=too-many-branches
    if hasattr(settings, 'SHORT_URL_SIGNING_KEY') and hasattr(settings, 'SHORT_URL_CREATE_URL'):
        shortener_url = urlparse(settings.SHORT_URL_CREATE_URL)
        remote_url = urlparse(long_url)

        if shortener_url.netloc.lower() != remote_url.netloc.lower():
            signing_key = SigningKey(binascii.unhexlify(settings.SHORT_URL_SIGNING_KEY))

            signature = binascii.b2a_hex(signing_key.sign(long_url.encode('utf-8')).signature)

            payload = {
                'url': long_url,
                'signature': signature,
            }

            if metadata is not None:
                xmit_metadata = metadata.copy()

                if 'url_mappings' in xmit_metadata:
                    del xmit_metadata['url_mappings']

                payload['client_metadata'] = json.dumps(xmit_metadata)

            if tracking_code is not None and tracking_code != '':
                payload['tracking_code'] = tracking_code

            fetch_request = requests.post(settings.SHORT_URL_CREATE_URL, data=payload, timeout=120)

            if fetch_request.status_code >= 200 and fetch_request.status_code < 300:
                short_url = fetch_request.json()['short_url']

                if metadata is not None:
                    if ('url_mappings' in metadata) is False:
                        metadata['url_mappings'] = {}

                    metadata['url_mappings'][long_url] = short_url

                return short_url

    if hasattr(settings, 'BITLY_ACCESS_CODE'):
        if ('bit.ly' in long_url.lower()) is False:
            headers = {'Authorization': 'Bearer ' + settings.BITLY_ACCESS_CODE}

            post_data = {'long_url': long_url}

            fetch_url = 'https://api-ssl.bitly.com/v4/shorten'

            fetch_request = requests.post(fetch_url, headers=headers, json=post_data, timeout=120)

            if fetch_request.status_code >= 200 and fetch_request.status_code < 300:
                short_url = fetch_request.json()['link']

                if metadata is not None:
                    if ('url_mappings' in metadata) is False:
                        metadata['url_mappings'] = {}

                    metadata['url_mappings'][long_url] = short_url

                return short_url

    return None
