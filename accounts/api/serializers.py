from django.db.models import Q
from push_notifications.models import GCMDevice

from rest_framework.serializers import(
     ModelSerializer,
     EmailField,
     CharField,
     SerializerMethodField,
     BooleanField,
     NullBooleanField,
     Serializer,
     ChoiceField,
     ImageField
     )
from django.contrib.auth import get_user_model

from rest_framework_jwt.settings import api_settings
from accounts.models import *
#new
from payment.models import PaymentHistory
from posts.models import Post

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()

# reset password
from . password_reset_form_api import MyPasswordResetForm

from django.conf import settings
from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException
import os
from django.conf import settings

from django.db.models import Q,F
from ..models import *
import random

import logging
logger = logging.getLogger('accounts')

from common_method.validators import save_JWT_token
class APIException400(APIException):
    status_code = 400

class APIException403(APIException):
    status_code = 403

class CountryCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model=CountryCode
        fields=('__all__')


class UserLoginSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    email = serializers.CharField(allow_blank=True)
    password = serializers.CharField(allow_blank=True)
    social_id = serializers.CharField(allow_blank=True)
    account_type = serializers.CharField(allow_blank=True)
    device_type = serializers.CharField(allow_blank=True)
    device_token = serializers.CharField(allow_blank=True)
    profile_type = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model=User
        fields=('user_id','email','password','social_id','account_type','device_type','device_token','profile_type','token')

    def validate(self,data):
        email=data['email']
        password=data['password']
        account_type=data['account_type']
        device_type=data['device_type']
        device_token=data['device_token']
        # profile_type=data['profile_type']
        social_id=data['social_id']

        if social_id:
            soc = SocialAccounts.objects.filter(social_id=social_id).first()
            if not soc:
                raise APIException400({
                    'message':'Social id does not exists. Please register first',
                    'success':'False',
                })
        else:
            if not email or email=='':
                raise APIException400({
                    'message':'Username/Email is required',
                    'success':'False',
                })
            if not password or password=='':
                raise APIException400({
                    'message':'Password is required',
                    'success':'False',
                })

        if not account_type or account_type=='':
            raise APIException400({
                'message':'Account type is required',
                'success':'False',
            })
        if not device_type or device_type=='':
            raise APIException400({
                'message':'Device type is required',
                'success':'False',
            })
        if not device_token or device_token=='':
            raise APIException400({
                'message':'Device token is required',
                'success':'False',
            })
        # if not profile_type or profile_type=='':
        #   raise APIException400({
        #       'message':'Profile type is required',
        #       'success':'False',
        #   })
        if account_type not in ('1','2','3'):
            raise APIException400({
                'message':'Account type is not correct',
                'success':'False',
            })
        if device_type not in ('1','2'):
            raise APIException400({
                'message':'Device type is not correct',
                'success':'False',
            })
        # if profile_type not in ('1','2'):
        #   raise APIException400({
        #       'message':'Profile type is not correct',
        #       'success':'False',
        #   })

        return data
    def create(self,validated_data):
        email = validated_data['email']
        password = validated_data['password']
        social_id = validated_data['social_id']
        account_type=validated_data['account_type']
        device_type=validated_data['device_type']
        device_token=validated_data['device_token']
        # profile_type=validated_data['profile_type']

        if social_id:
            soc = SocialAccounts.objects.filter(social_id=social_id).first()
            user = soc.user_id
        else:
            user = User.objects.filter(Q(email=email)|Q(username=email)).first() #,profile_type=profile_type
        if user:
            if not social_id:
                if not user.check_password(password):
                    raise APIException400({
                        'message':'Invalid credentials',
                        'success':'False',
                    })
            if not user.is_active:
                raise APIException400({
                    'message':'Your account is blocked by admin',
                    'success':'False',
                })
        else:
            raise APIException403({
                'message':'User does not exists. Please register first',
                'success':'False',
            })
        logger.debug('inside serializer login')
        previous_token_device = GCMDevice.objects.filter(registration_id=device_token)
        if previous_token_device.exists():
            logger.debug('inside if login')
            # logger.debug('in if for device token', previous_token_device[0].registration_id)
            previous_token_device.update(registration_id='')
            # logger.debug( previous_token_device[0].registration_id)
            previous_token_user = User.objects.filter(device_token=device_token)
            # logger.debug('in if for device token', previous_token_user[0].device_token)
            previous_token_user.update(device_token='')
            # logger.debug(previous_token_user[0].device_token)
        user.device_type = device_type
        user.device_token = device_token
        user.save()
        gcm_device, created = GCMDevice.objects.get_or_create(user=user, cloud_message_type='FCM')
        gcm_device.registration_id = device_token
        gcm_device.save()
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        token = 'JWT '+token
        save_JWT_token(token,user)
        validated_data['token']=token
        validated_data['user_id']=user.id
        validated_data['profile_type']=user.profile_type

        return validated_data


