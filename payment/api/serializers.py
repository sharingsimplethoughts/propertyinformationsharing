from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    Serializer,
    CharField,
    BooleanField

)

from payment.models import *

class PaymentSerializer(Serializer):
    is_card_save = BooleanField(error_messages={'required': 'is_card_save key is required', 'blank': 'is_card_save is required'})
    card_token = CharField(error_messages={'required': 'card_token key is required', 'blank': 'card_token is required'})


class ListOfSavedCardSerializer(ModelSerializer):
	class Meta:
		model 	= StripeCustomer
		fields 	= ['card','card_token','name','card_type','exp_month','exp_year']