from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from rest_framework import serializers
from rest_framework.exceptions import APIException
from questions.models import *
from posts.api.serializers import UserPostDetailSerializer


class CreateQuestionSerializer(serializers.ModelSerializer):
    nickname=serializers.CharField(allow_blank=True,allow_null=True)
    picture=serializers.ImageField(required=False)
    question_text=serializers.CharField(allow_blank=True, allow_null=True)
    lat=serializers.CharField(allow_blank=True,allow_null=True)
    lon=serializers.CharField(allow_blank=True,allow_null=True)

    class Meta:
        model=Question
        fields=('nickname','picture','question_text','lat','lon')

    def validate(self,data):
        lat=data['lat']
        lon=data['lon']
        question_text=data['question_text']


        if not question_text or question_text=="":
            raise APIException({
                'message':'Please provide question text',
                'success':'False',
            })
        if not lat or lat=="":
            raise APIException({
                'message':'Please provide lat',
                'success':'False',
            })
        if not lon or lon=="":
            raise APIException({
                'message':'Please provide lon',
                'success':'False',
            })
        return data

    def create(self, validated_data):
        nickname=validated_data['nickname']
        lat=validated_data['lat']
        lon=validated_data['lon']
        question_text=validated_data['question_text']
        picture=self.context['request'].FILES.get('picture')
        if not picture:
            raise APIException({
                'message': 'Please provide image',
                'success': 'False',
            })
        u =self.context.get('request').user
        if not u:
            raise APIException({
                'message':'Please continue as a guest or create your profile',
                'success':'False',
            })
        q = Question(
            nickname=nickname,
            lat=lat,
            lon=lon,
            picture=picture,
            question_text=question_text,
            guest=u,
        )
        q.save()
        validated_data['id'] = q.pk
        return validated_data


class LikePostSerilizer(serializers.Serializer):
    question_id = serializers.CharField(error_messages={'required': 'question_id key is required', 'blank': 'question_id is required'})
    is_liked = serializers.BooleanField(error_messages={'required': 'is_liked key is required', 'blank': 'is_liked is required'})


class CommentSerializer(serializers.ModelSerializer):
    question_id = serializers.CharField(error_messages={'required': 'question_id key is required', 'blank': 'question_id is required'})
    content = serializers.CharField(error_messages={'required': 'content key is required', 'blank': 'content is required'})

    class Meta:
        model = QuestionComments
        fields = [
            'question_id',
            'content',
        ]


class LikeCommentSerilizer(serializers.Serializer):
    comment_id = serializers.CharField(error_messages={'required': 'comment_id key is required', 'blank': 'comment_id is required'})
    is_liked = serializers.BooleanField(error_messages={'required': 'is_liked key is required', 'blank': 'is_liked is required'})


class ReportACommentSerilizer(serializers.Serializer):
    question_id= serializers.CharField(error_messages={'required': 'question_id key is required', 'blank': 'question_id is required'})
    reason_id = serializers.CharField(error_messages={'required': 'reason_id key is required', 'blank': 'reason_id is required'})


class QuestionCommentsSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comment_by = UserPostDetailSerializer()

    def get_is_liked(self, instance):
        qs = QuestionCommentLike.objects.filter(comment_id=instance)
        if qs.exists():
            return True
        return False

    def get_created(self, instance):
        return instance.get_created_time()

    class Meta:
        model = QuestionComments
        fields = [
            'id',
            'comment_by',
            'content',
            'total_like',
            'created',
            'is_liked'
        ]

class QuestionViewSerializer(serializers.ModelSerializer):
    is_reported = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()
    comments =serializers.SerializerMethodField()
    report_reasons = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        try:
            self.user = self.context['request'].user
        except KeyError:
            self.user = None

    def get_report_reasons(self, instance):
        return ReportReasons.objects.all().values('id', 'reason')


    def get_created_on(self, instance):
        return instance.get_created_time()

    def get_is_reported(self, instance):
        qs = QuestionReport.objects.filter(question_id = instance, user=self.context.get('request').user)
        if qs.exists():
            return True
        return False

    def get_is_liked(self, instance):
        qs = QuestionLikes.objects.filter(question_id = instance, liked_by=self.context.get('request').user)
        if qs.exists():
            return True
        return False

    def get_comments(self, instance):
        qs = QuestionComments.objects.filter(question_id=instance).order_by('-created')
        data = QuestionCommentsSerializer(qs, many=True, context={'request': self.context.get('request')}).data
        return data

    class Meta:
        model = Question
        fields = [
            'id',
            'picture',
            'nickname',
            'question_text',
            'lat',
            'lon',
            'created_on',
            'total_comments',
            'total_likes',
            'total_reported',
            'total_shares',
            'is_reported',
            'is_liked',
            'comments',
            'report_reasons'
        ]