class LoginAsGuestSerializer(serializers.Serializer):
    country_code=serializers.CharField(allow_blank=True)
    mobile_number=serializers.CharField(allow_blank=True)
    social_id=serializers.CharField(allow_blank=True)
    email=serializers.CharField(allow_blank=True)
    is_profile_created=serializers.CharField(read_only=True)
    # class Meta:
    #   model = User
    #   fields = ('country_code','mobile_number')
    def validate(self,data):
        country_code=data['country_code']
        mobile_number=data['mobile_number']
        social_id=data['social_id']
        email=data['email']
        if not country_code or country_code=='':
            raise APIException400({
                'message':'Country code is required',
                'success':'False'
            })
        if not mobile_number or mobile_number=='':
            raise APIException400({
                'message':'Mobile number is required',
                'success':'False'
            })
        return data


class OTPVerifySerializer(serializers.Serializer):
    country_code=serializers.CharField(allow_blank=True)
    mobile_number=serializers.CharField(allow_blank=True)
    verification_code=serializers.CharField(allow_blank=True)
    # class Meta:
    #   model = User
    #   fields = ('country_code','mobile_number','verification_code')
    def validate(self,data):
        country_code=data['country_code']
        mobile_number=data['mobile_number']
        verification_code=data['verification_code']
        if not country_code or country_code=='':
            raise APIException400({
                'message':'Country code is required',
                'success':'False'
            })
        if not mobile_number or mobile_number=='':
            raise APIException400({
                'message':'Mobile number is required',
                'success':'False'
            })
        if not verification_code or verification_code=='':
            raise APIException400({
                'message':'Verification code is required',
                'success':'False'
            })
        return data


class BussinessAreaListSerializer(serializers.ModelSerializer):
    class Meta:
        model=BussinessArea
        fields='__all__'
class ProfessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profession
        fields='__all__'


#--------- report reasons serializer
class ReportReasonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileReportReasons
        fields = ('id', 'reason', )
#----------- end


class UserDetailPersonalSerializer(ModelSerializer):
    profession = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    #------------ new fields
    mobile_number = serializers.SerializerMethodField()
    total_follow_to = serializers.SerializerMethodField()
    total_follow_by = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_projects = serializers.SerializerMethodField()
    followed_to = serializers.SerializerMethodField('user_followed_to')
    report_reasons = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    #----------- end
    class Meta:
        model = User
        #edit
        fields = ['id', 'username', 'name', 'email', 'mobile_number', 'country_code', 'is_mail_verify',
                  'is_num_verify', 'profile_image','profession','is_profile_created','is_social_active',
                  'is_verified','token','profile_type','total_follow_to','total_follow_by','social_links',
                  'total_likes','about','total_projects','followed_to', 'report_reasons', 'is_liked']
    def get_profession(self,instance):
        return instance.profession.type

    #----------- new functions
    def get_mobile_number(self, instance):
        if self.context.get('request').user.id == instance.id:
            return instance.mobile_number
        return None

    def get_total_follow_to(self, instance):
        print('in serializer', instance)
        return len(FollowersAndFollowing.objects.filter(followed_to=instance))

    def get_total_follow_by(self, instance):
        return len(FollowersAndFollowing.objects.filter(followed_by=instance))

    def get_social_links(self, instance):
        social_acounts = SocialLinks.objects.filter(user_id=instance)  
        my_social_accounts = {}
        for _ in social_acounts:
            my_social_accounts[_.account_type] = _.social_id
        return my_social_accounts

    def get_total_likes(self, instance):
        return len(ProfileLiked.objects.filter(user=instance))

    def get_total_projects(self, instance):
        return len(Post.objects.filter(created_by=instance))

    def user_followed_to(self, instance):
       return True if FollowersAndFollowing.objects.filter(followed_by=self.context['request'].user.id, followed_to=instance.id).exists() else False

    def get_report_reasons(self, instance):
        return ReportReasonsSerializer(ProfileReportReasons.objects.all(), many=True, context=self.context).data

    def get_is_liked(self, instance):
        return True if ProfileLiked.objects.filter(user=self.context.get('request').user, liked_by=instance) else False
    #---------- end 

    def get_token(self,instance):
        payload = jwt_payload_handler(instance)
        token = jwt_encode_handler(payload)
        token = 'JWT '+token
        return token


class CompanyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name','address_line1','address_line2','address_line3','description',
        'bussiness_area','year_of_foundation','picture']


class LoggedInSerializer(ModelSerializer):
    company_detail = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    business_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'business_type' ,'name', 'email', 'mobile_number', 'country_code', 'is_mail_verify',
                  'is_num_verify', 'profile_image','profession','is_profile_created','is_social_active',
                  'is_verified','token','profile_type','company_detail']
    
    def get_business_type(self, instance):
        if instance.profile_type == '3':
            company = instance.colleague_company_id
            return company.bussiness_area.subscription.id
        elif instance.profile_type == '2':
            company = Company.objects.filter(user=instance).first()
            return company.bussiness_area.subscription.id
        else:
            return 1

    def get_company_detail(self, instance):
        request=self.context['request']
        if instance.profile_type=='3':
            company = instance.colleague_company_id
        else:
            company = Company.objects.filter(user=instance).first()
        serializer = CompanyDetailSerializer(company,context={'request':request})
        return serializer.data

    def get_token(self,instance):
        payload = jwt_payload_handler(instance)
        token = jwt_encode_handler(payload)
        token = 'JWT '+token
        save_JWT_token(token, instance)

        return token


class UserDetailCompanySerializer(ModelSerializer):
    company_detail=serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    business_type = serializers.SerializerMethodField()
    #--------- new fields
    mobile_number = serializers.SerializerMethodField()
    total_follow_to = serializers.SerializerMethodField()
    total_follow_by = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_projects = serializers.SerializerMethodField()
    followed_to = serializers.SerializerMethodField('user_followed_to')
    report_reasons = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    #--------- end

    class Meta:
        model = User
        #edit
        fields = ['id', 'username', 'business_type','name', 'email', 'mobile_number', 'country_code', 'is_mail_verify',
                  'is_num_verify', 'profile_image','profession','is_profile_created','is_social_active',
                  'is_verified','token','profile_type','company_detail','total_follow_to','total_follow_by','social_links',
                  'total_likes','about','total_projects','followed_to', 'report_reasons', 'is_liked']

    def get_business_type(self, instance):
        if instance.profile_type == '3':
            company = instance.colleague_company_id
            return company.bussiness_area.subscription.id
        elif instance.profile_type == '2':
            company = Company.objects.filter(user=instance).first()
            return company.bussiness_area.subscription.id
        else:
            return 1

    #-------------- new functions
    def get_mobile_number(self, instance):
        if self.context.get('request').user.id == instance.id:
            return instance.mobile_number
        return None

    def get_total_follow_to(self, instance):
        return len(FollowersAndFollowing.objects.filter(followed_to=instance))

    def get_total_follow_by(self, instance):
        return len(FollowersAndFollowing.objects.filter(followed_by=instance))

    def get_social_links(self, instance):
        social_acounts = SocialLinks.objects.filter(user_id=instance)  
        my_social_accounts = {}
        for _ in social_acounts:
            my_social_accounts[_.account_type] = _.social_id
        return my_social_accounts

    def get_total_likes(self, instance):
        return len(ProfileLiked.objects.filter(user=instance))

    def get_total_projects(self, instance):
        return len(Post.objects.filter(created_by=instance, is_active=True))

    def user_followed_to(self, instance):
        return True if FollowersAndFollowing.objects.filter(followed_by=self.context['request'].user.id, followed_to=instance.id).exists() else False
    
    def get_report_reasons(self, instance):
        return ReportReasonsSerializer(ProfileReportReasons.objects.all(), many=True, context=self.context).data
    
    def get_is_liked(self, instance):
        return True if ProfileLiked.objects.filter(user=instance, liked_by=self.context.get('request').user).exists() else False
    #----------- end

    def get_company_detail(self, instance):
        request=self.context['request']
        if instance.profile_type=='3':
            company = instance.colleague_company_id
        else:
            company = Company.objects.filter(user=instance).first()
        serializer = CompanyDetailSerializer(company,context={'request':request})
        return serializer.data

    def get_token(self,instance):
        payload = jwt_payload_handler(instance)
        token = jwt_encode_handler(payload)
        token = 'JWT '+token
        save_JWT_token(token, instance)

        return token
    

