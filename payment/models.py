from django.db import models
from accounts.models import User
PAYMENT_METHOD = (('1', 'Card'),('3', 'Net banking'),('2' ,'Cash on delivery'))
PAYMENT_STATUS = (('1','Successed'),('2','Failed'))
from django.utils import timezone


class StripeCustomer(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    stripe_cus_id = models.CharField(max_length=300, blank=True, null=True)
    card_token = models.CharField(max_length=300, blank=True, null=True)
    card = models.CharField(max_length=40, blank=True, null=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    card_type = models.CharField(max_length=50,blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    exp_month = models.CharField(max_length=10)
    exp_year = models.CharField(max_length=10)

    def __str__(self):
        return str(self.id)


class PaymentHistory(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=200)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    status_message = models.TextField(blank=True, null=True)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    captured = models.BooleanField(default=False)
    payment_detail = models.CharField(max_length=100, blank=True, null=True)  # card token
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)