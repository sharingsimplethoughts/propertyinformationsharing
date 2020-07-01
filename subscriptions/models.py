from django.db import models
from accounts.models import *
# Create your models here.


class SubscriptionPlan(models.Model):

    plan_name=models.CharField(max_length=100,)
    plan_desc=models.CharField(max_length=800,)  #This is general description
    price=models.DecimalField(max_digits=10,decimal_places=2,default='0.00',)

    users_or_account=models.CharField(max_length=1000,blank=True,null=True,default='')
    comment_on_existing_posts=models.BooleanField(default=True)
    create_posts=models.BooleanField(default=False)
    mark_involvement_in_others_posts=models.BooleanField(default=False)
    add_pictures_link_to_others_posts=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now_add=True,)

    def __str__(self):
        return self.plan_name


