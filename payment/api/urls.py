from django.urls import path
from .views import *

app_name = 'payments'

urlpatterns = [
    path('make_payment', Make_Payment.as_view(), name='charge'),
    path('sign_up_payment', make_payment, name='sign_up_charge'),
    path('get_all_cards', ListOfSavedCard.as_view(), name='get_cards'),
    path('add_new_card', SaveNewCardAPIView.as_view(), name='add_card'),
]