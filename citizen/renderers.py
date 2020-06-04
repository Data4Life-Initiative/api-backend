import base64

from rest_framework import renderers


class PNGRenderer(renderers.BaseRenderer):
    """
    For rendering png image as response

    In this context, it is used to render QR code for citizen profile
    """
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        if 'image_base64' in data:
            return base64.b64decode(data['image_base64'].encode())

        self.media_type = 'application/json'
        self.format = 'json'
        self.charset = 'utf-8'
        self.render_style = 'text'

        return data
