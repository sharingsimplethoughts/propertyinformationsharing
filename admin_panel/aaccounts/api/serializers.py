from rest_framework import serializers


class UpdateTermsAndConditionsSerializer(serializers.Serializer):
    title = serializers.CharField(error_messages={'required': 'title key is required', 'blank': 'title is required'})
    content = serializers.CharField(
        error_messages={'required': 'content key is required', 'blank': 'content is required'})


class UpdatePrivacyPolicySerializer(serializers.Serializer):
    title = serializers.CharField(error_messages={'required': 'title key is required', 'blank': 'title is required'})
    content = serializers.CharField(
        error_messages={'required': 'content key is required', 'blank': 'content is required'})


class UpdateFAQSerializer(serializers.Serializer):
    question = serializers.CharField(error_messages={'required': 'question key is required', 'blank': 'question is required'})
    answer = serializers.CharField(error_messages={'required': 'answer key is required', 'blank': 'answer is required'})


class UpdateAboutUsSerializer(serializers.Serializer):
    key = serializers.CharField(error_messages={'required': 'key key is required', 'blank': 'key is required'})
    content = serializers.CharField(error_messages={'required': 'content key is required', 'blank': 'content is required'})
