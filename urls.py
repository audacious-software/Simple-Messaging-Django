from django.conf.urls import url

from .views import incoming_message_request, simple_messaging_ui, simple_messaging_messages_json, \
                   simple_messaging_send_json

urlpatterns = [
    url(r'^incoming$', incoming_message_request, name='incoming_message'),
    url(r'^incoming.xml$', incoming_message_request, name='incoming_message_xml'),
    url(r'^console$', simple_messaging_ui, name='simple_messaging_ui'),
    url(r'^messages.json$', simple_messaging_messages_json, name='simple_messaging_messages_json'),
    url(r'^send.json$', simple_messaging_send_json, name='simple_messaging_send_json'),
]
