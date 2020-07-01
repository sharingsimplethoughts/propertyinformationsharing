from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import logging

logger = logging.getLogger('accounts')
from accounts.middleware import ValidateJWTToken
from chat.models import *
from rest_framework.exceptions import APIException


class GetUsersListView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request):
        if request.user.profile_type != '4':
            excluded_user_list = list(BlockUserChat.objects.filter(blocked_by=request.user).values_list('user_id', flat=True))
            excluded_user_list.append(request.user.id)
            company_objs = Company.objects.select_related('user').exclude(user__id__in=excluded_user_list, user__is_active='True').order_by('name')
            if company_objs:
                data = GetUserListChatSerializer(company_objs, many=True).data
                return Response({
                    'message': 'Data Retrieved Successfully',
                    'success': 'True',
                    'data': data
                }, status=200, )
            return Response({
                'message': 'Data Retrieved successfully',
                'success': 'True',
                'data': 'No User exists'
            }, status=200, )
        return Response({
            'message': 'You can not chat as you are guest',
            'success': 'False'
        }, status=403, )


class BlockUserView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = BlockUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            if str(request.user.id) == data['block_user']:
                raise APIException({'You cannot block yourself'})
            try:
                user = User.objects.get(id=int(data['block_user']))
            except:
                raise APIException({'message': 'Invalid block_user id'})
            obj, created = BlockUserChat.objects.get_or_create(user_id=user, blocked_by=request.user)
            if not created:
                obj.delete()
                return Response({
                    'message': 'Unblocked User successfully',
                    'success': 'True',
                    'blocked': False
                }, status=200, )
            return Response({
                'message': 'User Blocked Successfully',
                'success': 'True',
                'blocked': True
            }, status=200, )


class UploadGetFileView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        if not request.FILES.get('file'):
            raise APIException({'message':'Please provide file to upload'})
        try:
            user = User.objects.get(id=request.user.id, is_active=True, profile_type='2')
        except Exception as e:
            logger.debug('exception occurred in file upload for chat {}'.format(str(e)))
            raise APIException({'message':'Something Went Wrong'})
        uploaded_file = UploadFileChat.objects.create(user=user, file=request.FILES.get('file'))
        return Response({
            'message':'Data retrieved successfully',
            'success':'True',
            'data':GetUploadedFileSerializer(uploaded_file).data
        })