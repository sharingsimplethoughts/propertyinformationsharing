from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from accounts.api.token import account_activation_token

User = get_user_model()

from django.views import View


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_mail_verify = True
        user.save()
        return HttpResponse("Your account is successfully Activated")
    else:
        return HttpResponse("Invalid token")


# class ServiceWorkerView(View):
#
#     def get(self, request, *args, **kwargs):
#         print('sw returned')
#         return render(request, 'fcm/firebase-messaging-sw.js', content_type="application/x-javascript")