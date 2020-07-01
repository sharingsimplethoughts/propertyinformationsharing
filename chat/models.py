from django.db import models
from accounts.models import User


class BlockUserChat(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name='blocked_user_id')
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_blocked_by')

    def clean(self):
        if self.user_id == self.blocked_by:
            from django.core.exceptions import ValidationError
            raise ValidationError('user_id cant same as blocked_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'blocked_by'], name='unique_user_blocked_ids'),
        ]


def chat_directory_path(instance, filename):
    return 'chat/chat{0}/{0}{1}'.format(instance.user.id, filename)


class UploadFileChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='user_id')
    file = models.FileField(upload_to=chat_directory_path, blank=False)
