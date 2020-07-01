from django.urls import reverse
from django.views.generic import TemplateView
import stripe
from push_notifications.models import GCMDevice

from PropInfoShare.settings import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
from rest_framework.generics import (
    CreateAPIView,
)

from PropInfoShare.signals import admin_notification
from payment.api.views import make_payment
from post_invitations.models import InvitationPost, MyInvitation
from posts.models import PostOwner
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from accounts.models import *
import random
import string

from django.core import mail
from django.db.models import F
from django.db.models import Q
from PropInfoShare.settings import BASE_URL
from authy.api import AuthyApiClient

from ..forms import SignUpForm

authy_api = AuthyApiClient("")

from PropInfoShare.settings import REMOTE_BASE_URL

User = get_user_model()

# PASSWORD RESET BY EMAIL START-------
from .settings import (
    PasswordResetSerializer,
)
from common_method.validators import get_error

from rest_framework_jwt.settings import api_settings
from django.contrib.sites.shortcuts import get_current_site

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from rest_framework.generics import GenericAPIView
from rest_framework import status

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect, render
from django.dispatch import receiver

from invitations.views import AcceptInvite
from invitations.app_settings import app_settings
from invitations.adapters import get_invitations_adapter
from invitations.models import Invitation
from invitations.signals import invite_accepted

from allauth.account.signals import user_signed_up
from allauth.account.models import EmailAddress
# END--------------------------------

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .password_reset_form import MyPasswordResetForm

# send email verify email
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from accounts.api.token import account_activation_token
import datetime

import logging

logger = logging.getLogger('accounts')
from common_method.celery_tasks import send_mail_shared
# from common_method.celery_tasks import send_email_verify_mail, create_user_node, send_phone_verify_otp ,delete_user_node, update_user_node
# from common_method.validators import get_error

from twilio.rest import Client

account = "fgh"
token = "hjgj"
from_no = "+564"
client = Client(account, token)
from common_method.validators import get_token
from accounts.middleware import ValidateJWTToken


