# pylint: disable=line-too-long, no-member
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import importlib
import json
import time
import traceback

import requests

from nacl.secret import SecretBox
from twilio.rest import Client

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_str

def decrypt_value(stored_text):
    try:
        key = base64.b64decode(settings.SIMPLE_MESSAGING_SECRET_KEY) # getpass.getpass('Enter secret backup key: ')

        box = SecretBox(key)

        ciphertext = base64.b64decode(stored_text.replace('secret:', '', 1))

        cleartext = box.decrypt(ciphertext)

        return smart_str(cleartext)

    except AttributeError:
        pass

    return None

def encrypt_value(cleartext):
    try:
        key = base64.b64decode(settings.SIMPLE_MESSAGING_SECRET_KEY) # getpass.getpass('Enter secret backup key: ')

        box = SecretBox(key)

        uft8_bytes = cleartext.encode('utf-8')

        ciphertext = box.encrypt(uft8_bytes)

        return 'secret:' + smart_str(base64.b64encode(ciphertext))

    except AttributeError:
        pass

    return None

class OutgoingMessage(models.Model):
    destination = models.CharField(max_length=256)

    reference_id = models.IntegerField(null=True, blank=True)

    send_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)

    message = models.TextField(max_length=1024)

    errored = models.BooleanField(default=False)

    transmission_metadata = models.TextField(blank=True, null=True)

    def fetch_message(self, metadata): # pylint: disable=dangerous-default-value
        tokens = self.message.split(' ')

        new_tokens = []

        for token in tokens: # pylint: disable=too-many-nested-blocks
            if token.lower().startswith('http://') or token.lower().startswith('https://'):
                try:
                    if ('bit.ly' in token.lower()) is False:
                        link = token

                        headers = {'Authorization': 'Bearer ' + settings.BITLY_ACCESS_CODE}

                        # post_data = {'long_url': urllib.quote_plus(self.get_absolute_url())}
                        post_data = {'long_url': link}

                        fetch_url = 'https://api-ssl.bitly.com/v4/shorten'

                        fetch_request = requests.post(fetch_url, headers=headers, json=post_data)

                        if fetch_request.status_code >= 200 and fetch_request.status_code < 300:
                            if metadata is not None and ('shortened_urls' in metadata) is False:
                                metadata['shortened_urls'] = {}

                            link = fetch_request.json()['link']

                            metadata['shortened_urls'][post_data['long_url']] = link

                        new_tokens.append(link)
                    else:
                        new_tokens.append(token)
                except AttributeError:
                    new_tokens.append(token)
            else:
                new_tokens.append(token)

        self.message = ' '.join(new_tokens)
        self.save()

        return self.message

    def current_destination(self):
        if self.destination is not None and self.destination.startswith('secret:'):
            return decrypt_value(self.destination)

        return self.destination

    def update_destination(self, new_destination, force=False):
        if force is False and new_destination == self.current_destination():
            return # Same as current - don't add

        if hasattr(settings, 'SIMPLE_MESSAGING_SECRET_KEY'):
            encrypted_dest = encrypt_value(new_destination)

            self.destination = encrypted_dest
        else:
            self.destination = new_destination

        self.save()

    def encrypt_destination(self):
        if self.destination.startswith('secret:') is False:
            self.update_destination(self.destination, force=True)

    def transmit(self):
        if self.sent_date is not None:
            raise Exception('Message (pk=' + str(self.pk) + ') already transmitted on ' + self.sent_date.isoformat() + '.')

        self.sent_date = timezone.now() # Saving early to avoid accidental duplicate sends.
        self.save()

        try:
            processed = False
            processed_metadata = {}

            for app in settings.INSTALLED_APPS:
                try:
                    response_module = importlib.import_module('.simple_messaging_api', package=app)

                    metadata = response_module.process_outgoing_message(self)

                    if metadata is not None:
                        processed = True
                        processed_metadata.update(metadata)
                except ImportError:
                    pass
                except AttributeError:
                    pass

            transmission_metadata = {}

            if self.transmission_metadata is not None and self.transmission_metadata.strip() != '':
                transmission_metadata = json.loads(self.transmission_metadata)

            if processed:
                transmission_metadata.update(processed_metadata)
            else:
                client = Client(settings.SIMPLE_MESSAGING_TWILIO_CLIENT_ID, settings.SIMPLE_MESSAGING_TWILIO_AUTH_TOKEN)

                twilio_message = None

                if self.message.startswith('image:'):
                    twilio_message = client.messages.create(to=self.current_destination(), from_=settings.SIMPLE_MESSAGING_TWILIO_PHONE_NUMBER, media_url=[self.message[6:]]) # pylint: disable=unsubscriptable-object

                    time.sleep(10)
                else:
                    twilio_message = client.messages.create(to=self.current_destination(), from_=settings.SIMPLE_MESSAGING_TWILIO_PHONE_NUMBER, body=self.fetch_message(transmission_metadata))

                transmission_metadata['twilio_sid'] = twilio_message.sid

            self.sent_date = timezone.now()

            self.transmission_metadata = json.dumps(transmission_metadata, indent=2)

            self.errored = False
            self.save()

        except: # pylint: disable=bare-except
            self.errored = True

            transmission_metadata = {}

            if self.transmission_metadata is not None and self.transmission_metadata.strip() != '':
                transmission_metadata = json.loads(self.transmission_metadata)

            transmission_metadata['error'] = traceback.format_exc().splitlines()

            self.transmission_metadata = json.dumps(transmission_metadata, indent=2)

            self.save()

class IncomingMessage(models.Model):
    sender = models.CharField(max_length=256)
    recipient = models.CharField(max_length=256)

    receive_date = models.DateTimeField()

    message = models.TextField(max_length=1024)

    transmission_metadata = models.TextField(blank=True, null=True)

    def current_sender(self):
        if self.sender is not None and self.sender.startswith('secret:'):
            return decrypt_value(self.sender)

        return self.sender

    def update_sender(self, new_sender, force=False):
        if force is False and new_sender == self.current_sender():
            return # Same as current - don't add

        if hasattr(settings, 'SIMPLE_MESSAGING_SECRET_KEY'):
            encrypted_sender = encrypt_value(new_sender)

            self.sender = encrypted_sender
        else:
            self.sender = new_sender

        self.save()

    def encrypt_sender(self):
        if self.sender.startswith('secret:') is False:
            self.update_sender(self.sender, force=True)

class IncomingMessageMedia(models.Model):
    message = models.ForeignKey(IncomingMessage, related_name='media', on_delete=models.CASCADE)

    index = models.IntegerField(default=0)

    content_file = models.FileField(upload_to='incoming_message_media', null=True, blank=True)
    content_url = models.CharField(max_length=1024, null=True, blank=True)
    content_type = models.CharField(max_length=128, default='application/octet-stream')
