import re

from django import http
from django.utils.deprecation import MiddlewareMixin


ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Allow-Headers'
ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'
ACCESS_CONTROL_MAX_AGE = 'Access-Control-Max-Age'

CORS_URLS_REGEX =  r'^/api/.*$'
CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken',
)
CORS_ALLOW_METHODS = (
        'GET',
        'OPTIONS',
)


class CorsMiddleware(MiddlewareMixin):
    '''
    This is a simplified version of the middleware in django-cors-header, https://github.com/ottoyiu/django-cors-headers/
    '''

    def process_request(self, request):
        '''
        If CORS preflight header, then create an empty body response (200 OK) and return it

        Django won't bother calling any other request view/exception middleware along with
        the requested view; it will call any response middlewares
        '''
        if (self.is_enabled(request) and
            request.method == 'OPTIONS' and
            'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META):
            response = http.HttpResponse()
            return response
        return None

    def process_response(self, request, response):
        '''
        Add the respective CORS headers
        '''

        if self.is_enabled(request):
            response[ACCESS_CONTROL_ALLOW_ORIGIN] = "*"

        if request.method == 'OPTIONS':
                response[ACCESS_CONTROL_ALLOW_HEADERS] = ', '.join(CORS_ALLOW_HEADERS)
                response[ACCESS_CONTROL_ALLOW_METHODS] = ', '.join(CORS_ALLOW_METHODS)

        return response


    def is_enabled(self, request):
            return re.match(CORS_URLS_REGEX, request.path_info)
