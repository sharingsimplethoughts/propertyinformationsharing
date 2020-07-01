from django.shortcuts import render

from django.views.generic import TemplateView#, DetailView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login ,logout
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy,reverse
from django.contrib.auth import views as auth_views
from accounts.api.password_reset_form import MyPasswordResetForm
from accounts.models import *
from .forms import *
from posts.models import Tags
# Create your views here.
import logging
logger = logging.getLogger('accounts')


class AdminHomeView(LoginRequiredMixin, TemplateView):
    login_url='ap_accounts:alogin'
    def get(self, request, *args, **kwargs):
        total_guest_users = len(User.objects.filter(profile_type='4', is_active=True).distinct('mobile_number'))
        total_registered_users = len(User.objects.all().exclude(profile_type='4', is_active=True))
        total_posts = len(Post.objects.filter(is_active=True))
        if total_guest_users > 1000:
            total_guest_users = '' + str(total_guest_users/1000) + 'K'
        if total_registered_users > 1000:
            total_registered_users = '' + str(total_registered_users/1000) + 'K'
        if total_posts > 1000:
            total_posts = '' + str(total_posts/1000) + 'K'
        return render(request, 'home/index.html', {'total_guest_users': total_guest_users,
                                                   'total_registered_users': total_registered_users,
                      'total_posts': total_posts})


class AdminLoginView(TemplateView):
    def get(self, request, *args, **kwargs):
        form = LoginForm
        if request.user.is_authenticated:
            login_user, created = LogInData.objects.get_or_create(user=request.user)
            login_user.logged_in = True
            login_user.last_login = datetime.datetime.now()
            login_user.save()
            return HttpResponseRedirect(reverse('ap_accounts:ahome'))
        return render(request, 'aaccounts/login.html', {'form': form})

    def post(self,request,*args,**kwargs):
        form = LoginForm(data=request.POST or None)
        print(form.errors)
        if form.is_valid():
            em=request.POST['email']
            user_qs= User.objects.get(email=em, is_active=True, is_staff=True, is_superuser=True)
            if not request.POST.getlist('rememberChkBox'):
                request.session.set_expiry(0)
            login(request,user_qs,backend='django.contrib.auth.backends.ModelBackend')
            response = HttpResponseRedirect(reverse('ap_accounts:ahome'))
            # response.set_cookie['role_admin']
            response.set_cookie(key='id', value=1)
            jwt_token = JWTTokenRecords.objects.filter(user=user_qs)
            response.set_cookie(key='JWT', value=jwt_token[0].token)
            login_user, created = LogInData.objects.get_or_create(user=request.user)
            login_user.logged_in = True
            login_user.last_login = datetime.datetime.now()
            login_user.save()
            return response
        return render(request,'aaccounts/login.html', {'form':form})


class AdminLogoutView(LoginRequiredMixin, TemplateView):
    login_url='ap_accounts:alogin'
    def get(self, request):
        login_user, created = LogInData.objects.get_or_create(user=request.user)
        login_user.logged_in = False
        login_user.last_logout = datetime.datetime.now()
        login_user.save()
        logout(request)
        response = HttpResponseRedirect(reverse('ap_accounts:ahome'))
        response.delete_cookie(key='id')
        return response


class ResetPasswordView(auth_views.PasswordResetView):
    form_class = MyPasswordResetForm


class ChangePasswordView(LoginRequiredMixin,TemplateView):
    login_url='ap_accounts:alogin'
    def get(self,request):
        form = ChangePasswordForm(user=request.user)
        return render(request, 'aaccounts/change-password.html',{'form': form})

    def post(self,request):
        user = request.user
        form = ChangePasswordForm(request.POST or None, user=request.user)

        if form.is_valid():
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            return HttpResponseRedirect(reverse('ap_accounts:alogin'))
        return render(request, 'aaccounts/change-password.html',{'form': form})


class AdminProfileView(LoginRequiredMixin, TemplateView):
    login_url='ap_accounts:alogin'
    def get(self, request, *args, **kwargs):
        form=AdminProfileEditForm
        print(request.user)
        context={}
        user=request.user
        context['email']=user.email
        context['name']=user.name
        context['mobile']=str(user.mobile_number)
        context['profile_image']=user.profile_image
        context['cover_image']=user.cover_image
        context['about']=user.about

        return render(request,'aaccounts/profile.html',context)


