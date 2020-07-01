from django.urls import path
from .views import *

app_name='extra-api'

urlpatterns=[
    path('t&c', GetTermsAndConditionsAPIView.as_view(), name='terms&conditions'),
    path('faq', GetFAQAPIView.as_view(), name='FAQ'),
    path('privacy_policy', GetPrivacyPolicy.as_view(), name='privacy_policy'),
    path('about_us', GetAboutUS.as_view(), name='about_us'),
]
