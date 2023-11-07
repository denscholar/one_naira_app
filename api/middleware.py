from django.conf import settings

class SessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        session_id = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        if session_id:
            response["X-Session-Id"] = session_id

        return response