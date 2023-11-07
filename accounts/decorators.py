from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def check_user_role(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                return Response(
                    data={"message": "Access denied"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return wrapper
    return decorator
