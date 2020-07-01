from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import serializers
from accounts.models import Company, User
from chat.models import *
import logging

logger = logging.getLogger('accounts')


class BlockUserSerializer(serializers.Serializer):
    block_user = serializers.CharField(error_messages={'required': 'block_user key is required', 'blank': 'block_user is required'})


class GetUserListChatSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    def get_id(self, instance):
        return instance.user.id

    def get_profile_image(self, instance):
        print(dir(instance.picture))
        return instance.picture.url if instance.picture else ''

    def get_username(self, instance):
        return instance.user.username

    def get_company_name(self, instance):
        return instance.name

    class Meta:
        model = Company
        fields = [
            'id',
            'company_name',
            'profile_image',
            'username'
        ]


class GetUploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFileChat
        fields = '__all__'