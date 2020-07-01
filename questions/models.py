from django.db import models
from accounts.models import *
# Create your models here.
from django.utils import timezone
from posts.models import ReportReasons


class Question(models.Model):

    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="q_guest",)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    # country_code = models.CharField(max_length=10, blank=True, null=True)
    # mobile_number = models.CharField(max_length=20, blank=True, null=True)
    picture = models.ImageField(upload_to='questions')
    question_text = models.CharField(max_length=1000, blank=True, null=True, default='')
    lat = models.CharField(max_length=100, blank=True, null=True)
    lon = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    total_comments = models.PositiveSmallIntegerField(default=0)
    total_likes = models.PositiveSmallIntegerField(default=0)
    total_reported = models.PositiveSmallIntegerField(default=0)
    total_shares = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.nickname

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
                return str((time - self.created_on).seconds // 3600) + " hours ago"
            elif 1 < time_left < 30:
                return str(time_left) + " days ago"
            elif 30 <= time_left < 365:
                return str(round(time_left / 30)) + " months ago"
            elif time_left >= 365:
                return str(round(time_left / 365)) + " years ago"
            else:
                return self.created_on


class QuestionLikes(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='liked_question_id')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_liked_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question_id', 'liked_by')


class QuestionComments(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_comments')
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_comment_user')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    total_like = models.PositiveSmallIntegerField(default=0)

    def get_created_time(self):
        time = timezone.now()

        if self.created.day == time.day and self.created.month == time.month and self.created.year == time.year:
            if (time.hour - self.created.hour) == 0:
                minute = time.minute - self.created.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created.hour) + " hours ago"
        else:
            time_left = (time - self.created).days
            if time_left < 1:
                return str((time - self.created).seconds // 3600) + " hours ago"
            elif 1 < time_left < 30:
                return str(time_left) + " days ago"
            elif 30 <= time_left < 365:
                return str(round(time_left / 30)) + " months ago"
            elif time_left >= 365:
                return str(round(time_left / 365)) + " years ago"
            else:
                return self.created


class QuestionCommentLike(models.Model):
    comment_id = models.ForeignKey(QuestionComments, on_delete=models.CASCADE, related_name='question_comments_like')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_comment_liked_user')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) +'-' + str(self.comment_id.id)

    class Meta:
        unique_together = ('comment_id', 'liked_by')


class QuestionReport(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reported_question')
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_by_user')
    reason = models.ForeignKey(ReportReasons, blank=True, null=True,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user')

