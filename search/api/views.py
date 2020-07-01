# from django.db.models import Q
# from rest_framework.filters import (SearchFilter,OrderingFilter,)
# from rest_framework.views import (APIView)
# from django.views.generic import TemplateView
# from rest_framework.permissions import (AllowAny,IsAuthenticated,)
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
# from datetime import datetime
# from django.utils.timezone import utc
# from datetime import date
# from accounts.middleware import ValidateJWTToken

# from posts.api.serializers import *
# from rest_framework import generics

# import logging
# logger = logging.getLogger('accounts')


# # class HomeScreenSearchView(APIView):
# #     def get(self,request,*args,**kwargs):
# #         permission_classes = (IsAuthenticated,)
# #         authentication_classes = (JSONWebTokenAuthentication,)
# #         # serializer_class = GarageListSerializer
# #         serializer_class = PostListSerializer
# #         filter_backends = (SearchFilter,OrderingFilter,)
# #         # search_fields = ['slug1','slug2','state','city','country','service_type','service_subtype',]
# #         filterset_fields = ['created_by', 'username']

# #     def get_queryset(self,request,*args,**kwargs):
# #         # if request.user:
# #         #     user = request.User
# #         #     User.objects.filter()
# #         sort_project = self.request.GET.get('sort_project', None)
# #         filter_project = self.request.GET.get('filter_project', None)
# #         # city=ruser.city
# #         # queryset_list=Garage.objects.filter(city=city)## find most popular garages here
# #         # query=self.request.GET.get('q',None)

# #         print('----------------')
# #         print(sort_project, filter_project)
# #     #     st=ServiceType.objects.filter(slug__icontains=query)
# #     #     sst=ServiceSubType.objects.filter(slug__icontains=query)
# #     #     vmt=ServiceSubType.objects.filter(slug__icontains=query)
# #     #     if query:
# #     #         queryset_list=queryset_list.filter(
# #     #             Q(name__icontains=query)|
# #     #             Q(location__icontains=query)|
# #     #             Q(state__icontains=query)|
# #     #             Q(city__icontains=query)|
# #     #             Q(country__icontains=query)|
# #     #             Q(service_type__in=(st))|
# #     #             Q(service_subtype__in=(sst))|
# #     #             Q(vehicle_model__in=(vmt))
# #     #         ).distinct()
# #         return queryset_list
# #     def list(self,request,*args,**kwargs):
# #         logger.debug('home search list called')
# #         logger.debug(self.request.data)
# #         print(request)
# #         qs=self.get_queryset(request)
# #         print('qs', qs)
# #         # data=GarageListSerializer(qs,many=True,context={'request':self.request}).data
# #         # for obj in data:
# #         #     if obj['is_favorite']=='True':
# #         #         obj['make_fav_garage_url']=''
# #         #     else:
# #         #         obj['remove_fav_garage_url']=''
# #         return Response({
# #             'message':'data retrieved successfully',
# #             'success':'True',
# #             # 'data':data,
# #         },status=HTTP_200_OK,)


# class HomeScreenSortProjectView(generics.ListAPIView):
#     permission_classes = (IsAuthenticated, ValidateJWTToken,)
#     authentication_classes = [JSONWebTokenAuthentication,]
#     serializer_class = PostListSerializer

#     def get_queryset(self):
#         sort_project = self.request.query_params.get('sort_project', None)
#         fetched_posts_list = []
#         if sort_project == 'True':
#             liked_users = ProfileLiked.objects.filter(liked_by=self.request.user)
#             for user in liked_users:
#                 for post in Post.objects.filter(created_by=user.liked_by):
#                     fetched_posts_list.append(post)
#             return fetched_posts_list
#         else:
#             return Post.objects.all()
                

# class HomeScreenFilterProjectView(generics.ListAPIView):
#     permission_classes = (IsAuthenticated, ValidateJWTToken,)
#     authentication_classes = [JSONWebTokenAuthentication,]
#     serializer_class = PostListSerializer

#     def get_queryset(self):
#         filter_project = self.request.query_params.get('filter_project', None)
#         fetched_posts_list = []
#         if filter_project == 'True':
#             liked_users = FollowersAndFollowing.objects.filter(followed_by=self.request.user)
#             for user in liked_users:
#                 for post in Post.objects.filter(created_by=user.followed_by, is_active=True).order_by('-created_on')[:15]:
#                     fetched_posts_list.append(post)
#             return fetched_posts_list
#         else:
#             return Post.objects.all()