#---------- invite user serializer
class InviteSerializer(serializers.Serializer):
    user_id = serializers.ListField(allow_empty=True, required=False, child=serializers.CharField(allow_blank=True))
    post_id = serializers.IntegerField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    email_id = serializers.ListField(allow_empty=True, required=False, child=serializers.EmailField(allow_blank=True))
#---------- end


#---------- user list serializer
class GetUserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        return instance.get_full_name()

    class Meta:
        model = User
        fields =[
            'id',
            'name',
            'username',
            'profile_image',
            'email'
        ]
#----------- end

#---------- feedback serializer
class FeedbackSerializer(serializers.Serializer):
    feedback = serializers.CharField(error_messages={'required': 'feedback key is required', 'blank': 'feedback is required'})
#---------- end


#-----------Update Device Token Serializer
class UpdateDeviceTokenSerializer(serializers.Serializer):
    old_token = serializers.CharField(error_messages={'required': 'old_token key is required', 'blank': 'old_token is required'})
    new_token = serializers.CharField(error_messages={'required': 'new_token key is required', 'blank': 'new_token is required'})
#--------- end


#------------ report user serializer
class ReportUserSerializer(serializers.Serializer):
    user_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    reason_id = serializers.CharField(error_messages={'required': 'reason_id key is required', 'blank': 'reason_id is required'})


#----------- flag user serializer
class FlagUserSerializer(serializers.Serializer):
    user_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    reason_id = serializers.CharField(error_messages={'required': 'reason_id key is required', 'blank': 'reason_id is required'})


