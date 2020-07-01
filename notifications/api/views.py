from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from common_method.validators import get_error, send_new_message_notification
import logging

logger = logging.getLogger('accounts')
from accounts.middleware import ValidateJWTToken
from notifications.models import *


class GetNotificationListByUserView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request, *args, **kwargs):
        serializer = GetNotificationListByUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            try:
                user = User.objects.get(id=data['notification_by_user'])
            except:
                raise APIException({'message': 'User doesnot exists'})
            notification_by_user = NotificationsDetail.objects.filter(notification_by=user).order_by('-created_at')[:30]
            return Response({
                'message': 'Data Retrieved successfully',
                'success': 'True',
                'data': NotificationsDetailSerializer(notification_by_user, many=True).data
            }, status=200, )


class GetNotificationListForUserView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request, *args, **kwargs):
        serializer = GetNotificationListForUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            try:
                user = User.objects.get(id=data['notification_for_user'])
            except:
                raise APIException({'message': 'User doesnot exists'})
            notification_for_user = NotificationsDetail.objects.filter(notification_for=user).order_by('-created_at')[
                                    :30]
            return Response({
                'message': 'Data Retrieved successfully',
                'success': 'True',
                'data': NotificationsDetailSerializer(notification_for_user, many=True).data
            }, status=200)


class GenerateChatNotificationView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        if 'user_id' in data and len(data['user_id']) != 0:
            context = {
                'user_id': data['user_id'],
                'notification_type': '7',
                'title': 'New Chat Message',
                'body': 'You got a new message from ' + request.user.username
            }
            send_new_message_notification(sender=request.user, context=context,
                                          sender_model_name="accounts.{}".format(request.user.__class__.__name__),
                                          sent_user_id=request.user.id)
            return Response({
                'message': 'Notification Sent Successfully',
                'success': 'True'
            }, status=200, )
        raise APIException({'message': 'Please provide valid user id'})


class GenerateAdminNotification(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id, is_active=True, is_staff=True, is_superuser=True)
        except:
            return Response({
                'message': 'Only admin can access this API',
                'success': 'False'
            }, status=401, )
        notifications_list = AdminNotifications.objects.all().order_by('-created_on')[:15]
        return Response({
            'message': 'Data retrieved successfully',
            'success': 'True',
            'data': AdminNotificationSerializer(notifications_list, many=True).data
        })
