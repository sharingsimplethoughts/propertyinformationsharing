from django.urls import path
from .views import *

app_name='subscriptions-api'

urlpatterns=[
    path('payment_detail_page', PaymentDetailPageListView.as_view(),name='get_subscription_plan_list'),

]
