# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib import admin
from django.utils import timezone

from .models import OutgoingMessage, OutgoingMessageMedia, IncomingMessage, IncomingMessageMedia, BlockedSender

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

def mark_error_handled(modeladmin, request, queryset): # pylint: disable=unused-argument
    for message in queryset:
        metadata = {}

        try:
            metadata = json.loads(message.transmission_metadata)
        except ValueError:
            metadata = {}

        metadata['error_handled'] = timezone.now().isoformat()

        message.transmission_metadata = json.dumps(metadata, indent=2)

        message.save()

mark_error_handled.short_description = "Mark error handled"

class OutgoingMessageMediaInline(admin.TabularInline):
    model = OutgoingMessageMedia

    fields = ['content_file', 'content_type', 'index']
    readonly_fields = ['content_file', 'content_type', 'index']

    def has_add_permission(self, request, obj=None): # pylint: disable=arguments-differ,unused-argument
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(OutgoingMessage)
class OutgoingMessageAdmin(admin.ModelAdmin):
    if hasattr(settings, 'SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES') and settings.SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES:
        list_display = ('id', 'current_destination', 'reference_id', 'send_date', 'sent_date', 'current_message', 'errored')
    else:
        list_display = ('id', 'destination', 'reference_id', 'send_date', 'sent_date', 'message', 'errored')

    inlines = [
        OutgoingMessageMediaInline,
    ]

    search_fields = ('destination', 'message', 'transmission_metadata',)
    list_filter = ('errored', 'send_date', 'sent_date',)
    actions = [reset_resend_messages, mark_error_handled]

    def get_search_results(self, request, queryset, search_term):
        original_query_set = queryset

        queryset, may_have_duplicates = super(OutgoingMessageAdmin, self).get_search_results(request, queryset, search_term,) # pylint:disable=super-with-arguments

        if search_term is None or search_term == '':
            return queryset, may_have_duplicates

        for message in original_query_set:
            if search_term in message.current_destination():
                queryset = queryset | self.model.objects.filter(destination=message.destination)

        return queryset, may_have_duplicates

class IncomingMessageMediaInline(admin.TabularInline):
    model = IncomingMessageMedia

    fields = ['content_file', 'content_type', 'index']
    readonly_fields = ['content_file', 'content_type', 'index']

    def has_add_permission(self, request, obj=None): # pylint: disable=arguments-differ,unused-argument
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(IncomingMessage)
class IncomingMessageAdmin(admin.ModelAdmin):
    if hasattr(settings, 'SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES') and settings.SIMPLE_MESSAGING_SHOW_ENCRYPTED_VALUES:
        list_display = ('id', 'current_sender', 'recipient', 'receive_date', 'current_message')
    else:
        list_display = ('id', 'sender', 'recipient', 'receive_date', 'message')

    inlines = [
        IncomingMessageMediaInline,
    ]

    search_fields = ('sender', 'message',)
    list_filter = ('receive_date',)

    def get_search_results(self, request, queryset, search_term):
        original_query_set = queryset

        queryset, may_have_duplicates = super(IncomingMessageAdmin, self).get_search_results(request, queryset, search_term,) # pylint:disable=super-with-arguments

        if search_term is None or search_term == '':
            return queryset, may_have_duplicates

        for message in original_query_set:
            if search_term in message.current_sender():
                queryset = queryset | self.model.objects.filter(sender=message.sender)

        return queryset, may_have_duplicates

@admin.register(IncomingMessageMedia)
class IncomingMessageMediaAdmin(admin.ModelAdmin):
    list_display = ('message', 'index', 'content_url', 'content_type')
    search_fields = ('content_url', 'content_type',)
    list_filter = ('content_type',)

@admin.register(OutgoingMessageMedia)
class OutgoingMessageMediaAdmin(admin.ModelAdmin):
    list_display = ('message', 'index', 'content_type')
    search_fields = ('content_url', 'content_type',)
    list_filter = ('content_type',)

@admin.register(BlockedSender)
class BlockedSenderAdmin(admin.ModelAdmin):
    list_display = ('sender', 'blocked')
    search_fields = ('sender', 'notes',)
    list_filter = ('blocked',)
