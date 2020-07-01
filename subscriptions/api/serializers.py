from rest_framework.serializers import ModelSerializer,SerializerMethodField
from rest_framework.exceptions import APIException

from datetime import datetime
# from dateutil.relativedelta import relativedelta
from subscriptions.models import *
from accounts.models import *


class SubscriptionDetailSerializer(ModelSerializer):
    users_or_account = SerializerMethodField()


    def get_users_or_account(self, instance):
        if instance.users_or_account:
            if int(instance.users_or_account) > 100:
                return "Unlimited"
        return instance.users_or_account

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'plan_name',
            'plan_desc',
            'price',
            'users_or_account',
            'comment_on_existing_posts',
            'create_posts',
            'mark_involvement_in_others_posts',
            'add_pictures_link_to_others_posts',
            'created_on',

        ]