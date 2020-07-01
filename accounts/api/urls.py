from django.urls import path
from django.conf.urls import url
from .views import *

app_name = 'accounts-api'

urlpatterns = [

    path('country_code_list', CountryCodeListView.as_view(), name="country_code_list"),
    path('login', UserLoginAPIView.as_view(), name="login"),
    path('login_as_guest',LoginAsGuestView.as_view(),name='login_as_guest'),
    path('verify_otp',OTPVerifyView.as_view(),name='verify_otp'),
    path('bussiness_area_list',BussinessAreaListView.as_view(),name='bussiness_area_list'),
    path('profession_list',ProfessionListView.as_view(),name='profession_list'),
    #---------- edited
    # path('sign_up_form', )
    url(r'user_detail/(?P<username>[a-zA-Z0-9_]+)$', UserDetailView.as_view(),   name='user_detail'),
    path('invite', InviteUserAPIView.as_view(), name='invite_user'),
    path('follow_unfollow', FollowAUserAPIView.as_view(), name='follow_unfollow'),
    path('get_authorized_user', GetAuthourizedUserForInvite.as_view(), name='get_authorized_user'),
    path('report_user', ReportUserView.as_view(), name='report_user'),
    path('flag_user', FlagUserView.as_view(), name='flag_user'),
    path('like_other_profile', LikeOtherProfileAPIView.as_view(), name='like other profile'),
    path('edit_profile', UserEditProfileAPIView.as_view(), name='edit profile'),
    path('update_device_token', UpdateDeviceTokenAPIView.as_view(), name='update_device_token'),
    path('user_feedback', SendUserFeedbackView.as_view(), name='user_feedback'),
    path('user_list_for_owner', GetUserListForOwnerView.as_view(), name='owner_list'),
    #----------- end
    # path('user_detail',UserDetailView.as_view(),name='user_detail'), -------- removed
    path('registration', UserCreateAPIView.as_view(), name='registration'),
    path('password_reset', PasswordResetView.as_view(), name='rest_password_reset'),
    path('change_password', ChangePasswordAPIView.as_view(), name='change_password'),

    path('create_colleague_profile', CreateColleagueProfileAPIView.as_view(), name='create_colleague_profile'),
    path('delete_colleague_profile', DeleteColleagueProfileAPIView.as_view(), name='delete_colleague_profile'),
    path('view_colleagues_profile', ViewColleagueProfileAPIView.as_view(), name='view_colleagues_profile'),

    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('delete_account', DeleteAPIView.as_view(), name='delete'),

]
