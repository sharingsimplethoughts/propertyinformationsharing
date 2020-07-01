from django.contrib import admin
from .models import *
# Register your models here.
class UserAdmin(admin.ModelAdmin):
	list_display = ('name','is_active','mobile_number','email')
	search_fields = ('name','mobile_number','email')

admin.site.register([CountryCode])
# admin.site.register(GuestAccount)
admin.site.register(User, UserAdmin)
admin.site.register(SocialAccounts)
admin.site.register(Device)
admin.site.register(Profession)
admin.site.register(BussinessArea)
admin.site.register(Company)
admin.site.register(OTPStorage)
admin.site.register(UserLocation)
admin.site.register(JWTTokenRecords)
admin.site.register(FollowersAndFollowing)
admin.site.register(ProfileLiked)
admin.site.register(ProfileReportReasons)
admin.site.register(ReportProfile)
admin.site.register(FlagProfile)
admin.site.register(ProfileFlagReasons)
admin.site.register(SocialLinks)
admin.site.register(LogInData)