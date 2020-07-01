from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
import datetime
import pytz
from django.db.models import Q

from extra.models import *
from .forms import *

class SettingsManagementListView(TemplateView):
    def get(self,request,*args,**kwargs):
        return render(request,'settings_management/settings.html')

class SettingsManagementAboutUsView(TemplateView):
    def get(self, request, *args,**kwargs):
        about_us = AboutUS.objects.all().first()
        return render(request,'settings_management/view/about-us.html',{'about_us':about_us})

class SettingsManagementFaqView(TemplateView):
    def get(self, request, *args,**kwargs):
        faqs=Faq.objects.all()
        return render(request,'settings_management/view/faq.html',{'faqs':faqs})
class SettingsManagementPrivacyPolicyView(TemplateView):
    def get(self,request,*args,**kwargs):
        ppolicy=PrivacyPolicy.objects.all().first()
        print(ppolicy)
        return render(request,'settings_management/view/privacy-policy.html',{'ppolicy':ppolicy})
class SettingsManagementTermsAndConditionView(TemplateView):
    def get(self,request,*args,**kwargs):
        tacond=TermsAndCondition.objects.all().first()
        return render(request,'settings_management/view/terms-conditions.html',{'tacond':tacond})

class SettingsManagementFaqEditView(TemplateView):
    def get(self,request,*args,**kwargs):
        faqs=Faq.objects.all()
        print(faqs)
        return render(request,'settings_management/edit/faq.html',{'faqs':faqs})
    def post(self,request,*args,**kwargs):
        title=request.POST['title']
        content=request.POST['content']
        f = Faq(
            question=title,
            answer=content,
        )
        f.save()
        faqs=Faq.objects.all()
        return render(request,'settings_management/edit/faq.html',{'faqs':faqs})

class SettingsManagementEditView(View):
    def get(self,request,*args,**kwargs):
        id=self.kwargs['id']
        context=''
        if id=='f1':
            context=TermsAndCondition.objects.all().first()
        elif id=='f2':
            context=PrivacyPolicy.objects.all().first()
        elif id == 'f3':
            context = AboutUS.objects.all()
        else:
            context=Faq.objects.filter(id=id).first()
            print(context)
        return render(request,'settings_management/edit/settings_common_edit.html',{'context':context,'id':id})

    def post(self,request,*args,**kwargs):
        id=self.kwargs['id']
        # servicetitle=request.POST['servicetitle']
        # servicedesc=request.POST['servicedesc'].strip()
        form=SettingsManagementEditForm(request.POST or None)
        obj=''
        succ_messages=''
        if form.is_valid():            
            if id=='f1':
                obj=TermsAndCondition.objects.all().first()
                if obj:
                    obj.content=form.cleaned_data['servicedesc']
                    obj.save()
                else:
                    obj = TermsAndCondition.objects.create(title='1', content=form.cleaned_data['servicedesc'])
                obj=TermsAndCondition.objects.all().first()            
            elif id=='f2':
                obj=PrivacyPolicy.objects.all().first()
                print(obj)
                if obj:
                    obj.content=form.cleaned_data['servicedesc']
                    obj.save()
                else:
                    obj  = PrivacyPolicy.objects.create(title='1', content=form.cleaned_data['servicedesc'])
                obj=PrivacyPolicy.objects.all().first()
            elif id == 'f3':
                obj = AboutUS.objects.all().first()
                print(obj)
                if obj:
                    obj.content = form.cleaned_data['servicedesc']
                    obj.save()
                else:
                    obj = AboutUS.objects.create(key='1', content=form.cleaned_data['servicedesc'])
                obj = AboutUS.objects.all().first()
            else:
                obj=Faq.objects.filter(id=id).first()
                if obj:
                    obj.answer=form.cleaned_data['content']
                    obj.save()
                else:
                    obj = Faq.objects.create(question=form.cleaned_data['title'], answer=form.cleaned_data['content'])
                obj=Faq.objects.filter(id=id).first()
            
            succ_messages='Settings edited successfully'

        return render(request,'settings_management/edit/settings_common_edit.html',{'context':obj,'id':id,'succ_messages':succ_messages,'form':form})
