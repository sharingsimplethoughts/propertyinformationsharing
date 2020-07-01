from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from rest_framework import serializers
from rest_framework.exceptions import APIException
from notifications.models import *


class GetNotificationListByUserSerializer(serializers.Serializer):
    notification_by_user = serializers.CharField(
        error_messages={'required': 'notification_by_user key is required',
                        'blank': 'notification_by_user is required'})


class GetNotificationListForUserSerializer(serializers.Serializer):
    notification_for_user = serializers.CharField(
        error_messages={'required': 'notification_for_user key is required',
                        'blank': 'notification_for_user is required'})


class NotificationsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationsDetail
        fields = '__all__'


class AdminNotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, instance):
        return instance.get_created_time()

    class Meta:
        model = AdminNotifications
        fields = ['id', 'notification_type', 'notification_context', 'sender_model_name', 'sender_pk', 'read',
                  'created_at']
