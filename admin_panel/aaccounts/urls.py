from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import *

app_name = 'ap_accounts'

urlpatterns=[
    path('home/',AdminHomeView.as_view(),name='ahome'),
    path('login/',AdminLoginView.as_view(),name='alogin'),
    path('logout/',AdminLogoutView.as_view(),name='alogout'),

    # password reset by mail
    url(r'^password_reset/$', ResetPasswordView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView, name='password_reset_complete'),

    path('profile/',AdminProfileView.as_view(),name='aprofile'),
    path('profile/edit',AdminProfileEditView.as_view(),name='aprofile_edit'),
    path('change_password/',ChangePasswordView.as_view(),name='a_change_password'),

   # tag_management
    path('tag_management', TagManagementView.as_view(), name='tag_management'),

    #report management
    path('report_management', ReportListView.as_view(), name='report_management'),
    path('report_detail/<str:post_id>/<str:post_type>', ReportDetailView.as_view(), name='report_detail'),

    #flag management
    path('flag_management', FlagListView.as_view(), name='flag_management'),
    path('flag_detail/<str:post_id>/<str:post_type>', FlagDetailView.as_view(), name='flag_detail'),

    #post management
    path('post_management', PostListView.as_view(), name='post_management'),
    path('post_detail/<str:post_id>', PostDetailView.as_view(), name='post_detail'),

    # usermanagement

    path('user_management', UserManagementView.as_view(), name='user_management'),
    path('payment_management', PaymentManagementView.as_view(), name='payment_management'),

]
