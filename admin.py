# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib import admin

from .models import OutgoingMessage, IncomingMessage, IncomingMessageMedia

def reset_resend_messages(modeladmin, request, queryset): # pylint: disable=unused-argument
    for message in queryset:
        metadata = json.loads(message.transmission_metadata)

        if 'error' in metadata:
            del metadata['error']

        if 'twilio_sid' in metadata:
            del metadata['twilio_sid']

        message.transmission_metadata = json.dumps(metadata, indent=2)

        message.errored = False
        message.sent_date = None

        message.save()

reset_resend_messages.short_description = "Reset and resend selected messages"

@admin.register(OutgoingMessage)
class OutgoingMessageAdmin(admin.ModelAdmin):
    if hasattr(settings, 'SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES') and settings.SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES:
        list_display = ('current_destination', 'reference_id', 'send_date', 'sent_date', 'message', 'errored')
    else:
        list_display = ('destination', 'reference_id', 'send_date', 'sent_date', 'message', 'errored')

    search_fields = ('destination', 'message', 'transmission_metadata',)
    list_filter = ('errored', 'send_date', 'sent_date',)
    actions = [reset_resend_messages]

@admin.register(IncomingMessage)
class IncomingMessageAdmin(admin.ModelAdmin):
    if hasattr(settings, 'SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES') and settings.SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES:
        list_display = ('current_sender', 'recipient', 'receive_date', 'message')
    else:
        list_display = ('sender', 'recipient', 'receive_date', 'message')

    search_fields = ('sender', 'message',)
    list_filter = ('receive_date',)

@admin.register(IncomingMessageMedia)
class Admin(admin.ModelAdmin):
    list_display = ('message', 'index', 'content_url', 'content_type')
    search_fields = ('content_url', 'content_type',)
    list_filter = ('content_type',)