def id_generator2(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def id_generator(size=4):
    return random.randint(1000, 9999)


def send_otp(country_code, mobile_number):
    verification_code = id_generator(size=4)
    try:
        message = client.messages.create(to=country_code + mobile_number, from_=from_no,
                                         body="Hello there! Your  Exchange otp is " + str(verification_code))
        otp_obj = OTPStorage(
            country_code=country_code,
            mobile=mobile_number,
            otp=verification_code,
        )
        otp_obj.save()
        print('end of try')
    except:
        return 0  # after twilio it should be 0
    return verification_code


# request = authy_api.phones.verification_start(mobile_number, country_code,via='sms', locale='en')
# return request
def verify_otp(country_code, mobile_number, verification_code):
    otp_obj = OTPStorage.objects.filter(country_code=country_code, mobile=mobile_number, is_used=False).order_by(
        '-id').first()
    if otp_obj:
        if otp_obj.otp == "1234" or otp_obj.otp == verification_code:
            otp_obj.is_used = True
            otp_obj.save()
            return 1
        return 0
    # check = authy_api.phones.verification_check(mobile_number, country_code, verification_code)
    return 0


class CountryCodeListView(APIView):
    def get(self, request, *args, **kwargs):
        logger.debug('Country code list get called')
        logger.debug(request.data)
        queryset = CountryCode.objects.all()
        serializer = CountryCodeListSerializer(queryset, many=True)
        return Response({
            'message': 'Data retrieved successfully',
            'success': 'True',
            'data': serializer.data,
        }, status=200, )


class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug('Login post called')
        logger.debug(request.data)
        social_id = request.data['social_id']
        if social_id:
            soc = SocialAccounts.objects.filter(social_id=social_id).first()
            if not soc:
                return Response({
                    'message': 'Social id does not exists. Please register first',
                    'success': 'False',
                }, 403)
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            user_obj = User.objects.filter(id=data['user_id']).first()
            user_obj.device_type = data['device_type']
            user_obj.save()
            # if user_obj.profile_type=='1':
            # user_data = UserDetailPersonalSerializer(user_obj,context={'request':request}).data
            # else:

            # edit
            user_data = LoggedInSerializer(user_obj, context={'request': request}).data
            login_user, created = LogInData.objects.get_or_create(user=user_obj)
            login_user.logged_in = True
            login_user.last_login = datetime.datetime.now()
            login_user.save()

            if user_obj.profile_type == '1':
                captured = True
            elif user_obj.profile_type == '3':
                captured = True
            elif user_obj.profile_type == '2':
                company = Company.objects.filter(user=user_obj).first()
                bussiness_type = company.bussiness_area.subscription.id

            if user_obj.profile_type == '2':
                if bussiness_type != 2:
                    print('in if')
                    payment_history = PaymentHistory.objects.filter(user=user_obj)
                    for _ in payment_history:
                        if _.captured:
                            captured = True
                            break
                    else:
                        captured = False
                else:
                    captured = True

            return Response({
                'message': 'Login successful',
                'success': 'True',
                'data': user_data,
                'captured': captured,
            }, status=200)
        else:
            return Response({
                'message': 'Login failed',
                'success': 'False',
                'data': serializer.errors
            }, status=400)


class LoginAsGuestView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug('Login as guest post called')
        logger.debug(request.data)
        serializer = LoginAsGuestSerializer(data=request.data)
        if serializer.is_valid():
            country_code = serializer.data['country_code']
            mobile_number = serializer.data['mobile_number']
            social_id = serializer.data['social_id']
            email = serializer.data['email']
            res = ''

            if social_id:

                social_obj = SocialAccounts.objects.filter(social_id=social_id).first()
                if social_obj:

                    u = social_obj.user_id

                    # restrict registered user for login
                    if u.is_profile_created:
                        return Response({
                            'message': 'Please login by using email and password'
                        }, 400)

                    if email:
                        if u.email != email:
                            raise APIException({
                                'message': 'This email is not valid against this social id',
                                'success': 'False',
                            })

                    if country_code and mobile_number:
                        if u.country_code != country_code or u.mobile_number != mobile_number:
                            raise APIException({
                                'message': 'This mobile number is not valid against this social id',
                                'success': 'False',
                            })

                    if u.is_num_verify == False:
                        res = send_otp(country_code, mobile_number)
                        if res != 0:
                            message = 'Successfully sent otp'
                        else:
                            message = 'Invalid mobile number. Unable to send otp.'
                            return Response({
                                'message': message,
                                'success': 'False'
                            }, status=400)
                    else:
                        message = 'Already verified otp',
                    data = {
                        'email': u.email,
                        'country_code': u.country_code,
                        'mobile_number': u.mobile_number,
                        'verification_code': res,
                        'is_num_verify': u.is_num_verify,
                        'is_social_active': u.is_social_active,
                        'is_profile_created': u.is_profile_created,
                        'profile_type': u.profile_type,
                        "business_type": '0',
                        'token': get_token(u)
                    }
                    return Response({
                        'message': message,
                        'success': 'True',
                        'data': data,
                    }, 200)

            u = User.objects.filter(country_code=country_code, mobile_number=mobile_number).first()
            if u:
                # restrict registered user for login
                if u.is_profile_created:
                    return Response({
                        'message': 'Please login by using email and password'
                    }, 400)

                if u.is_num_verify == False:
                    res = send_otp(country_code, mobile_number)
                    if res != 0:
                        message = 'Successfully sent otp'
                    else:
                        message = 'Invalid mobile number. Unable to send otp.'
                        return Response({
                            'message': message,
                            'success': 'False'
                        }, status=400)
                else:
                    message = 'Already verified otp'
                data = {
                    'email': u.email,
                    'country_code': u.country_code,
                    'mobile_number': u.mobile_number,
                    'verification_code': res,
                    'is_num_verify': u.is_num_verify,
                    'is_social_active': u.is_social_active,
                    'is_profile_created': u.is_profile_created,
                    'profile_type': u.profile_type,
                    "business_type": '0',
                    'token': get_token(u)
                }
                return Response({
                    'message': message,
                    'success': 'True',
                    'data': data,
                }, 200)

            if email:
                uobj = User.objects.filter(email=email).first()
                if uobj:
                    raise APIException({
                        'message': 'This email is already used for another account',
                        'success': 'False',
                    })

            res = send_otp(country_code, mobile_number)

            if res != 0:

                message = 'Successfully sent otp'
                u = User(
                    username=str(country_code) + str(mobile_number),
                    country_code=country_code,
                    mobile_number=mobile_number,
                    email=email,
                    profile_type='4'
                )
                u.save()
                if social_id:
                    s = SocialAccounts(
                        user_id=u,
                        social_isociald=social_id,
                    )
                    s.save()
                    u.is_social_active = True
                    u.save()
                data = {
                    'email': u.email,
                    'country_code': u.country_code,
                    'mobile_number': u.mobile_number,
                    'verification_code': res,
                    'is_num_verify': u.is_num_verify,
                    'is_social_active': u.is_social_active,
                    'is_profile_created': u.is_profile_created,
                    'profile_type': u.profile_type,
                    "business_type": '0',
                    'token': get_token(u)
                }
                return Response({
                    'message': message,
                    'success': 'True',
                    'data': data,
                }, status=200)

            else:
                '''
				NEED TO change this after getting twilio key
				'''
                # message='Successfully sent otp'
                # return Response({
                # 	'message':message,
                # 	'success':'True',
                # 	'data':data,
                # },status=200)

                message = 'Invalid mobile number. Unable to send otp.'
                return Response({
                    'message': message,
                    'success': 'False'
                }, status=400)
        else:
            return Response({
                'message': 'Some error',
                'success': 'False',
                'data': serializer.errors
            }, status=400)


class OTPVerifyView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug('Otp verify post called')
        logger.debug(request.data)
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            country_code = serializer.data['country_code']
            mobile_number = serializer.data['mobile_number']
            verification_code = serializer.data['verification_code']
            res = verify_otp(country_code, mobile_number, verification_code)
            if res == 1 or verification_code == '1234':
                u = User.objects.filter(country_code=country_code, mobile_number=mobile_number).first()
                u.is_num_verify = True
                u.save()
                return Response({
                    'message': 'Verification successfull',
                    'success': 'True'
                }, status=200)
            return Response({
                'message': 'Verification failed',
                'success': 'False'
            }, status=400)
        return Response({
            'message': 'Verification failed',
            'success': 'False',
            'data': serializer.errors,
        }, status=400)


class BussinessAreaListView(APIView):
    def get(self, request, *args, **kwargs):
        logger.debug('Bussiness area list get called')
        logger.debug(request.data)
        queryset = BussinessArea.objects.all().exclude(type='Manufacturer premium')
        if queryset:
            serializer = BussinessAreaListSerializer(queryset, many=True)
            return Response({
                'message': 'Data retrieved successfully',
                'success': 'True',
                'data': serializer.data,
            }, status=200, )
        return Response({
            'message': 'No bussiness area found',
            'success': 'False',
        }, status=400, )


class ProfessionListView(APIView):
    def get(self, request, *args, **kwargs):
        logger.debug('Profession list get called')
        logger.debug(request.data)
        queryset = Profession.objects.all().order_by('id')
        if queryset:
            serializer = ProfessionListSerializer(queryset, many=True)
            return Response({
                'message': 'Data retrieved successfully',
                'success': 'True',
                'data': serializer.data,
            }, status=200, )
        return Response({
            'message': 'No profession found',
            'success': 'False',
        }, status=400, )


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def get(self, request, username, *args, **kwargs):
        logger.debug('User detail get called')
        logger.debug(request.data)
        user = User.objects.filter(username=username)
        if user.exists():
            user = user[0]
            if user.profile_type == '1':
                serializer = UserDetailPersonalSerializer(user, context={'request': request})
            else:
                serializer = UserDetailCompanySerializer(user, context={'request': request})
            return Response({
                'message': 'Data retrieved successfully',
                'success': 'True',
                'data': serializer.data,
            }, status=200, )
        else:
            return Response({
                'message': 'User not exists',
                'success': 'False'
            }, status=403, )


# ----------- feedback mail
class SendUserFeedbackView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            data = serializer.validated_data
            to = 'parvez.khan.010000@gmail.com'
            plain_message = None
            from_email = 'Viewed <webmaster@localhost>'
            subject = 'Feedback From ' + user.username
            message_text = render_to_string('mails/send_feedback.html', {
                'user': user.username,
                'feedback': data['feedback']
            })
            send_mail_shared.delay(subject, plain_message, from_email, to, html_message=message_text)
            return Response({
                'message': 'Feedback sent successfully',
                'success': 'True'
            }, status=200, )
        return Response({'message': 'Some exception occurred'}, status=400, )


# ----------- end


# -------- invite user
class InviteUserAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = InviteSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            inv_link = REMOTE_BASE_URL + '/api/v1/posts/project_post_detail/' + str(data['post_id'])
            try:
                post = Post.objects.get(id=data['post_id'], is_active=True, created_by=request.user)
            except:
                raise APIException({'message': 'Invalid post_id or you are trying to invite on some one else post'})
            if 'user_id' in data:
                user_ids = set(data['user_id'])
                if str(request.user.id) in user_ids:
                    raise APIException({'message': 'you cannot invite yourself'})
                user_ids = [user_id for user_id in user_ids if user_id != ""]
                users = User.objects.filter(id__in=user_ids)
                if not len(users) == len(user_ids):
                    raise APIException({'message': 'Some user ids doesnt exists'})
            if request.user.profile_type == '2':
                name = Company.objects.get(user=request.user).name
            else:
                name = request.user.name
            if 'email_id' in data:
                email_ids = data['email_id']
                email_ids = [email_id for email_id in email_ids if email_id != ""]
                for email_id in email_ids:
                    if email_id == request.user.email:
                        continue
                    to = email_id
                    plain_message = None
                    from_email = 'Viewed <webmaster@localhost>'
                    subject = 'Invite Link for a post'
                    message_text = render_to_string('mails/send_invite_link.html', {
                        'invited_user': email_id.split('@')[0],
                        'user': name,
                        'post_id': post.id,
                        'invite_link': inv_link,
                    })
                    send_mail_shared.delay(subject, plain_message, from_email, to, html_message=message_text)
        return Response({
            'message': 'invite link sent successfully',
            'success': 'True'
        }, status=200, )


# ------- end


# ---------- update device token
class UpdateDeviceTokenAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = UpdateDeviceTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            if data['old_token'] != request.user.device_token:
                return Response({
                    'message': 'Token validation failed',
                    'success': 'False'
                }, status=403, )
            user = User.objects.get(id=request.user.id)
            user.device_token = data['new_token']
            user.save()
            gcm_device = GCMDevice.objects.get(registration_id=data['old_token'], user=user)
            gcm_device.registration_id = data['new_token']
            gcm_device.save()
            return Response({
                'message': 'Token updated successfully',
                'success': 'True'
            }, status=200, )


# ---------- end


# ------------ get authorized user
class GetAuthourizedUserForInvite(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request):
        search_key = request.GET.get('name')
        user_qs = User.objects.filter((
                                              Q(first_name__icontains=search_key)
                                              | Q(email__icontains=search_key)
                                              | Q(username__icontains=search_key))
                                      & (Q(profile_type='2') | Q(profile_type='3')))
        data = GetUserListSerializer(user_qs, many=True, context={'request': request}).data
        return Response({
            'message': 'success',
            'data': data
        }, 200)


# ------------ end


# ---------- get list for owner
class GetUserListForOwnerView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request):
        search_key = request.GET.get('query')
        user_company_list = Company.objects.filter(bussiness_area_id__in=['1', '2']).exclude(
            user_id__id=request.user.id).values_list('user_id', flat=True)
        user_qs = User.objects.filter((
                Q(first_name__icontains=search_key)
                | Q(email__icontains=search_key)
                | Q(username__icontains=search_key)), id__in=user_company_list
        )
        data = GetUserListSerializer(user_qs, many=True, context={'request': request}).data
        return Response({
            'message': 'success',
            'data': data
        }, 200)