import types
class UserCreateSerializer(Serializer):
    # first_name = CharField(allow_blank=True, error_messages={'required': 'first name key required'})
    # last_name = CharField(allow_blank=True, error_messages={'required': 'last name key required'})
    username = CharField(allow_blank=True, error_messages={'required': 'username key required'})
    name = CharField(allow_blank=True, error_messages={'required': 'name key required'})
    email = EmailField(allow_blank=True, error_messages={'required': 'email key required'})
    # country_code = CharField(error_messages={'required': 'country code key required'})
    # mobile_number = CharField(error_messages={'required': 'mobile number key required'})
    profession = CharField(allow_blank=True)
    profile_image = ImageField(required=False)
    password = CharField(error_messages={'required': 'password key required'})
    account_type = ChoiceField(choices=ACCOUNT_TYPE, error_messages={'required': 'account type key required', 'blank':'account type is required'})
    profile_type = CharField(allow_blank=True,)
    social_id = CharField(allow_blank=True, error_messages={'required': 'social id key required'})
    device_token = CharField(error_messages={'required': 'device_token key is required' ,'blank': 'device_token  is required'})
    device_type = ChoiceField(choices=ACCOUNT_TYPE, error_messages={'required': 'device_type key is required'})
    user_id = CharField(read_only=True)

    company_name = CharField(allow_blank=True, )
    lat= CharField(allow_blank=True, )
    lon = CharField(allow_blank=True, )
    address_line1 = CharField(allow_blank=True, )
    address_line2 = CharField(allow_blank=True, )
    address_line3 = CharField(allow_blank=True, )
    description = CharField(allow_blank=True, )
    bussiness_area = CharField(allow_blank=True, )
    is_more_than_5 = BooleanField()
    year_of_foundation = CharField(allow_blank=True, )


    def validate(self, data):
        print('---------hello------------')

        username = data['username']
        # country_code = data['country_code']
        # mobile_number = data['mobile_number']
        email = data['email']
        profession = data['profession']
        device_type = data['device_type']
        account_type = data['account_type']
        profile_type = data['profile_type']
        social_id = data['social_id']
        lat = data['lat']
        lon = data['lon']


        company_name = data['company_name']

        bussiness_area = data['bussiness_area']
        year_of_foundation = data['year_of_foundation']

        if username:
            user=User.objects.filter(username=username).first()
            if user:
                raise APIException400({
                    'message':'This username already taken',
                    'success':'Fasle'
                })
        
        if not profile_type or profile_type=="":
            raise APIException400({
                'message':'Profile type is required',
                'success':'False',
            })
        if profile_type not in ('1','2'):
            raise APIException400({
                'message':'Profile type is not valid',
                'success':'False',
            })
        if profile_type=='1':
            print('dfsf')
            if not profession or profession=='':
                raise APIException400({
                    'message':'Profession is required',
                    'success':'False',
                })
            if profession:
                profession = Profession.objects.filter(id=profession).first()
                if not profession:
                    raise APIException400({
                        'message':'Profession is incorrect',
                        'success':'False',
                    })
            # if not country_code or country_code=="":
            #     raise APIException400({
            #         'message': 'Please provide country code',
            #         'success':'False',
            #     })
            # if not mobile_number or mobile_number=="":
            #     raise APIException400({
            #         'message': 'Please provide mobile number',
            #         'success':'False',
            #     })
        if profile_type=='2':
            if not company_name or company_name=='':
                raise APIException400({
                    'message':'Company name is required',
                    'success':'False',
                })

            if not bussiness_area or bussiness_area=='':
                raise APIException400({
                    'message':'Bussiness area is required',
                    'success':'False',
                })
            if not year_of_foundation or year_of_foundation=='':
                raise APIException400({
                    'message':'Year of foundation is required',
                    'success':'False',
                })
            if not year_of_foundation.isdigit():
                raise APIException400({
                    'message': 'Please correct your year of foundation',
                    'success':'False',
                })
            if not bussiness_area.isdigit():
                raise APIException400({
                    'message': 'Please correct your bussiness area',
                    'success':'False',
                })
            if bussiness_area:
                bussiness_area=BussinessArea.objects.filter(id=bussiness_area).first()
                if not bussiness_area:
                    raise APIException400({
                        'message':'Bussiness area in incorrect',
                        'success':'False',
                    })
                if bussiness_area.type=='Manufacturer':
                    if not isinstance( data.get('is_more_than_5'),(bool)):
                        raise APIException400({
                            'message': 'is_more_than_5 option is required',
                            'success': 'False',
                        })

        if device_type not in ['1', '2']:
            raise APIException400({
                'message': 'Please enter correct format of device_type',
                'success':'False',
            })
        if profile_type not in ['1', '2']:
            raise APIException400({
                'message': 'Please enter correct format of profile_type',
                'success':'False',
            })
        if account_type not in ['1', '2', '3']:
            raise APIException400({
                'message': 'Please enter correct format of account_type',
                'success':'False',
            })
        if account_type in ['2','3']:
            if not social_id or social_id=='':
                raise APIException400({
                    'message': 'Please provide social id',
                })
        # if not mobile_number.isdigit():
        #     raise APIException400({
        #         'message': 'Please correct your mobile number',
        #         'success':'False',
        #     })
        if not email or email=="":
            raise APIException400({
                'message': 'Please provide email',
                'success':'False',
            })

        if profile_type == '2':

            if not lat or lat == "":
                raise serializers.ValidationError({
                    'lat': 'Please provide lat',
                })
            if not lon or lon == "":
                raise serializers.ValidationError({
                    'lon': 'Please provide lon',
                })

        return data

    def create(self,validated_data):
        username = validated_data['username']
        name = validated_data['name']
        # country_code = validated_data['country_code']
        # mobile_number = validated_data['mobile_number']
        email = validated_data['email']
        profession = validated_data['profession']
        password = validated_data['password']
        device_type = validated_data['device_type']
        device_token = validated_data['device_token']
        account_type = validated_data['account_type']
        profile_type = validated_data['profile_type']
        social_id = validated_data['social_id']



        company_name = validated_data['company_name']
        lat = validated_data['lat']
        lon = validated_data['lon']
        address_line1 = validated_data['address_line1']
        address_line2 = validated_data['address_line2']
        address_line3 = validated_data['address_line3']
        description = validated_data['description']
        bussiness_area = validated_data['bussiness_area']
        is_more_than_5_account = validated_data.get('is_more_than_5')


        year_of_foundation = validated_data['year_of_foundation']
        profile_image = self.context['request'].FILES.get('profile_image')
        print('image_user', profile_image)
        # picture = self.context['request'].FILES.get('picture')

        if profile_type=='1':
            profession=Profession.objects.filter(id=profession).first()
        if profile_type=='2':

            bussiness_area=BussinessArea.objects.filter(id=bussiness_area).first()
            if is_more_than_5_account and bussiness_area.type=="Manufacturer":
                bussiness_area = BussinessArea.objects.filter(type = 'Manufacturer premium').first()


        if account_type == '1':
            # user=User.objects.filter(Q(username=username) & Q(email=email)).first()
            # user=User.objects.filter(Q(country_code=country_code) & Q(mobile_number=mobile_number)).first()
            # UPDATE if exists
            # if (not user) and user1:
            #   raise APIException400({
            #       'message':'This mobile is registered with another username',
            #       'success':'False',
            #   })
            user, created = User.objects.get_or_create(email=email)
            if not created:
                # tu = User.objects.filter(email=email).exclude(id=user.id).first()
                # if tu:
                #     raise APIException400({
                #         'message':'This email id is already linked with another account',
                #         'success':'False',
                #     })
                raise APIException({
                    'message':'This email is already registered. Please proceed with login',
                    'success':'True'
                })
            

                # user.first_name=name.split('')[0]
            user.username=username
            # user.country_code=country_code
            # user.mobile_number=mobile_number
            user.email=email
            user.profile_type=profile_type
            user.device_type=device_type
            user.device_token=device_token
            user.is_profile_created=True
            user.save()
            user.set_password(password)
            user.save()
            logger.debug('inside serializer create')
            previous_token_device = GCMDevice.objects.filter(registration_id=device_token)
            if previous_token_device.exists():
                logger.debug('inside if create')
                # logger.debug('in if for device token', previous_token_device[0].registration_id)
                previous_token_device.update(registration_id='')
                # logger.debug( previous_token_device[0].registration_id)
                previous_token_user = User.objects.filter(device_token=device_token)
                # logger.debug('in if for device token', previous_token_user[0].device_token)
                previous_token_user.update(device_token='')
                # logger.debug(previous_token_user[0].device_token)
            GCMDevice.objects.create(registration_id=device_token, user=user, cloud_message_type='FCM')
            #--------- added
            if profile_image:
                user.profile_image = profile_image
            user.save()

            if profile_type=='1':
                user.profession = profession
                # if profile_image:
                #     user.profile_image=profile_image
                user.name=name
                first_name=name.split(' ')[0]
                user.save()
            elif profile_type=='2':
                company = Company.objects.filter(user=user).first()

                if company:
                    company.name=company_name
                    company.lat = lat
                    company.lon = lon
                    company.address_line1=address_line1
                    company.address_line2=address_line2
                    company.address_line3=address_line3
                    company.description=description
                    company.bussiness_area=bussiness_area
                    company.is_more_than_5_account =is_more_than_5_account
                    company.year_of_foundation=year_of_foundation
                    if profile_image:
                        company.picture=profile_image
                    company.save()
                else:
                    company = Company.objects.create(name=company_name,lat=lat,lon=lon,address_line1=address_line1,
                        address_line2=address_line2,address_line3=address_line3,description=description,
                        bussiness_area=bussiness_area,is_more_than_5_account= is_more_than_5_account,year_of_foundation=year_of_foundation,user=user,)
                    if profile_image:
                        company.picture=profile_image
                        company.save()

            # CREATE if not exists
            # else:
            #     raise APIException400({
            #         'success':'False',
            #         'message':'Your number is not present in our database'
            #     })

                # user = User.objects.create(username = username,mobile_number=mobile_number,country_code=country_code,
                #                       email=email,account_type=account_type,profile_type=profile_type,
                #                       device_type=device_type,device_token=device_token,is_profile_created=True)
                # user.set_password(password)
                # user.save()
                # if profile_type=='1':
                #   user.profession=profession
                #   if profile_image:
                #       user.profile_image=profile_image
                #   first_name=name.split(' ')[0]
                #   name=name
                #   user.save()
                # if profile_type=='2':
                #   company = Company.objects.create(name=company_name,address_line1=address_line1,
                #       address_line2=address_line2,address_line3=address_line3,description=description,
                #       bussiness_area=bussiness_area,year_of_foundation=year_of_foundation,user=user,)
                #   if profile_image:
                #       company.picture=profile_image
                #       company.save()

        elif account_type in ['2', '3']:
            social_obj, created=SocialAccounts.objects.get_or_create(social_id=social_id)
            # UPDATE if exists
            if created:
                social_obj.account_type=account_type
                social_obj.social_id=social_id
                # social_obj.save()

                # user = social_obj.user_id

                # tu1 = User.objects.filter(Q(country_code=country_code) & Q(mobile_number=mobile_number)).exclude(id=user.id).first()
                # tu2 = User.objects.filter(email=email).exclude(id=user.id).first()
                # if tu1:
                #     raise APIException400({
                #         'message':'This mobile is already registered with another account',
                #         'success':'False'
                #     })
                # if tu2:
                #     raise APIException400({
                #         'message':'This email is already registered with another account',
                #         'success':'False'
                #     })

                # user.username=username
                # user.country_code=country_code
                # user.mobile_number=mobile_number
                # user.email=email
                # user.profile_type=profile_type
                # user.device_type=device_type
                # user.device_token=device_token
                # user.is_profile_created=True
                # user.is_social_active=True
                # user.save()
                # user.set_password(password)
                # user.save()

                user = User.objects.create(username=username, email=email, profile_type=profile_type, device_token=device_token,
                is_profile_created=True, is_social_active=True)
                user.set_password(password)
                user.save()

                if profile_type=='1':
                    user.profession = profession
                    if profile_image:
                        user.profile_image=profile_image
                    user.first_name=name.split(' ')[0]
                    user.name=name
                    user.save()
                elif profile_type=='2':
                    company = Company.objects.filter(user=user).first()

                    if company:
                        company.name=company_name
                        company.lat = lat
                        company.lon = lon
                        company.address_line1=address_line1
                        company.address_line2=address_line2
                        company.address_line3=address_line3
                        company.description=description
                        company.bussiness_area=bussiness_area
                        company.is_more_than_5_account =is_more_than_5_account
                        company.year_of_foundation=year_of_foundation
                        if profile_image:
                            company.picture=profile_image
                        company.save()
                    else:
                        company = Company.objects.create(name=company_name,lat=lat,lon=lon,address_line1=address_line1,
                            address_line2=address_line2,address_line3=address_line3,description=description,
                            bussiness_area=bussiness_area,is_more_than_5_account= is_more_than_5_account,year_of_foundation=year_of_foundation,user=user,)
                        if profile_image:
                            company.picture=profile_image
                            company.save()
            # CREATE is not exists
            # else:
            #     raise APIException400({
            #         'success':'False',
            #         'message':'Your social account is not present in the record',
            #     })
                # user = User.objects.create(username = username,mobile_number=mobile_number,country_code=country_code,
                #                       email=email,account_type=account_type,profile_type=profile_type,
                #                       device_type=device_type,device_token=device_token,is_profile_created=True,
                #                       is_social_active=True,profile_image=profile_image)
                # user.set_password(password)
                # user.save()
                # social_account = SocialAccounts.objects.create(user_id=user,account_type=account_type,
                #                                               social_id=social_id)
                # if profile_type=='1':
                #   user.profession=profession
                #   if profile_image:
                #       user.profile_image=profile_image
                #   first_name=name.split(' ')[0]
                #   name=name
                #   user.save()
                # if profile_type=='2':
                #   company = Company.objects.create(name=company_name,address_line1=address_line1,
                #       address_line2=address_line2,address_line3=address_line3,description=description,
                #       bussiness_area=bussiness_area,year_of_foundation=year_of_foundation,user=user,)
                #   if profile_image:
                #       company.picture=profile_image
                #       company.save()

            # user_qs = User.objects.filter(Q(mobile_number__iexact=mobile_number) & Q(country_code=country_code)).exclude(
            #   Q(mobile_number__isnull=True) & Q(mobile_number__iexact='')
            # ).distinct()

                social_obj.user_id = user
                social_obj.save()
            user = social_obj.user_id
        validated_data['user_id']=user.id
        return validated_data


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField(error_messages={'required':'email key is required', 'blank': 'email is required'})

    class Meta:
        model = User
        fields = [

            'email',
        ]

    password_reset_form_class = MyPasswordResetForm

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(_('Error'))

        if not User.objects.filter(email=value, account_type ="1").exists():
            raise serializers.ValidationError(_('This e-mail address is not linked with any account'))
        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }
        self.reset_form.save(**opts)