class AdminProfileEditView(LoginRequiredMixin, TemplateView):
    login_url='ap_accounts:alogin'
    def get(self,request,*args,**kwargs):
        print('inside get')
        form=AdminProfileEditForm
        print(request.user)
        context={}
        user=request.user
        context['email']=user.email
        context['name']=user.name
        context['mobile']=''
        if user.mobile_number:
            context['mobile']=str(user.mobile_number)
        if user.profile_image:
            context['profile_image']=user.profile_image
        if user.cover_image:
            context['cover_image']=user.cover_image
        context['about']=user.about

        return render(request,'aaccounts/edit-profile.html',context)

    def post(self,request,*args,**kwargs):
        print('inside post')
        user=request.user

        context={}
        context['email']=user.email
        context['name']=user.name
        context['mobile']=''
        if user.mobile_number:
            context['mobile']=str(user.mobile_number)
        if user.profile_image:
            context['profile_image']=user.profile_image
        if user.cover_image:
            context['cover_image']=user.cover_image
        context['about']=user.about

        form=AdminProfileEditForm(data=request.POST or None, user=request.user)
        if form.is_valid():
            print('inside post valid form')
            print(request.POST)
            print(request.FILES)
            name=request.POST['name']
            email=request.POST['email']
            mobile=request.POST['mobile']
            profile_image=request.FILES.get('profileimg')
            cover_image=request.FILES.get('coverimg')
            about=request.POST['about']

            user.email=email
            user.name=name
            user.first_name=name.split(' ')[0]
            user.country_code='+49'
            user.mobile_number=mobile
            user.email=email
            if profile_image:
                user.profile_image=profile_image
            if cover_image:
                user.cover_image=cover_image
            user.about=about
            user.save()

            return HttpResponseRedirect(reverse('ap_accounts:aprofile'))

        print(form.errors)
        return render(request,'aaccounts/edit-profile.html',{'context':context,'form':form})


class TagManagementView(LoginRequiredMixin, TemplateView):

    def get(self,request,*args,**kwargs):
        sort_by = request.GET.get('sort_by')
        if sort_by=='0':# admin
            tag_list = Tags.objects.filter(created_by__is_superuser=True).order_by('-created_on')
        elif sort_by=='1': #users
            tag_list = Tags.objects.filter(created_by__is_superuser=False).order_by('-created_on')
        else: #all
            tag_list = Tags.objects.all().order_by('-created_on')

        return render(request, 'tag_management/tag_list.html', context={'tag_list':tag_list,'sort_by': sort_by})


from posts.models import *
import datetime
from questions.models import Question


class PostListView(LoginRequiredMixin, TemplateView):

    def get(self,request):
        filter_by_project = request.GET.get('sort_by_project','0')
        filter_by_category = request.GET.get('sort_by_category','0')
        start_date = request.GET.get('start_date','')
        end_date =request.GET.get('end_date','')
        post_type = request.GET.get('post_type')

        if post_type=='1': #for question type
            posts = Question.objects.all().order_by('-created_on')

        else: #project type post

            if filter_by_project!='0' and filter_by_category!='0':

                posts =  Post.objects.filter(project_category__id=filter_by_category,project_type__id=filter_by_project).order_by('-created_on')


            elif filter_by_project=='0' and filter_by_category !='0':
                posts =  Post.objects.filter(project_category__id=filter_by_category).order_by('-created_on')

            elif filter_by_project!='0' and filter_by_category =='0':
                posts =  Post.objects.filter(project_type__id=filter_by_project).order_by('-created_on')
            else:
                posts =  Post.objects.all().order_by('-created_on')


        if start_date and end_date:
            startdate = datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            enddate = datetime.datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d') + ' 23:59:59'
            posts = posts.filter(created_on__range=(startdate, enddate))

        if post_type=='1':
            return render(request, 'post_management/question_post_list.html',
                          context={
                              'posts':posts,
                              'start_date':start_date,
                              'end_date':end_date,
                              'post_type':post_type
                          })
        else:
            projects = ProjectType.objects.all().values('id', 'type').order_by('id')
            categories = ProjectCategory.objects.all().values('id','category').order_by('id')

            return render(request, 'post_management/post_list.html',
                          context={
                              'posts': posts,
                              'start_date': start_date,
                              'end_date': end_date,
                              'post_type': post_type,
                              'sort_by_category': filter_by_category,
                              'sort_by_project': filter_by_project,
                              'projects': projects,
                              'categories': categories
                          })


