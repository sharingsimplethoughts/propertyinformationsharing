
from rest_framework import permissions
from .models import JWTTokenRecords
from rest_framework.exceptions import APIException



class APIException401(APIException):
    status_code = 401


class ValidateJWTToken(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user:
            qs = JWTTokenRecords.objects.filter(user=user, token=request.META.get('HTTP_AUTHORIZATION'))
            if not qs.exists():
                raise APIException401({'detail': 'Invalid token'})
        return True


class DebuggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        print(request.POST, request.GET)
        return response

