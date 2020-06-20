# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import OutgoingMessage, IncomingMessage, IncomingMessageMedia

@admin.register(OutgoingMessage)
class OutgoingMessageAdmin(admin.ModelAdmin):
    list_display = ('destination', 'reference_id', 'send_date', 'sent_date', 'message', 'errored')
    search_fields = ('destination', 'message', 'transmission_metadata',)
    list_filter = ('errored', 'send_date', 'sent_date',)

@admin.register(IncomingMessage)
class IncomingMessageAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'receive_date', 'message')
    search_fields = ('message', 'source',)
    list_filter = ('receive_date',)

@admin.register(IncomingMessageMedia)
class Admin(admin.ModelAdmin):
    list_display = ('message', 'index', 'content_url', 'content_type')
    search_fields = ('content_url', 'content_type',)
    list_filter = ('content_type',)
