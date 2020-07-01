from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from accounts.middleware import ValidateJWTToken
from posts.models import Tags
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication

User = get_user_model()
from questions.models import Question
from posts.models import Post

from extra.models import *
from .serializers import *


class DeleteTagAPIView(APIView):
    """
    allow only for admin
    """

    def post(self, request, *args, **kwargs):

        try:
            Tags.objects.get(id=self.kwargs.get('id')).delete()
            return Response({
                'message': 'Post deleted successfully',
            }, 200)

        except:
            return Response({
                'message': 'Somthing went wrong'
            }, 500)


class AddTagAPIView(APIView):
    """
    tag create and edit
    """

    # permission_classes = [IsAuthenticated, ]
    # authentication_classes = [SessionAuthentication, ]

    def post(self, request):
        tag = request.data.get('tag')
        id = request.data.get('id')
        if id:
            tag_obj_new = Tags.objects.filter(tag=tag).exclude(id=id)
            if tag_obj_new.exists():
                return Response({
                    'message': 'This tag is already exist'
                }, 400)

            tag_obj = Tags.objects.get(id=id)
            tag_obj.tag = tag
            tag_obj.save()
            return Response({
                'message': 'Tag edited successfully'
            }, 200)

        obj, created = Tags.objects.get_or_create(tag=tag)
        if not created:
            return Response({
                'message': 'This tag is already exist'
            }, 400)

        user = User.objects.get(id=1)
        obj.created_by = user
        obj.save()
        return Response({
            'message': 'Tag created successfully'
        }, 200)


class BlockPostAPIView(APIView):
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        post_type = self.kwargs.get('post_type')
        post_status = self.kwargs.get('post_status')

        if post_type or post_id or post_status:

            if post_type == "1":
                Question.objects.filter(id=post_id).update(is_active=post_status)
            else:
                Post.objects.filter(id=post_id).update(is_active=post_status)

            if post_status == "True":
                msg = 'Unblocked successfully'
            else:
                msg = 'Blocked successfully'

            return Response({
                'message': msg
            }, 200)

        return Response({
            'message': 'Please provide all fields'
        }, 400)


class PostDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        data = Question.objects.values('nickname', 'picture', 'question_text',
                                       'lat', 'lon', 'total_comments',
                                       'total_likes', 'total_reported').get(id=self.kwargs.get('post_id'))

        return Response({

            'data': data
        }, 200)


class BlockUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            if user.is_active == True:
                user.is_active = False
                user.save()
                msg = 'Blocked successfully'
            else:
                user.is_active = True
                user.save()
                msg = 'Unblocked successfully'

        except:
            return Response({
                'message': 'Invalid user id'
            }, 400)

        return Response({
            'message': msg
        }, 200)


class UpdateTermsAndConditions(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request):
        if User.objects.get(id=request.user.id).is_superuser:
            serializer = UpdateTermsAndConditionsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                tc_obj, created = TermsAndCondition.objects.get_or_create(title=data['title'])
                tc_obj.content = data['content']
                tc_obj.save()
                return Response({
                    'message':'Terms And Conditions Updated Successfully',
                    'success':'True'
                }, status=200, )
            return Response({
                'message':'Something Went Wrong',
                'success':'False'
            }, status=400, )


class UpdatePrivacyPolicy(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request):
        if User.objects.get(id=request.user.id).is_superuser:
            serializer = UpdatePrivacyPolicySerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                privacy_policy_obj, created = PrivacyPolicy.objects.get_or_create(title=data['title'])
                privacy_policy_obj.content = data['content']
                privacy_policy_obj.save()
                return Response({
                    'message':'Terms And Conditions Updated Successfully',
                    'success':'True'
                }, status=200, )
            return Response({
                'message':'Something Went Wrong',
                'success':'False'
            }, status=400, )


class UpdateFAQ(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request):
        if User.objects.get(id=request.user.id).is_superuser:
            serializer = UpdateFAQSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                faq_obj, created = Faq.objects.get_or_create(question=data['question'])
                faq_obj.answer = data['answer']
                faq_obj.save()
                return Response({
                    'message':'Terms And Conditions Updated Successfully',
                    'success':'True'
                }, status=200, )
            return Response({
                'message':'Something Went Wrong',
                'success':'False'
            }, status=400, )


class UpdateAboutUs(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request):
        if User.objects.get(id=request.user.id).is_superuser:
            serializer = UpdateAboutUsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                about_us_obj, created = AboutUS.objects.get_or_create(key=data['key'])
                about_us_obj.content = data['content']
                about_us_obj.save()
                return Response({
                    'message':'Terms And Conditions Updated Successfully',
                    'success':'True'
                }, status=200, )
            return Response({
                'message':'Something Went Wrong',
                'success':'False'
            }, status=400, )