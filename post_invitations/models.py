import datetime

from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from invitations import signals
from invitations.adapters import get_invitations_adapter
from invitations.app_settings import app_settings

from accounts.models import User
from posts.models import Post
from invitations.models import Invitation


class MyInvitation(models.Model):
    email = models.EmailField(verbose_name=_('e-mail address'),
                              max_length=254)
    created = models.DateTimeField(verbose_name=_('created'),
                                   default=timezone.now)
    accepted = models.BooleanField(verbose_name=_('accepted'), default=False)
    key = models.CharField(verbose_name=_('key'), max_length=64, unique=True)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    inviter = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    @classmethod
    def generate_key(cls, **kwargs):
        return get_random_string(64).lower()

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        return cls._default_manager.create(
            email=email,
            key=cls.generate_key(**kwargs),
            inviter=inviter,
            **kwargs)

    def key_expired(self):
        expiration_date = (
            self.sent + datetime.timedelta(
                days=app_settings.INVITATION_EXPIRY))
        return expiration_date <= timezone.now()

    def send_invitation(self, request, **kwargs):
        current_site = kwargs.pop('site', Site.objects.get_current())
        invite_url = reverse('invitations:accept-invite',
                             args=[self.key])
        invite_url = request.build_absolute_uri(invite_url)
        ctx = kwargs
        ctx.update({
            'invite_url': invite_url,
            'site_name': current_site.name,
            'email': self.email,
            'key': self.key,
            'inviter': self.inviter,
        })

        email_template = 'invitations/email/email_invite'

        get_invitations_adapter().send_mail(
            email_template,
            self.email,
            ctx)
        self.sent = timezone.now()
        self.save()

        signals.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=invite_url,
            inviter=self.inviter)


class InvitationPost(models.Model):
    invitation_id = models.ForeignKey(MyInvitation, on_delete=models.DO_NOTHING, blank=False,
                                      related_name='invitation_id')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False, related_name='invited_post_id')