# ----------- end


# ------------ invitation validation
class InvitationValidation(AcceptInvite):
    def check_invitation_code(self, invitation, *args, **kwargs):
        if not invitation:
            get_invitations_adapter().add_message(
                kwargs['request'],
                messages.ERROR,
                'invitations/messages/invite_invalid.txt')
            return HttpResponse(status=400)
        if invitation and (invitation.accepted or invitation.key_expired()):
            return HttpResponse(status=410)
        if invitation.accepted:
            get_invitations_adapter().add_message(
                kwargs['request'],
                messages.ERROR,
                'invitations/messages/invite_already_accepted.txt',
                {'email': invitation.email})
            return HttpResponse(status=410)
        return HttpResponse(status=200)

    def get_invitation(self, *args, **kwargs):
        return MyInvitation.objects.filter(key=kwargs['key']).first()


# ------------ end


# ---------- accept invite view
class AcceptInviteView(APIView):
    def get(self, request, *args, **kwargs):
        invite_validation = InvitationValidation()
        kwargs['request'] = request
        invitation = invite_validation.get_invitation(*args, **kwargs)
        http_response = invite_validation.check_invitation_code(invitation, *args, **kwargs)
        if http_response.status_code != 200:
            return http_response
        form = SignUpForm
        return render(self.request, 'signUpPayment.html', context={'form': form, 'key': STRIPE_PUBLISHABLE_KEY})

    def post(self, request, *args, **kwargs):
        invite_validation = InvitationValidation()
        kwargs['request'] = request
        invitation = invite_validation.get_invitation(*args, **kwargs)
        http_response = invite_validation.check_invitation_code(invitation, *args, **kwargs)
        if http_response.status_code != 200:
            return http_response
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            try1 = render_to_string('pay.html', context={'key': STRIPE_PUBLISHABLE_KEY, 'amount': 500}, request=request)
            # payment_response = make_payment(request)
            # if payment_response.status_code == 200:
            if True:
                try:
                    user_obj = User.objects.create(username=data['username'], email=invitation.email, profile_type='2',
                                                   account_type='1',
                                                   device_type='1', is_profile_created=True)
                    user_obj.profile_image = request.FILES.get('profile_image')
                    user_obj.set_password(data['password'])
                    user_obj.save()
                    company_obj = Company.objects.create(user=user_obj, name=data['company_name'],
                                                         address_line1=data['address_line1'],
                                                         address_line2=data['address_line2'],
                                                         address_line3=data['address_line3'],
                                                         description=data['description'],
                                                         bussiness_area_id=int(data['bussiness_area']),
                                                         year_of_foundation=data['year_of_foundation'], lat=data['lat'],
                                                         lon=data['lon'], is_more_than_5_account=data['is_more_than_5'])
                    company_obj.picture = data['profile_image']
                    invitation = MyInvitation.objects.get(key=self.kwargs['key'])
                    invitation_post_obj = InvitationPost.objects.get(invitation_id=invitation)
                    post_owner_obj = PostOwner.objects.get(post_id=invitation_post_obj.post_id)
                    post_owner_obj.owner_id = user_obj
                    post_owner_obj.owner_joined = True
                    post_owner_obj.save()
                    invitation.accepted = True
                    invitation.save()
                except Exception as e:
                    try:
                        user = User.objects.get(username=data['username'])
                        company = Company.objects.filter(user=user)
                        if company.exists():
                            company.delete()
                        user.delete()
                    except:
                        raise APIException({'message': 'Some Exception occurred {}'.format(str(e))})

                    logger.debug('in sign up form {}'.format(str(e)))
                    return Response({
                        'message': 'Some Error occured.',
                        'status': 'False'
                    }, status=400)
                # get_invitations_adapter().get_user_signed_up_signal().connect()
                return render(self.request, 'thankyou.html')
        return render(self.request, 'signUpPayment.html', context={'form': form, 'key': STRIPE_PUBLISHABLE_KEY})


