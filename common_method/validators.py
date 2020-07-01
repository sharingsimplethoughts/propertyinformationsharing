from django.apps import apps
from rest_framework.fields import empty
from rest_framework.serializers import (
    Serializer,
    BooleanField,
)
from rest_framework import pagination
from pyfcm import FCMNotification
import json
import requests
from notifications.models import NotificationsDetail, AdminNotifications
from common_method.celery_tasks import send_new_notification_shared
from PropInfoShare.signals import new_notification, admin_notification
from posts.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

fcm_server_key = 'fcm_server_key'

from rest_framework_jwt.settings import api_settings
from accounts.models import JWTTokenRecords

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from push_notifications.models import GCMDevice

@receiver(new_notification)
def send_new_message_notification(sender, **kwargs):
    if 'user_id' in kwargs['context']:
        notification_for_users = User.objects.filter(id__in=kwargs['context']['user_id'])
    else:
        notification_for_users = User.objects.all().exclude(id__in=kwargs['context']['exclude_user_id'])
    notification_by_user = User.objects.get(id=kwargs['sent_user_id'])
    bulk_notification = NotificationsDetail.objects.bulk_create([NotificationsDetail(
        notification_by=notification_by_user, notification_for=x,
        notification_sender_model_name=kwargs['sender_model_name'],
        notification_type=kwargs['context']['notification_type'],
        notification_context=kwargs['context']) for x in notification_for_users])
    new_kwargs = {}
    for key in kwargs:
        if key not in ('signal',):
            new_kwargs[key] = kwargs[key]
    new_kwargs['sender_pk'] = sender.pk
    send_new_notification_shared.delay(**new_kwargs)


@receiver(admin_notification)
def generate_admin_notification(sender, **kwargs):
    sender_model_name = kwargs['sender_model_name']
    sender_pk = sender.pk
    AdminNotifications.objects.create(notification_by=kwargs['notification_by'],
                                      notification_type=kwargs['notification_type'],
                                      notification_context=kwargs['context'],
                                      sender_model_name=sender_model_name, sender_pk=sender_pk)


def get_error(serializer):
    error_keys = list(serializer.errors.keys())
    if error_keys:
        error_msg = serializer.errors[error_keys[0]]
        return error_msg[0]
    return serializer.errors


class CustomBooleanField(BooleanField):
    def get_value(self, dictionary):
        return dictionary.get(self.field_name, empty)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


def get_token(instance):
    payload = jwt_payload_handler(instance)
    token = jwt_encode_handler(payload)
    token = 'JWT ' + token
    JWTTokenRecords.objects.get_or_create(user=instance, token=token)
    return token


def save_JWT_token(token, user):
    JWTTokenRecords.objects.get_or_create(user=user, token=token)
