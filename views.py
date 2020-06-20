# pylint: disable=no-member, line-too-long

import importlib
import json
import mimetypes

from io import BytesIO

import requests

from django.conf import settings
from django.core import files
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import IncomingMessage, IncomingMessageMedia

@csrf_exempt
def incoming_twilio(request): # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    response = '<?xml version="1.0" encoding="UTF-8" ?><Response>'

    responses = []

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            responses.extend(response_module.simple_messaging_response(request.POST))
        except ImportError:
            pass
        except AttributeError:
            pass

    for message in responses:
        response += '<Message>' + message + '</Message>'

    response += '</Response>'

    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        record_responses = True

        for app in settings.INSTALLED_APPS:
            try:
                response_module = importlib.import_module('.simple_messaging_api', package=app)

                record_responses = response_module.simple_messaging_record_response(request.POST)
            except ImportError:
                pass
            except AttributeError:
                pass

        if record_responses:
            now = timezone.now()

            destination = request.POST['To']

            incoming = IncomingMessage(recipient=destination)
            incoming.receive_date = now
            incoming.message = request.POST['Body'].strip()
            incoming.transmission_metadata = json.dumps(dict(request.POST), indent=2)

            incoming.save()

            num_media = 0

            media_objects = {}

            if 'NumMedia' in request.POST:
                num_media = int(request.POST['NumMedia'])

                for i in range(0, num_media):
                    media = IncomingMessageMedia(message=incoming)

                    media.content_url = request.POST['MediaUrl' + str(i)]
                    media.content_type = request.POST['MediaContentType' + str(i)]
                    media.index = i

                    media.save()

                    media_response = requests.get(media.content_url)

                    if media_response.status_code != requests.codes.ok:
                        continue

                    filename = media.content_url.split('/')[-1]

                    extension = mimetypes.guess_extension(media.content_type)

                    if extension is not None:
                        if extension == '.jpe':
                            extension = '.jpg'

                        filename += extension

                    file_bytes = BytesIO()
                    file_bytes.write(media_response.content)

                    media.content_file.save(filename, files.File(file_bytes))
                    media.save()

                    media_objects[filename] = {
                        'content': file_bytes.getvalue(),
                        'mime-type': media.content_type
                    }

    return HttpResponse(response, content_type='text/xml')