class PostDetailView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        post = Post.objects.prefetch_related('tags').get(id=self.kwargs.get('post_id'))
        post_imgs = PostImages.objects.filter(post=post)

        return render(request, 'post_management/post_detail.html', context={'post':post,'post_imgs':post_imgs})


#--------------- report management
class ReportListView(LoginRequiredMixin, TemplateView):

    def get(self,request):
        post_type = request.GET.get('post_type')
        if post_type == '2': #for User type
            reported_users = ReportProfile.objects.all().order_by('-created')
            return render(request, 'report_management/report_users_list.html',
                context={
                    'reported_users':reported_users,
                    'post_type':post_type
                })

        else: #project type post
            reported_posts =  ReportAPost.objects.all().order_by('-created')
            return render(request, 'report_management/report_posts_list.html',
                context={
                    'reported_posts': reported_posts,
                    'post_type': post_type,
                })


class ReportDetailView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('post_type') == '2':
            user = User.objects.get(id=self.kwargs.get('post_id'))
            return render(request, 'report_management/report_user_detail.html', context={'fetched_user':user})
        
        post = Post.objects.prefetch_related('tags').get(id=self.kwargs.get('post_id'))
        post_imgs = PostImages.objects.filter(post=post)
        return render(request, 'report_management/report_post_detail.html', context={'post':post,'post_imgs':post_imgs})   
#----------- end


#--------------- flag management
class FlagListView(LoginRequiredMixin, TemplateView):

    def get(self,request):
        post_type = request.GET.get('post_type')
        if post_type == '2': #for User type
            flaged_users = FlagProfile.objects.all().order_by('-created')
            return render(request, 'flag_management/flag_users_list.html',
                context={
                    'flaged_users':flaged_users,
                    'post_type':post_type
                })

        else: #project type post
            flaged_posts =  FlagPost.objects.all().order_by('-created')
            return render(request, 'flag_management/flag_posts_list.html',
                context={
                    'flaged_posts': flaged_posts,
                    'post_type': post_type,
                })


class FlagDetailView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('post_type') == '2':
            user = User.objects.get(id=self.kwargs.get('post_id'))
            return render(request, 'flag_management/flag_user_detail.html', context={'fetched_user':user})
        
        post = Post.objects.prefetch_related('tags').get(id=self.kwargs.get('post_id'))
        post_imgs = PostImages.objects.filter(post=post)
        return render(request, 'flag_management/flag_post_detail.html', context={'post':post,'post_imgs':post_imgs})   
#----------- end


from django.db.models import Q
class UserManagementView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date','')
        end_date =request.GET.get('end_date','')
        user_type = request.GET.get('user_type','0')

        if user_type=='0':
            users = User.objects.filter(~Q(is_superuser=True)).order_by('-date_joined')
        else:
            users = User.objects.filter(~Q(is_superuser=True), Q(profile_type=user_type)).order_by('-date_joined')

        if start_date and end_date:
            startdate = datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            enddate = datetime.datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d') + ' 23:59:59'
            users = users.filter(date_joined__range=(startdate, enddate))

        for user in users:
            if user.profile_type=='2':
                try:
                    company = Company.objects.get(user=user)
                except Exception as e:
                    logger.error('in accounts management exception {} for {}'.format(str(e), user.email))
                user.company=company.name
            elif user.profile_type=='3':
                user.company = user.colleague_company_id.name
            else:
                user.company =''

        return render(request, 'user_management/user_list.html', context={'users':users, 'user_type':user_type,'start_date':start_date,
                              'end_date':end_date,})


from payment.models import PaymentHistory
class PaymentManagementView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date','')
        end_date =request.GET.get('end_date','')
        payments = PaymentHistory.objects.all().order_by('-created')

        if start_date and end_date:
            startdate = datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            enddate = datetime.datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d') + ' 23:59:59'
            payments = payments.filter(created__range=(startdate, enddate))

        # for payment in payments:
        #     if payment.user is not None:
        #         if payment.user.profile_type=='2':
        #
        #             company = Company.objects.get(user=payment.user)
        #             payment.user.company=company.name
        #     else:
        #         payment.company=''


        return render(request, 'payment_management/payment.html', context={'payments':payments, 'start_date':start_date,
                              'end_date':end_date,})

