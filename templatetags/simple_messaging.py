import json

from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def simple_messaging_broadcast():
    return render_to_string('dashboard/dashboard_messages_broadcast.html')
