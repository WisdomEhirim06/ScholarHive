# utils.py

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import Scholarship

# TO check the authentication of a user type
def check_auth(user_type):
    """
    Decorator to check if user is authenticated and has correct user type.
    Maintains existing session-based authentication logic.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.session.get('is_authenticated', False) or request.session.get('user_type') != user_type:
                return Response({
                    'error': f'Unauthorized. Only {user_type}s can access this endpoint.'
                }, status=status.HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


