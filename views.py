# pylint: disable=no-member, line-too-long

import importlib

from django.conf import settings
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def incoming_message_request(request):
    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            return response_module.process_incoming_request(request)
        except ImportError:
            pass
        except AttributeError:
            pass

    raise Http404("No module found to process incoming message.")
