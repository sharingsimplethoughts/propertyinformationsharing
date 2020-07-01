from django.urls import path

from .views import *

app_name='chat-api'

urlpatterns=[
    path('get_users_list', GetUsersListView.as_view(), name='get_users_list'),
    path('block_user', BlockUserView.as_view(), name='block_user'),
    path('upload_get_file', UploadGetFileView.as_view(), name='upload_get_file'),
]
