import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        token = data.get('token', None)

        if token is not None and isinstance(token, dict):
            data['token'] = {
                "access": token["access"],
                "refresh": token["refresh"]
            }

        return json.dumps(data)