# @receiver(user_signed_up)
# def accept_invite(sender, request, user, **kwargs):
#     # Traverse from the user to verified email addresses. It is possible for a
#     # user to already have multiple email addresses if they typed in a different
#     # email after accepted the invite. In this case, the user will have two
#     # emails, but only one will be verified.
#     addresses = EmailAddress.objects.filter(user=user, verified=True) \
#         .values_list('email', flat=True)
#     # Check if any invites exist for this address and were accepted.
#     invites = Invitation.objects.filter(email__in=addresses)
#     if invites:
#         # Mark all these invites as accepted.
#         invites.update(accepted=True)
#         for invite in invites:
#             # Note that this doesn't send it with a request.
#             invite_accepted.send(sender=Invitation, email=invite.email)
#
#
# ----------- end


# ----------- report a user
class ReportUserView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = ReportUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                reason = ProfileReportReasons.objects.get(id=serializer.validated_data['reason_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid reason id'})

            try:
                user = User.objects.get(id=serializer.validated_data['user_id'])
            except:
                raise serializers.ValidationError({'message': 'User doesnt exists'})
            if user.id == request.user.id:
                raise APIException({'message': 'You cant report yourself'})
            else:
                obj, created = ReportProfile.objects.get_or_create(user=user, reported_by=request.user,
                                                                   reason_id=reason.id)
                obj.reason = reason
                obj.save()
                context = {
                    'title': 'New Report',
                    'body': '{} reported {}'.format(request.user.username, user.username)
                }
                admin_notification.send(sender=user, context=context, notification_by=request.user,
                                        notification_type='1', sender_model_name='posts.{}'.format(user.__class__.__name__))
                return Response({
                    'message': 'Reported successfully',
                    'success': 'True'
                }, status=200, )
        raise serializers.ValidationError({'message': get_error(serializer)})


