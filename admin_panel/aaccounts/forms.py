from django import forms
from django.contrib.auth.models import User

from accounts.models import *


class LoginForm(forms.Form):
    email=forms.CharField()
    password=forms.CharField()
    def clean(self):
        em=self.data['email']
        password=self.data['password']
        if not em or em=="":
            raise forms.ValidationError('This email id is required')
        if em:
            e = em.split('@')

            if len(e)==2:
                e1 = em.split('@')[1]
                e1_0 = e1.split('.')
                if len(e1_0)<2:
                    raise forms.ValidationError('This email is not valid')
                else:
                    e1_0_0=e1.split('.')[1]
                    if not e1_0_0 or e1_0_0=="":
                        raise forms.ValidationError('This email is not valid')
            else:
                raise forms.ValidationError('This email is not valid')


        if not password or password=="":
            raise forms.ValidationError('This password is also required')

        user_qs = User.objects.filter(email=em)
        usertemp = user_qs.exclude(email__isnull=True).exclude(email__iexact='').distinct()
        if usertemp.exists() and usertemp.count()==1:
            userObj=usertemp.first()
        else:
            raise forms.ValidationError('This email id does not exists')
        password=self.data['password']
        checked_pass = userObj.check_password(password)
        if checked_pass:
            if not userObj.is_superuser or not userObj.is_active:
                raise forms.ValidationError('You are not authorised to access this panel')
        else:
            raise forms.ValidationError('Authentication failed')

class ChangePasswordForm(forms.Form):
    oldpassword 	= forms.CharField()
    password 		= forms.CharField()
    confpassword 	= forms.CharField()

    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user',None)
         super(ChangePasswordForm, self).__init__(*args, **kwargs)
         self.fields['oldpassword'].strip = False
         self.fields['password'].strip = False
         self.fields['confpassword'].strip = False

    def clean(self):
        password = self.cleaned_data.get('password')
        confpassword =self.cleaned_data.get('confpassword')
        oldpassword = self.cleaned_data.get('oldpassword')

        if not oldpassword or oldpassword=="":
            raise forms.ValidationError('Please provide old password')
        if not password or password=="":
            raise forms.ValidationError('Please provide new password')
        if not confpassword or confpassword=="":
            raise forms.ValidationError('Please provide confirm password')

        if not len(password) >= 8 or not len(confpassword) >= 8:
            raise forms.ValidationError('Password must be at least 8 characters')

        if not self.user.check_password(oldpassword):
            raise forms.ValidationError('Incorrect old password')

        if password!=confpassword:
            raise forms.ValidationError('Both password fields should be same')

        return self.cleaned_data

class AdminProfileEditForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)
    mobile = forms.CharField(max_length=15, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user','None')
        # self.ruser=None
        # if not self.user:
        #     self.ruser = RegisteredUser.objects.filter(user=self.user)
        super(AdminProfileEditForm,self).__init__(*args,**kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not self.user.email==email:
            if email.count('@')>1:
                raise forms.ValidationError('Please provide a valid email')
            try:
                domain=email.split('@')[1]
            except:
                raise forms.ValidationError('Please provide a valid email')
            user_qs=User.objects.filter(email__iexact=email)
            if user_qs.exists():
                raise forms.ValidationError('This email already exists')
            return email
        return email

    def clean_mobile(self):
        mob=self.cleaned_data.get('mobile')
        str1=str(mob)
        if len(str(mob))>15:
            raise forms.ValidationError('This mobile number is not valid')

        alpha = ""
        num = ""
        special = ""
        for i in range(len(str1)):
            if (str1[i].isdigit()):
                num = num+ str1[i]
            elif((str1[i] >= 'A' and str1[i] <= 'Z') or
                (str1[i] >= 'a' and str1[i] <= 'z')):
                alpha += str1[i]
            else:
                special += str1[i]

        if alpha:
            raise forms.ValidationError('This mobile number is not valid')
        if special:
            raise forms.ValidationError('This mobile number is not valid')

        if not mob==self.user.mobile_number:
            if mob.isdigit() and len(mob)<10:
                raise forms.ValidationError('This mobile number is not valid')
            user_qs=User.objects.filter(mobile_number__iexact=mob)
            if user_qs.exists():
                raise forms.ValidationError('This mobile number already exists')
            return mob
        return mob

    def clean_name(self):
        name=self.cleaned_data.get('name')
        str1=str(name)
        if len(name)>25:
            raise forms.ValidationError('Name must contain maximum of 25 characters')
        alpha = ""
        num = ""
        special = ""
        for i in range(len(str1)):
            if (str1[i].isdigit()):
                num = num+ str1[i]
            elif((str1[i] >= 'A' and str1[i] <= 'Z') or
                (str1[i] >= 'a' and str1[i] <= 'z')):
                alpha += str1[i]
            else:
                special += str1[i]

        if num:
            raise forms.ValidationError('This name is not valid')
        if special:
            raise forms.ValidationError('This name is not valid')
