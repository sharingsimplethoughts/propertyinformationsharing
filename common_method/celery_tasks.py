from django.apps import apps
from celery import shared_task
from push_notifications.models import GCMDevice, APNSDevice

from PropInfoShare.celery import app
from django.template.loader import render_to_string
from django.core import mail
from accounts.models import User, LogInData
from PropInfoShare.settings import BASE_URL
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.api.token import account_activation_token
# from common_method.firebase import createNode, deleteNode, updateNode
from authy.api import AuthyApiClient

authy_api = AuthyApiClient('')
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# @shared_task(track_started=True)
# def send_email_verify_mail(user_id):
#     user_obj = User.objects.get(id=user_id)

#     subject = 'Activate Your Viewed Account'
#     to = user_obj.email
#     plain_message = None
#     from_email = 'Viewed <webmaster@localhost>'
#     message_text = render_to_string('account_activation/account_activation_email.html', {
#         'user': user_obj,
#         'domain': BASE_URL,
#         'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(),
#         'token': account_activation_token.make_token(user_obj),
#     })
#     mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)

#     return 'success..!!'


# ----------- new
@shared_task
def send_mail_shared(subject, plain_message, from_email, to, html_message):
    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return 'Mail sent success'
# ----------- end


# ---------- notification job
@shared_task
def send_new_notification_shared(**kwargs):
    sender_model = apps.get_model('{}'.format(kwargs['sender_model_name']))
    instance = kwargs['context']
    data = {}
    for key in instance:
        if key not in ('user_id', 'title', 'body', 'followers', 'exclude_user_id'):
            data[key] = instance[key]
    excluded_users = list(LogInData.objects.filter(logged_in=False).values_list('user', flat=True))
    print('logged_out', excluded_users)
    if instance['notification_type'] in ('5', '4', ):
        excluded_users.extend(kwargs['context']['exclude_user_id'])
        print('kwargs', kwargs['context']['exclude_user_id'])
        print('updated', excluded_users)
        devices = GCMDevice.objects.all().exclude(user__id__in=excluded_users)
    else:
        if instance['notification_type'] == '1':
            excluded_users.extend(kwargs['context']['exclude_user_id'])
        devices = GCMDevice.objects.filter(user__id__in=kwargs['context']['user_id']).exclude(user__id__in=excluded_users)

    print('devices', devices)
    if len(devices) != 0:
        for device in devices:
            if device.registration_id == '':
                continue
            print('same', GCMDevice.objects.filter(registration_id=device.registration_id))
            device.send_message(
                None,
                extra={
                    'title': instance['title'],
                    'body': instance['body'],
                    'misc': data
                }
            )
    # device = GCMDevice.objects.get(registration_id='fjVidL9Gmg0:APA91bEI2gFNqnl1nVSm4C7X5nIqrPESQi-GSb9fzeSV5y9HZXgcyUAm5NbBCFxNm70TftHo2GnRU4ENG_nZASxDytEQdT20WLzg_839D2KbAOenBmtcb2zlkVtM2u2Mna-s22DWqBXv')
    # device.send_message(
    #     None,
    #     extra={
    #         'title': instance['title'],
    #         'body': instance['body'],
    #         'misc': data
    #     }
    # )
    return 'Notification sent success'
# ----------- end


# @shared_task(track_started=True)
# def send_phone_verify_otp(country_code, mobile_number ):
#     request = authy_api.phones.verification_start(mobile_number, country_code,
#                                 via='sms', locale='en')
#     if request.content['success'] == True:
#         return 'successfully send message'
#     else:
#         return 'faild to send message' + request.content['message']


# @shared_task(track_started=True)
# def create_user_node(first_name, last_name, id, profile_image):
#     createNode(first_name, last_name ,id, profile_image)
#     return 'successfully created user node'

# @shared_task(track_started=True)
# def update_user_node(first_name, last_name, id, profile_image):
#     updateNode(first_name, last_name ,id, profile_image)
#     return 'successfully created user node'

# @shared_task(track_started=True)
# def delete_user_node(id):
#     deleteNode(id)
#     return 'successfully created user node'
