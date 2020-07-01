from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from subscriptions.models import SubscriptionPlan

ACCOUNT_TYPE = (('1', 'normal'), ('2', 'fb'), ('3', 'google'))
PROFILE_TYPE = (('1', 'Personal'), ('2', 'Company'), ('3', 'Company colleague'), ('4', 'Guest'))
DEVICE_TYPE = (('1', 'android'), ('2', 'ios'))
SOCIAL_LINKS = (('1','fb'), ('2', 'twitter'), ('3', 'insta'), ('4', 'google'))


class CountryCode(models.Model):
    country=models.CharField(max_length=50,blank=True,null=True)
    code=models.CharField(max_length=10,blank=True,null=True)
    country_code=models.CharField(max_length=100, blank=True, null=True,default='')

    def __str__(self):
        return self.country


class Profession(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.type


class User(AbstractUser):
    """
    Extended user model
    """
    GENDER = (('1', 'male'), ('2', 'female'))
    name = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    profession = models.ForeignKey(Profession,on_delete=models.CASCADE,null=True,related_name='u_profession')
    is_mail_verify = models.BooleanField(default=False)
    is_num_verify = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, choices=GENDER)
    profile_type = models.CharField(max_length=20, blank=True, choices=PROFILE_TYPE)
    # in case of colleauge
    colleague_company_id =models.ForeignKey('Company',on_delete=models.CASCADE,null=True,blank=True,related_name='colleague_company')
    colleague_pass = models.CharField(max_length=50, blank=True)

    cover_image = models.ImageField(blank=True, upload_to='cover_image')
    profile_image = models.ImageField(blank=True, upload_to='profile_image')
    is_profile_created = models.BooleanField(default=False)
    is_social_active = models.BooleanField(default=False)
    device_token = models.TextField()
    device_type = models.CharField(choices=DEVICE_TYPE, max_length=5)
    account_type = models.CharField(max_length=5,choices=ACCOUNT_TYPE)
    about = models.CharField(max_length=500,null=True,blank=True,default='')
    is_verified = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=True)

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name
    
    def __str__(self):
        return self.username

    # class Meta:
    #     unique_together = ('mobile_number', 'country_code')


#log in data
class LogInData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_log_in')
    logged_in = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    last_logout = models.DateTimeField(blank=True, null=True)


class FollowersAndFollowing(models.Model):
    followed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_by')
    followed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_to')
    created = models.DateTimeField(auto_now_add=True)


class ProfileLiked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_profile')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_by')
    created = models.DateTimeField(auto_now_add=True)

#------------- Flag classes
class ProfileFlagReasons(models.Model):
    reason = models.CharField(max_length=300)


class FlagProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flaged_profile')
    reason = models.ForeignKey(ProfileFlagReasons, on_delete=models.CASCADE, related_name='flaged_profile_reason')
    flaged_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flaged_profile_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'flaged_by', )
#----------- end


class ProfileReportReasons(models.Model):
    reason = models.CharField(max_length=300)


class ReportProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_profile')
    reason = models.ForeignKey(ProfileReportReasons, on_delete=models.CASCADE, related_name='reported_reason')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_by')
    created = models.DateTimeField(auto_now_add=True)


class SocialAccounts(models.Model):
    # social login
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    account_type = models.CharField(max_length=500, default=1, choices=ACCOUNT_TYPE)
    social_id = models.CharField(max_length=500, blank=True, null=True)


#------------- social links
class SocialLinks(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    account_type = models.CharField(max_length=1, blank=False, choices=SOCIAL_LINKS)
    social_id = models.CharField(max_length=500, blank=False)

    class Meta:
        unique_together = ('user_id', 'account_type')
#-------------- end


class Device(models.Model):
    """
    save device 
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE,)
    device_name = models.CharField(max_length=30, blank=True, null=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    app_version = models.CharField(max_length=100, blank=True, null=True)
    device_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.device_type


class BussinessArea(models.Model):
    type = models.CharField(max_length=100, blank=True, null=True)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='barea_subs', default = '1')

    def __str__(self):
        return self.type


class Company(models.Model):
    name=models.CharField(max_length=100, blank=True,null=True)
    lat = models.CharField(max_length=100, blank=True)
    lon = models.CharField(max_length=100, blank=True)
    address_line1=models.CharField(max_length=200, blank=True, null=True)
    address_line2=models.CharField(max_length=200, blank=True, null=True)
    address_line3=models.CharField(max_length=200, blank=True, null=True)
    description=models.CharField(max_length=500, blank=True, null=True)
    bussiness_area=models.ForeignKey(BussinessArea, on_delete=models.CASCADE,related_name='c_bussiness_area')
    is_more_than_5_account = models.BooleanField(default=False)
    is_subscription_plan_active = models.BooleanField(default=False)
    no_of_colleague_create = models.CharField(default='0' , max_length=10)
    year_of_foundation=models.CharField(max_length=5, blank=True, null=True)
    picture=models.ImageField(upload_to='company')
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='c_user')

    def __str__(self):
        return self.name


class OTPStorage(models.Model): #THIS IS THE GUEST STORAGE
    country_code=models.CharField(max_length=10,blank=True,null=True)
    mobile=models.CharField(max_length=20,blank=True,null=True)
    otp=models.CharField(max_length=10,blank=True,null=True)
    is_used=models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class UserLocation(models.Model):
    lat = models.CharField(max_length=50)
    lon = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    rest_address = models.CharField(max_length=300)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='ul_user',blank=True,null=True)

    def __str__(self):
        return self.country


class JWTTokenRecords(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='token_user',blank=True,null=True)
    token = models.TextField()
    created = models.DateTimeField(auto_now_add=True)