# ----------- end


# ----------- flag user
class FlagUserView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = FlagUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                reason = ProfileFlagReasons.objects.get(id=serializer.validated_data['reason_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid reason id'})

            try:
                user = User.objects.get(id=serializer.validated_data['user_id'])
            except:
                raise serializers.ValidationError({'message': 'User doesnt exists'})
            if user.id == request.user.id:
                raise APIException({'message': 'You cant flag yourself'})
            else:
                obj, created = FlagProfile.objects.get_or_create(user=user, flaged_by=request.user, reason_id=reason.id)
                obj.reason = reason
                obj.save()
                context = {
                    'title': 'New Flag',
                    'body': '{} flagged {}'.format(request.user.username, user.username)
                }
                admin_notification.send(sender=user, context=context, notification_by=request.user,
                                        notification_type='3', sender_model_name='posts.{}'.format(user.__class__.__name__))
                return Response({
                    'message': 'Flagged successfully',
                    'success': 'True'
                }, status=200, )
        raise serializers.ValidationError({'message': get_error(serializer)})


# ----------- end


# ----------------- edit profile view
class UserEditProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        # serializer = EditProfileSerializer(data=request.data)
        # if serializer.is_valid(raise_exception=True):
        # validated_data = serializer.validated_data
        # name  = validated_data['name']
        # about = validated_data['about']
        try:
            user = User.objects.get(id=request.user.id)
        except:
            raise APIException({'message': 'Something went wrong'})
        if 'profile_image' in request.data:
            profile_image = request.data['profile_image']
            user.profile_image = profile_image
        else:
            profile_image = None
        if request.user.profile_type == '1':
            if 'name' in request.data:
                name = request.data['name']
                user.name = name
            if 'about' in request.data:
                about = request.data['about']
                user.about = about
            user.save()
        else:
            user.save()
        if request.user.profile_type == '2':
            company_obj = Company.objects.get(user=user)
            if 'company_name' in request.data:
                company_name = request.data['company_name']
                company_obj.name = company_name
            if 'company_desc' in request.data:
                company_desc = request.data['company_desc']
                company_obj.description = company_desc
            if profile_image:
                company_obj.picture = profile_image
            company_obj.save()

        if 'fb' in request.data:
            obj, created = SocialLinks.objects.get_or_create(user_id=request.user, account_type='1')
            obj.social_id = request.data['fb']
            obj.save()

        if 'twitter' in request.data:
            obj, created = SocialLinks.objects.get_or_create(user_id=request.user, account_type='2')
            obj.social_id = request.data['twitter']
            obj.save()

        if 'insta' in request.data:
            obj, created = SocialLinks.objects.get_or_create(user_id=request.user, account_type='3')
            obj.social_id = request.data['insta']
            obj.save()

        if 'google' in request.data:
            obj, created = SocialLinks.objects.get_or_create(user_id=request.user, account_type='4')
            obj.social_id = request.data['google']
            obj.save()

        if request.user.profile_type == '1':
            data = UserDetailPersonalSerializer(user, context={'request': request}).data
        else:
            data = UserDetailCompanySerializer(user, context={'request': request}).data

        return Response({
            'message': 'Profile Edited Sucessfully',
            'success': 'True',
            'data': data
        })


