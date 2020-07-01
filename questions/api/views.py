from django.db.models import Q

from PropInfoShare.signals import new_notification
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
User = get_user_model()

from django.db.models import F,Q
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from common_method.validators import get_error
from accounts.models import *
from posts.models import *
import logging
logger = logging.getLogger('accounts')
from accounts.middleware import ValidateJWTToken


class CreateQuestionView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self,request,*args,**kwargs):
        logger.debug('Create question list post called')
        logger.debug(request.data)
        serializer=CreateQuestionSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            question_instance = serializer.save()
            question_obj = Question.objects.get(id=question_instance['id'])
            context = {
                'notification_type': '5',
                'title': 'New Question',
                'body': request.user.username + ' posted a new question near you',
                'id': question_instance['id'],
                'lat': question_instance['lat'],
                'lon': question_instance['lon'],
                'exclude_user_id': [request.user.id, ]
            }
            new_notification.send(sender=question_obj, context=context, sender_model_name="questions.{}".format(question_obj.__class__.__name__), sent_user_id=request.user.pk)
            return Response({
                'message':'Question submitted successfully',
                'success':'True',
                'data':serializer.data,
            },status=200)
        return Response({
            'message':'Question submition failed',
            'success':'False',
            'data':serializer.errors,
        },status=400)


class LikePostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        serilizer = LikePostSerilizer(data=data)

        if serilizer.is_valid():
            try:
                question = Question.objects.get(id=serilizer.validated_data['question_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid question_id'})
            else:
                if not serilizer.validated_data['is_liked']:
                    try:
                        question_likes = QuestionLikes.objects.get(question_id=question, liked_by=request.user)
                        question_likes.delete()

                        question.total_likes = F('total_likes') - 1
                        question.save()

                        return Response({
                            'message':'Like Removed successfully',
                        }, 200)
                    except:
                        raise serializers.ValidationError({'message': 'first like this post'})

                obj, created = QuestionLikes.objects.get_or_create(question_id = question, liked_by=request.user)

                if created:
                    question.total_likes = F('total_likes')+1
                    question.save()

                return Response({
                    'message': 'Liked successfully',
                }, 200)
        return Response({
            'message': get_error(serilizer)
        }, 400)


class CommentOnPostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer =CommentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                question = Question.objects.get(id=request.data['question_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid question id'})

            serializer.save(comment_by=request.user, question_id=question)
            question.total_comments = F('total_comments')+1
            question.save()
            return Response({
                'message':'Commented successfully'
            }, 200)
        return Response({
            'message':get_error(serializer)
        }, 400)


class LikeACommentPostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = LikeCommentSerilizer(data=request.data)

        if serializer.is_valid():
            try:
                comment = QuestionComments.objects.get(id=serializer.validated_data['comment_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid comment_id'})
            else:
                if not serializer.validated_data['is_liked']:
                    try:
                        comment_likes = QuestionCommentLike.objects.get(comment_id=comment, liked_by=request.user)
                        comment_likes.delete()
                        comment.total_like = F('total_like') - 1
                        comment.save()

                        return Response({
                            'message':'Like Removed successfully',
                        }, 200)
                    except:
                        raise serializers.ValidationError({'message': 'first like this post'})

                obj, created = QuestionCommentLike.objects.get_or_create(comment_id = comment, liked_by=request.user)

                if created:
                    comment.total_like = F('total_like')+1
                    comment.save()

                return Response({
                    'message': 'Liked successfully',
                }, 200)

        return Response({
            'message': get_error(serializer)
        }, 400)


class ReportAPostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = ReportACommentSerilizer(data=request.data)
        if serializer.is_valid():
            try:
                reason = ReportReasons.objects.get(id=request.data['reason_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid reason id'})

            try:
                question = Question.objects.get(id=serializer.validated_data['question_id'], is_active=True)
            except:
                raise serializers.ValidationError({'message': 'Invalid question id'})
            else:
                obj, created = QuestionReport.objects.get_or_create(question=question, user=request.user)
                if created:
                    question.total_reported = F('total_reported') + 1
                    question.save()

                obj.reason = reason
                obj.save()
                return Response({
                    'message': 'reported successfully'
                }, 200)

        raise serializers.ValidationError({'message': get_error(serializer)})


class QuestionView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, *args , **kwargs):
        question_id = self.kwargs.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except:
            raise serializers.ValidationError({'message':'Invalid question id'})

        data = QuestionViewSerializer(question, context={'request':request}).data
        return Response({
            'data':data
        }, 200)

