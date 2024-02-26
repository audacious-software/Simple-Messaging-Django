# pylint: disable=line-too-long, no-name-in-module

import sys

from .views import incoming_message_request, simple_messaging_ui, simple_messaging_messages_json, \
                   simple_messaging_send_json, simple_messaging_lookup, simple_messaging_lookup_json

if sys.version_info[0] > 2:
    from django.urls import re_path

    urlpatterns = [
        re_path(r'^incoming$', incoming_message_request, name='incoming_message'),
        re_path(r'^incoming.xml$', incoming_message_request, name='incoming_message_xml'),
        re_path(r'^console$', simple_messaging_ui, name='simple_messaging_ui'),
        re_path(r'^messages.json$', simple_messaging_messages_json, name='simple_messaging_messages_json'),
        re_path(r'^send.json$', simple_messaging_send_json, name='simple_messaging_send_json'),
        re_path(r'^lookup$', simple_messaging_lookup, name='simple_messaging_lookup'),
        re_path(r'^lookup.json$', simple_messaging_lookup_json, name='simple_messaging_lookup_json'),
    ]
else:
    from django.conf.urls import url

    urlpatterns = [
        url(r'^incoming$', incoming_message_request, name='incoming_message'),
        url(r'^incoming.xml$', incoming_message_request, name='incoming_message_xml'),
        url(r'^console$', simple_messaging_ui, name='simple_messaging_ui'),
        url(r'^messages.json$', simple_messaging_messages_json, name='simple_messaging_messages_json'),
        url(r'^send.json$', simple_messaging_send_json, name='simple_messaging_send_json'),
        url(r'^lookup$', simple_messaging_lookup, name='simple_messaging_lookup'),
        url(r'^lookup.json$', simple_messaging_lookup_json, name='simple_messaging_lookup_json'),
    ]