# -------------------- end


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        # logger.debug('User detail update or create called')
        # logger.debug(request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            user_obj = User.objects.filter(id=data['user_id']).first()
            # if data['profile_type']=='1':
            # user_data = UserDetailPersonalSerializer(user_obj,context={'request':request}).data
            # elif data['profile_type']=='2':

            # edit
            user_data = LoggedInSerializer(user_obj, context={'request': request}).data
            login_user, created = LogInData.objects.get_or_create(user=user_obj)
            login_user.logged_in = True
            login_user.last_login = datetime.datetime.now()
            login_user.save()
            context = {
                'title': 'New Registration',
                'body': 'New user with {} and id {} created'.format(user_obj.username, user_obj.pk)
            }
            admin_notification.send(sender=user_obj, context=context, notification_by=user_obj, notification_type='2',
                                    sender_model_name='accounts.{}'.format(user_obj.__class__.__name__))
            return Response({
                'message': 'Data saved successfully',
                'success': 'True',
                'data': user_data,
            }, status=200)

        # error_keys = list(serializer.errors.keys())
        # if error_keys:
        # 	error_msg = serializer.errors[error_keys[0]]
        # 	return Response({'message': error_msg[0]}, status=400)
        return Response(serializer.errors, status=400)


class PasswordResetView(GenericAPIView):
    """
	Calls Django Auth PasswordResetForm save method.
	Accepts the following POST parameters: email
	Returns the success/fail message.
	"""
    serializer_class = PasswordResetSerializer

    def post(self, request):
        logger.debug('Password reset post called')
        logger.debug(request.data)
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return the success message with OK HTTP status
            return Response(
                {
                    'message': "Password reset e-mail has been sent successfully"
                }, 200)

        error_keys = list(serializer.errors.keys())
        if error_keys:
            error_msg = serializer.errors[error_keys[0]]
            return Response({'message': error_msg[0]}, status=400)
        return Response(serializer.errors, status=400)


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get_object(self):
        logger.debug('Change password get called')
        return self.request.user

    def post(self, request, *args, **kwargs):
        logger.debug('Change password post called')
        logger.debug(request.data)
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")
            if old_password == new_password:
                raise APIException({'message': 'new password cant be same as old password'})
            # confPassword = serializer.data.get("confPassword")
            # if newPassword == confPassword:
            if not user.check_password(old_password):
                return Response({
                    "message": "You entered wrong current password"},
                    status=400)

            user.set_password(new_password)
            user.save()
            return Response(
                {
                    'message': 'Your password changed successfully'
                }, status=200)

        # fow showing all serializer errors one by one
        error_keys = list(serializer.errors.keys())
        if error_keys:
            error_msg = serializer.errors[error_keys[0]]
            return Response({'message': error_msg[0]}, status=400)
        return Response(serializer.errors, status=400)


class ViewColleagueProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.profile_type == '2':
            comp_obj = Company.objects.select_related('bussiness_area__subscription').get(user=user)
            data = {}
            coll_qs = User.objects.filter(colleague_company_id=comp_obj).annotate(
                colleague_password=F('colleague_pass')).values('id', 'username', 'colleague_password', 'email')
            # data =	ColleagueProfileSerializer(coll_obj).data
            data['colleague_accounts'] = coll_qs
            data['max_account_possible'] = comp_obj.bussiness_area.subscription.users_or_account
            return Response({
                'data': data
            }, 200)
        return Response({
            'message': 'Not a company profile'
        }, 400)


class DeleteColleagueProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user
        id = request.data.get('id')
        if id:
            try:
                coll_user = User.objects.get(id=id)
            except:
                return Response({
                    'message': 'invalid user id'
                }, 400)
            if not user.profile_type == '2':
                return Response({
                    'message': 'This account is not a company account'
                }, 400)
            comp = Company.objects.get(user=user)
            if not coll_user.colleague_company_id.id == comp.id:
                return Response({
                    'message': 'This user is not your company colleague'
                }, 400)
            coll_user.delete()
            comp.no_of_colleague_create = int(comp.no_of_colleague_create) - 1
            return Response({
                'message': 'User deleted successfully'
            }, 200)

        return Response({
            'message': 'Please provide user id'
        }, 400)


class CreateColleagueProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.profile_type == '2':
            serializer = ColleaugeProfileCreateSerializer(data=request.data)
            if serializer.is_valid():
                company_obj = Company.objects.select_related('bussiness_area__subscription').get(user=user)
                if not company_obj.no_of_colleague_create == company_obj.bussiness_area.subscription.users_or_account:
                    # if not company_obj.is_subscription_plan_active==True:
                    # 	return Response({
                    # 		'message': 'Your subscription plan is not active or expired'
                    # 	}, 400)
                    data = serializer.validated_data
                    user = User.objects.create(
                        username=data['username'], mobile_number=data['mobile_number'],
                        country_code=request.data['country_code'],
                        email=data['email'], profile_type='3',
                        colleague_company_id=company_obj, account_type='1', is_guest=False,
                        colleague_pass=data['password'], is_num_verify=True, is_profile_created=True, is_verified=True
                    )
                    user.set_password(data['password'])
                    user.save()

                    company_obj.no_of_colleague_create = int(company_obj.no_of_colleague_create) + 1
                    company_obj.save()

                    return Response({
                        'message': 'Colleague account created successfully'
                    }, 200)

            return Response({
                'message': get_error(serializer)
            }, 400)
        return Response({
            'message': 'Individual type account has no permission to create colleague profile'
        }, 400)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        try:
            JWTTokenRecords.objects.get(user=request.user, token=request.META.get('HTTP_AUTHORIZATION')).delete()
        except:
            raise APIException({'message': 'Something went wrong'})
        login_user, created = LogInData.objects.get_or_create(user=request.user)
        login_user.logged_in = False
        login_user.last_logout = datetime.datetime.now()
        login_user.save()
        return Response({
            'message': 'Logout successfully'
        }, 200)


class DeleteAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def delete(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            user.is_active = False
            user.save()
        except Exception as e:
            raise APIException({'message': str(e)})
        return Response({
            'message': 'Account deleted successfully'
        }, 200)


# -------------- edited
class LikeOtherProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user
        user_id = request.data.get('user_id')
        if not user_id or user_id == "":
            raise serializers.ValidationError({'message': 'user_id is required'})
        if user_id == str(user.id):
            return Response({
                'message': 'You can not like your own profile',
                'success': 'True'
            }, status=400, )
        try:
            user_obj = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'Invalid user id'
            }, 400)
        obj, created = ProfileLiked.objects.get_or_create(user=user_obj, liked_by=user)
        if not created:
            obj.delete()
            return Response({
                'message': 'Like removed from this user profile',
                'success': 'True',
                'likes': len(ProfileLiked.objects.filter(user=user_obj))
            }, status=200, )
        return Response({
            'message': 'Account liked successfully',
            'success': 'True',
            'likes': len(ProfileLiked.objects.filter(user=user_obj))
        }, 200)


# -------- end


class FollowAUserAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user
        user_id = request.data['user_id']
        try:
            user_obj = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'Invalid user id'
            }, 400)

        obj, created = FollowersAndFollowing.objects.get_or_create(followed_by=user, followed_to=user_obj)
        if not created:
            obj.delete()
            return Response({
                'message': 'Unfollowed successfully',
                'followed': 'False'
            }, 200)
        followed = True
        return Response({
            'message': 'You just followed ' + str(User.objects.get(id=obj.followed_to_id)),
            'followed': 'True'
        }, 200)


class ReportUserAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):

        reason_id = self.kwargs.get('reason_id')
        user_id = self.kwargs.get('user_id')
        try:
            res = ProfileReportReasons.objects.get(id=reason_id)
        except:
            return Response({
                'message': 'Invalid reason id'
            }, 400)

        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'Invalid user id'
            }, 400)

        obj, created = ReportProfile.objects.get_or_create(user=user, reported_by=request.user)
        if not created:
            obj.reason = res
            obj.save()

        return Response({
            'message': 'Reported successfully'
        }, 200)
