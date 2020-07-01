from datetime import date

from django import forms
from django.contrib.auth.models import User
import stripe
from PropInfoShare.settings import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
from accounts.models import *

stripe.api_key = STRIPE_SECRET_KEY


def year_choices():
    return ((x, x) for x in range(date.today().year, 1983, -1))


YEAR_CHOICES = year_choices()


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label='Username', widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'name': 'username',
                'placeholder': 'User Name'
            }
        ))
    company_name = forms.CharField(max_length=30, required=True, label='Company Name', widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'name': 'company_name',
                'placeholder': 'Company Name'
            }
        ))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'name': 'password',
            'placeholder': 'Password'
        }
    ))
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'name': 'confirm_password',
            'placeholder': 'Confirm Password'
        }
    ))
    profile_image = forms.ImageField(label='Profile Image', required=True)
    address_line1 = forms.CharField(max_length=100, required=True, label='Address Line 1', widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'name': 'add_line1',
                'placeholder': 'Address Line 1'
            }
        ))
    address_line2 = forms.CharField(max_length=100, required=True, label='Address Line 2', widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'name': 'add_line2',
                'placeholder': 'Address Line 2'
            }
        ))
    address_line3 = forms.CharField(max_length=100, required=True, label='Address Line 3', widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'name': 'add_line3',
                'placeholder': 'Address Line 3'
            }
        ))
    description = forms.CharField(max_length=300, required=True, label='Description', widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'rows': '5',
            'placeholder': 'Description'
        }
    ))
    bussiness_area = forms.ChoiceField(choices=(('1', 'Architecture Office'), ('2', 'Design Office/Agency'),), widget=forms.Select(
        attrs={
            'class': 'form-control'
        }
    ))
    year_of_foundation = forms.ChoiceField(required=True, choices=YEAR_CHOICES, widget=forms.Select(
        attrs={
            'class': 'form-control'
        }))
    lat = forms.DecimalField(max_digits=9, decimal_places=6, required=True, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Latitude'
        }
    ))
    lon = forms.DecimalField(max_digits=9, decimal_places=6, required=True, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Longitude'
        }))
    is_more_than_5 = forms.BooleanField(required=False)

    def clean(self):
        print('in clean', self.data)
        username = self.cleaned_data['username']
        company_name = self.cleaned_data['company_name']
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        # profile_image = self.cleaned_data['profile_image']
        address_line1 = self.cleaned_data['address_line1']
        address_line2 = self.cleaned_data['address_line2']
        address_line3 = self.cleaned_data['address_line3']
        description = self.cleaned_data['description']
        bussiness_area = self.cleaned_data['bussiness_area']
        year_of_foundation = self.cleaned_data['year_of_foundation']
        lat = self.cleaned_data['lat']
        lon = self.cleaned_data['lon']

        if not password:
            raise forms.ValidationError('This password is also required')
        if password == '' or len(password) < 8:
            raise forms.ValidationError('please provide valid password')

        if not password:
            raise forms.ValidationError('This confirm password is also required')
        if password == '' or len(password) < 8:
            raise forms.ValidationError('please provide valid confirm password')

        if password != confirm_password:
            raise forms.ValidationError('password and confirm password must be same')

        if bussiness_area not in ['1', '2']:
            raise forms.ValidationError('Incorrect business area')

        if not username:
            raise forms.ValidationError('please provide username')
        if username == '':
            raise forms.ValidationError('Incorrect username')

        if User.objects.filter(username=username).first():
            raise forms.ValidationError('Username already taken')

        if not company_name:
            raise forms.ValidationError('please provide company name')
        if company_name == '':
            raise forms.ValidationError('Incorrect company_name')

        if not address_line1:
            raise forms.ValidationError('please provide address line 1')
        if address_line1 == '':
            raise forms.ValidationError('Incorrect address line 1')

        if not address_line2:
            raise forms.ValidationError('please provide address line 2')
        if address_line2 == '':
            raise forms.ValidationError('Incorrect address line 2')

        if not address_line3:
            raise forms.ValidationError('please provide address line 3')
        if address_line3 == '':
            raise forms.ValidationError('Incorrect address line 3')

        if not description:
            raise forms.ValidationError('please provide desciption')
        if description == '':
            raise forms.ValidationError('description cant be blank')

        if not year_of_foundation:
            raise forms.ValidationError('Please provide year of foundation')
        try:
            if year_of_foundation == '' or int(year_of_foundation) > date.today().year:
                raise forms.ValidationError('Incorrect year of foundation')
        except:
            raise forms.ValidationError('incorrect year of foundation')

        if not lat:
            raise forms.ValidationError('please provide latitude')
        try:
            if int(lat) and int(lat) < 0:
                raise forms.ValidationError('Incorrect lat')
        except:
            raise forms.ValidationError('Incorrect lat')

        if not lon:
            raise forms.ValidationError('please provide lon')
        try:
            if int(lon) and int(lon) < 0:
                raise forms.ValidationError('incorrect lon')
        except:
            raise forms.ValidationError('Incorrect lon')

        return self.cleaned_data
