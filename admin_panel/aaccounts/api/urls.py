from django.urls import path
from .views import *

app_name = 'ap_accounts'

urlpatterns=[

    path('delete_tag/<str:id>', DeleteTagAPIView.as_view() ,name='delete_tag'),
    path('add_edit_tag', AddTagAPIView.as_view(), name='add_edit_tag'),
    path('block_post/<str:post_id>/<str:post_type>/<str:post_status>', BlockPostAPIView.as_view(), name='block_post'),
    path('post_detail/<str:post_id>', PostDetailAPIView.as_view(), name='post_post'),
    path('block_user/<str:user_id>', BlockUserAPIView.as_view(), name='user_block'),
    path('update_t&c', UpdateTermsAndConditions.as_view(), name='update_t&c'),

]
