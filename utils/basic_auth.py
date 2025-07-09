from django.http import HttpResponse
from functools import wraps
import base64
import os

def basic_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Basic'):
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')

            excepted_user = os.getenv('BASIC_AUTH_USER', 'admin')
            excepted_pass = os.getenv('BASIC_AUTH_PASS', 'pw')

            if username == excepted_user and excepted_pass:
                return view_func(request, *args, **kwargs)
        response = HttpResponse("Unauthorized", status=401)
        response['WWW-Authenticate']= "Basic realm='Protected'"
        return response
    return _wrapped_view