class ChangePasswordSerializer(Serializer):
    old_password = CharField(error_messages={'required': 'old_password key is required', 'blank': 'Old password is required'})
    new_password = CharField(error_messages={'required': 'new_password key is required', 'blank': 'New password is required'})

    def validate_old_password(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters',
                })
        return password
    def validate_new_password(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters',
                })
        return password


class ColleaugeProfileCreateSerializer(Serializer):
    username = serializers.CharField(error_messages={'required': 'username key is required', 'blank': 'username is required'})
    mobile_number = serializers.CharField(allow_blank=True,error_messages={'required': 'mobile_number key is required'})
    country_code = serializers.CharField(allow_blank=True,error_messages={'required': 'country_code key is required'})
    email = serializers.CharField(error_messages={'required': 'email key is required', 'blank': 'email is required'})
    password = serializers.CharField(error_messages={'required': 'password key is required', 'blank': 'password is required'})

    def validate(self, data):

        # if not data['mobile_number'].isdigit():
        #     raise serializers.ValidationError({'message': 'Invalid mobile number'})

        if len(data['password']) < 8:
            raise serializers.ValidationError({'message': 'Password must be at least 8 characters'})

        user = User.objects.filter(username=data['username'])
        if user.exists():
            raise serializers.ValidationError({'message': 'This username already taken'})

        if data['mobile_number'] and not data['country_code']:
            raise serializers.ValidationError({'message': 'country code is required'})

        if data['mobile_number'] and data['country_code']:
            user_qs =User.objects.filter(mobile_number = data['mobile_number'], country_code=data['country_code'])
            if user_qs.exists():
                raise serializers.ValidationError({'message': 'User with this mobile number is already exist'})

        user_qs = User.objects.filter(email =data['email'])
        if user_qs.exists():
            raise serializers.ValidationError({'message': 'User with this email is already exist'})

        return data
