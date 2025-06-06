# pylint: disable=line-too-long, no-member

import base64
import json
import mimetypes
import posixpath

from urllib.parse import urlparse, urlsplit

import requests

from django.core.files.base import ContentFile

from simple_scheduling import SchedulingError # pylint: disable=import-error

from .models import OutgoingMessage, OutgoingMessageMedia

def execute_scheduled_item(task, when, context=dict): # pylint: disable=too-many-locals
    if task == 'simple_messaging.send_message':
        destination = context.get('destination', None)
        message = context.get('message', None)

        if None in (destination, message):
            raise SchedulingError('Please verify that "destination" and "mesage" are populated. If sending an empty message, set "message" to an empty string.')

        outgoing = OutgoingMessage.objects.create(destination=destination, message=message, send_date=when)

        transmission_metadata = context.get('transmission_metadata', {})

        channel = context.get('channel', None)

        if channel is not None:
            transmission_metadata['channel'] = channel

        outgoing.transmission_metadata = json.dumps(transmission_metadata, indent=2)

        metadata = context.get('metadata', {})

        outgoing.message_metadata = json.dumps(metadata, indent=2)

        outgoing.save()

        media_index = 0

        for media_item in context.get('media', []):
            outgoing_media = OutgoingMessageMedia.objects.create(message=outgoing, index=media_index)

            media_url = media_item.get('url', None)

            media_content = media_item.get('base64', None)
            media_type = media_item.get('type', 'application/octet-stream')
            filename =  media_item.get('filename', None)

            if media_url is not None:
                response = requests.get(media_url, timeout=300)

                outgoing_media.content_type = response.headers['content-type']

                outgoing_media.content_file.save()

                if filename is None:
                    url_path = urlsplit(media_url).path

                    filename = posixpath.basename(url_path)

                    extension = mimetypes.guess_extension(outgoing_media.content_type, strict=False)

                    if extension is None:
                        extension = 'bin'

                    if filename.lower().endswith(extension) is False:
                        filename = '%s.%s' % (filename, extension)

                outgoing_media.save(filename, ContentFile(response.raw.read()), save=True)
            elif (None in (media_content, media_type, filename)) is False: # Base64-encoded file.
                outgoing_media.content_type = media_type

                outgoing_media.save(filename, ContentFile(base64.b64decode(media_content)), save=True)
            else:
                outgoing_media.delete()
                outgoing.delete()

                raise SchedulingError('Please validate that your media objects are encoded correctly.')

            media_index += 1

        return True

    return False
