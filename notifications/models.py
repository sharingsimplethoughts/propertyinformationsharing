from accounts.models import *
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

NOTIFICATION_TYPE = (
    ('1', 'POST_INVOLVEMENT'), ('2', 'POST_COMMENT'), ('3', 'POST_LIKE'), ('4', 'POST_NEW'), ('5', 'QUESTION_NEW'),
    ('6', 'UPDATE_FOLLOWED_USER'), ('7', 'Chat'), )
ADMIN_NOTIFICATION_TYPE = (('1', 'REPORT_PROFILE'), ('2', 'REPORT_POST'), ('3', 'FLAG_PROFILE'), ('4', 'FLAG_POST'),
                           ('5', 'NEW_REGISTRATION'))


class NotificationsDetail(models.Model):
    notification_by = models.ForeignKey(User, blank=False, on_delete=models.CASCADE,
                                        related_name='notification_by_user')
    notification_for = models.ForeignKey(User, blank=False, on_delete=models.CASCADE,
                                         related_name='notification_for_users')
    notification_type = models.CharField(max_length=1, choices=NOTIFICATION_TYPE, blank=False)
    notification_context = JSONField()
    notification_sender_model_name = models.CharField(max_length=50, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class AdminNotifications(models.Model):
    notification_by = models.ForeignKey(User, blank=False, on_delete=models.CASCADE,
                                        related_name='notification_admin_user')
    notification_type = models.CharField(max_length=1, choices=ADMIN_NOTIFICATION_TYPE, blank=False)
    notification_context = JSONField()
    sender_model_name = models.CharField(max_length=50, blank=False)
    sender_pk = models.IntegerField(blank=False)
    read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def get_created_time(self):
        time = timezone.now()

        if self.created_on.day == time.day and self.created_on.month == time.month and self.created_on.year == time.year:
            if (time.hour - self.created_on.hour) == 0:
                minute = time.minute - self.created_on.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created_on.hour) + " hours ago"
        else:
            time_left = (time - self.created_on).days
            if time_left < 1:

                return str((time-self.created_on).seconds // 3600) + " hours ago"
            elif 1 <= time_left < 30:
                return str(time_left) + " days ago"
            elif 30 <= time_left < 365:
                return str(round(time_left / 30)) + " months ago"
            elif time_left >= 365:
                return str(round(time_left / 365)) + " years ago"
            else:
                return self.created_on
