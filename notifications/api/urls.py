from django.urls import path

from .views import *

app_name='notification-api'

urlpatterns=[
    path('get_notification_list_by_user', GetNotificationListByUserView.as_view(), name='get_notification_list_by_user'),
    path('get_notification_list_for_user', GetNotificationListForUserView.as_view(), name='get_notification_list_for_user'),
    path('generate_chat_notification', GenerateChatNotificationView.as_view(), name='generate_chat_notification'),
    path('generate_admin_notification', GenerateAdminNotification.as_view(), name='generate_admin_notification'),
]
