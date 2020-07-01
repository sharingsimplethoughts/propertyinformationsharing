from django.db import models
from datetime import datetime

ABOUT_US = (('1', 'AboutUs'), ('2', 'fbLink'), ('3', 'twitterLink'), ('4', 'instaLink'))


class TermsAndCondition(models.Model):
    title = models.CharField(max_length=100, default='')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Terms and Condition-' + str(self.id)

    class Meta:
        unique_together = ('title', )


class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=100, default='')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'PrivacyPolicy-' + str(self.id)

    class Meta:
        unique_together = ('title', )


class Faq(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    created_on = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('question', )

    def __str__(self):
        return 'Faq-' + str(self.question)


class AboutUS(models.Model):
    key = models.CharField(max_length=1, choices=ABOUT_US)
    content = models.CharField(max_length=512)
    created_on = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('key',)
