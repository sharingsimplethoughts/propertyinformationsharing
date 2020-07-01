from django.urls import path
from .views import *

app_name='ap_settings_management'

urlpatterns=[
    path('settings/',SettingsManagementListView.as_view(),name='apsetm_set_list'),
    path('edit/<str:id>',SettingsManagementEditView.as_view(),name='apsetm_edit'),
    path('faq/edit/',SettingsManagementFaqEditView.as_view(),name='apsetm_faq_edit'),

    path('faq/',SettingsManagementFaqView.as_view(),name='apsetm_faq'),
    path('about_us/', SettingsManagementAboutUsView.as_view(), name='apsetm_about_us'),
    path('privacy_policy/',SettingsManagementPrivacyPolicyView.as_view(),name='apsetm_privacypolicy'),
    path('terms_and_condition/',SettingsManagementTermsAndConditionView.as_view(),name='apsetm_termsandcondition'),
]
