from django.conf.urls import url

from .views import incoming_message_request

urlpatterns = [
    url(r'^incoming$', incoming_message_request, name='incoming_message'),
]
