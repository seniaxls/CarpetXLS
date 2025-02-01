# orders/middleware.py
from user_agents import parse


class DeviceDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Parse the user agent string
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

        # Determine if it's a mobile device
        request.is_mobile = user_agent.is_mobile

        response = self.get_response(request)
        return response