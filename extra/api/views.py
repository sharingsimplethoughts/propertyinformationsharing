from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

from common_method.validators import get_error
from extra.models import *

class GetTermsAndConditionsAPIView(APIView):
    def get(self, request):
        return Response({
            'message':'Data Retrieved Successfully',
            'data':TermsAndConditionSerializer(TermsAndCondition.objects.all(), many=True).data
        }, status=200, )

class GetAboutUS(APIView):
    def get(selfself, request):
        return Response({
            'message':'Data Retrieved Successfully',
            'success':'True',
            'data': AboutUsSerializer(AboutUS.objects.all(), many=True).data
        })


class GetFAQAPIView(APIView):
    def get(self, request):
        return Response({
            'message':'Data Retrieved Successfully',
            'data':FAQSerializer(Faq.objects.all(), many=True).data
        }, status=200, )


class GetPrivacyPolicy(APIView):
    def get(self, request):
        return Response({
            'message':'Data Retrieved Successfully',
            'data':PrivacyPolicySerializer(PrivacyPolicy.objects.all(), many=True).data
        }, status=200, )