from rest_framework.views import (APIView,)
# from rest_framework.generics import (CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView,)
from rest_framework.permissions import (AllowAny,IsAuthenticated,)
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from django.db.models import Q
from datetime import datetime
from datetime import date
import string
import random
from accounts.middleware import ValidateJWTToken

from .serializers import *
from accounts.models import *
from subscriptions.models import *

import logging
logger = logging.getLogger('accounts')

class PaymentDetailPageListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request):
        user = request.user
        if user.profile_type=='2':
            comp_obj = Company.objects.get(user = user)
            subs_data = SubscriptionDetailSerializer(comp_obj.bussiness_area.subscription).data

            if comp_obj.is_more_than_5_account or comp_obj.bussiness_area.type=='Engineering Company':
                subs_data['account_type'] = 'Manufacturer'
                subs_data['users_or_account'] = 'Unlimited'
            else:
                subs_data['account_type'] = comp_obj.bussiness_area.type

            return Response({
                'data':subs_data
            }, 200)
        else:
            return Response({
                'message':'Individual type account is not required payment'
            },400)

