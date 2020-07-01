from django.db.models import Q

from post_invitations.models import InvitationPost
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()
from accounts.middleware import ValidateJWTToken

# -------- new
from PropInfoShare.settings import POST_ALL_PARAMS, REMOTE_BASE_URL, BASE_URL
from common_method.celery_tasks import send_mail_shared
from django.urls import resolve
from django.template.loader import render_to_string
from PropInfoShare.settings import REMOTE_BASE_URL
from django.core import mail
# -------- end

from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from accounts.models import *
from posts.models import *
import logging
from django.db.models import Q, F
from common_method.validators import get_error

logger = logging.getLogger('accounts')
from questions.models import Question

from invitations.utils import get_invitation_model
#signal process
from PropInfoShare.signals import new_notification, admin_notification


class ProjectTypeListView(APIView):

    def get(self, request, *args, **kwargs):
        queryset = ProjectType.objects.all().order_by('id')
        serializer = ProjectTypeListSerializer(queryset, many=True, context={'request': request})
        return Response({
            'message': 'Data retrieved successfully',
            'data': serializer.data
        }, status=200, )


class ProjectCategoryListView(APIView):

    def get(self, request, *args, **kwargs):
        queryset = ProjectCategory.objects.all().order_by('id')
        serializer = ProjectCategoryListSerializer(queryset, many=True, context={'request': request})
        return Response({
            'message': 'Data retrieved successfully',
            'data': serializer.data
        }, status=200, )


class SectorListView(APIView):

    def get(self, request, *args, **kwargs):
        queryset = Sector.objects.all()
        serializer = SectorListSerializer(queryset, many=True, context={'request': request})
        return Response({
            'message': 'Data retrieved successfully',
            'data': serializer.data
        }, status=200, )


class GetTagListView(APIView):
    def get(self, request):
        tag = request.GET.get('tag_name')
        tag_list = list(Tags.objects.filter(tag__startswith=tag).values('tag'))
        return Response({
            'message': 'success',
            'data': tag_list
        }, 200)


class GetUsersListView(APIView):
    """
    Get only registered user list for tag
    """

    def get(self, request):
        search_key = request.GET.get('name')
        user_qs = User.objects.filter(
            Q(first_name__icontains=search_key)
            | Q(email__icontains=search_key)
            | Q(username__icontains=search_key)
            & Q(is_profile_created=True)
        )
        data = GetUserListForTagSerializer(user_qs, many=True, context={'request': request}).data

        return Response({
            'message': 'success',
            'data': data
        }, 200)


# ------- search post
class SearchPostView(APIView):
    def get(self, request, *args, **kwargs):
        query_params = request.GET.get('q')
        if query_params:
            post_ids = PostOwner.objects.select_related('post_id', 'owner_id').filter(Q(owner_id__name__icontains=query_params)
                                                                           | Q(post_id__name__icontains=query_params)).\
                values_list('post_id', flat=True)
        else:
            post_ids = Post.objects.all().values_list('id', flat=True)
        return Response({
            'message': 'Data retrieved successfully',
            'success': 'True',
            'data': post_ids
        })
#------------- end


class CreatePostView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request, *args, **kwargs):
        logger.debug('Create post called')
        if request.user.profile_type != '2':
            logger.error('{} has profile_type {}, cant create posts'.format(request.user, request.user.profile_type))
            return Response({
                'message': 'Individual profiles cant create posts',
                'success': 'False'
            }, status=403, )
        data = request.data
        logger.debug(data)
        serializer = CreatePostSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data

            images = request.FILES.getlist('images')
            # image_tag = request.data.getlist('image_tag')
            if not images:
                return Response({
                    'message': 'please provide images'
                }, 400)

            # if len(image_tag)!=len(images):
            #     return Response({
            #         'message': 'Array length of image and image tag is not same'
            #     }, 400)
            post_obj = Post.objects.create(
                name=data['name'], project_type_id=data['project_type'], project_category_id=data['project_category'],
                year=data['year'], about_post=data['about_post'], lat=data['lat'], lon=data['lon'],
                country=data['country'], city=data['city'],
                zip_code=data['zip_code'], street=data['street'], created_by=request.user,
                t_type_start_date=serializer.data['t_type_start_date'],
                t_type_end_date=serializer.data['t_type_end_date']

            )
            if data['is_owner']:
                post_owner = User.objects.get(id=request.user.id)
                is_owner_joined = True
            elif data['is_owner_registered']:
                if str(request.user.id) == data['post_owner']:
                    raise APIException({'message': 'Please select is_owner as True'})
                try:
                    post_owner = User.objects.get(id=data['post_owner'], profile_type='2', is_active=True)
                    post_owner_company = Company.objects.get(user_id=post_owner, bussiness_area_id__in=['1', '2'])
                    is_owner_joined = True
                except Exception as e:
                    logger.error('Exception occurred in post_create {}'.format(str(e)))
                    raise APIException({'message': 'Please enter valid post_owner id'})
            else:
                post_owner = User.objects.get(id=request.user.id)
                print(data['post_owner'])
                Invitation = get_invitation_model()
                print(type(Invitation))
                invite = Invitation.create(data['post_owner'], inviter=request.user)
                print(invite)
                InvitationPost.objects.create(invitation_id=invite, post_id=post_obj)
                invite.send_invitation(request)
                is_owner_joined = False

            post_owner_obj = PostOwner.objects.create(post_id=post_obj, owner_id=post_owner,
                                                      owner_joined=is_owner_joined)

            # #get_or_create tags
            tag_objs = []
            tags = list(serializer.data.get('tags').split(','))
            for tag in tags:
                obj, created = Tags.objects.get_or_create(tag=tag)
                tag_objs.append(obj)
                if created:
                    obj.created_by = request.user
                    obj.save()

            # save tag to post
            post_obj.tags.add(*tag_objs)
            # save_images
            tags_list = list(data.get('image_tag').split(','))
            for i in range(len(images)):
                PostImages.objects.create(post=post_obj, image=images[i], image_tag=tags_list[i])
            # invite
            inv_link = REMOTE_BASE_URL + '/api/v1/posts/project_post_detail/' + str(post_obj.id)
            tagged_users = data['taged_users']
            for _ in tagged_users:
                if _ == "":
                    continue
                if not User.objects.filter(id=_).exists():
                    tagged_users.remove(_)
                    continue
                if _ == str(request.user.id):
                    tagged_users.remove(_)
            if request.user.profile_type == '2':
                name = Company.objects.get(user=request.user).name
            else:
                name = request.user.name
            if 'email_id' in data:
                email_ids = data['email_id']
                email_ids = [email_id for email_id in email_ids if email_id != ""]
                for email_id in email_ids:
                    if email_id == request.user.email:
                        continue
                    to = email_id
                    plain_message = None
                    from_email = 'Viewed <webmaster@localhost>'
                    subject = 'Invite Link for a post'
                    message_text = render_to_string('mails/send_invite_link.html', {
                        'invited_user': email_id.split('@')[0],
                        'user': name,
                        'post_id': post_obj.id,
                        'invite_link': inv_link
                    })
                    send_mail_shared.delay(subject, plain_message, from_email, [to], html_message=message_text)
            data = serializer.data
            context = {
                'notification_type': '4',
                'title': 'New Post',
                'body': post_obj.created_by.username + ' posted a new project near you',
                'id': post_obj.pk,
                'lat': post_obj.lat,
                'lon': post_obj.lon,
                'exclude_user_id': [post_obj.created_by.pk, ]
            }
            new_notification.send(sender=post_obj, context=context, sender_model_name="posts.{}".format(post_obj.__class__.__name__), sent_user_id=post_obj.created_by.pk)
            followers = FollowersAndFollowing.objects.filter(followed_to=post_obj.created_by).values_list('followed_by', flat=True)
            context = {
                'notification_type': '6',
                'title': 'New Post',
                'body': post_obj.created_by.username + ' posted a new project',
                'id': post_obj.pk,
                'user_id': list(followers),
            }
            new_notification.send(sender=post_obj, context=context, sender_model_name="posts.{}".format(post_obj.__class__.__name__), sent_user_id=post_obj.created_by.pk)
            return Response({
                'message': 'Post created successfully',
                'success': 'True',
                'data': data
            }, status=200, )

        return Response({'message': get_error(serializer)}, 400)


class PostListView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def get(self, request, *args, **kwargs):
        logger.debug('All post list post called')
        logger.debug(request.data)
        queryset = Post.objects.filter(is_active=True)
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        if serializer.data:
            return Response({
                'message': 'Data retrieved successfully',
                'success': 'True',
                'data': serializer.data,
            }, status=200, )
        return Response({
            'message': 'No data available',
            'success': 'False',
        }, status=400, )


def custom_filter(country, city_or_zip, project_type, category, year, material, element, queryset, **kwargs):
    if kwargs['sort_projects'] == 'true':
        user_qs = ProfileLiked.objects.filter(liked_by=kwargs['request'].user).values_list('user', flat=True)
        sort_project_qs = Post.objects.filter(created_by__in=user_qs)
    else:
        sort_project_qs = queryset

    if not country:
        country_qs = queryset
    else:
        country_qs = queryset.filter(country__iexact=country)
    if not city_or_zip:
        city_or_zip_qs = queryset
    else:
        city_or_zip_qs = queryset.filter(Q(city__iexact=city_or_zip) | Q(zip_code=city_or_zip))

    if not project_type:
        project_type_qs = queryset
    else:
        project_type_qs = queryset.filter(project_type__id=project_type)

    if not category:
        category_qs = queryset
    else:
        category_qs = queryset.filter(project_category__id=category)

    if not year:
        year_qs = queryset
    else:
        year_qs = queryset.filter(year=year)

    if not material:
        material_qs = queryset
    else:
        mark_qs = MarkInvolvement.objects.filter(keyword_for_material__icontains=material).values_list('post_id',
                                                                                                       flat=True)
        material_qs = Post.objects.filter(id__in=mark_qs)

    if not element:
        element_qs = queryset
    else:
        mark_qs = MarkInvolvement.objects.filter(keyword_for_element__icontains=element).values_list('post_id',
                                                                                                     flat=True)
        element_qs = Post.objects.filter(id__in=mark_qs)

    return (
            sort_project_qs & country_qs & city_or_zip_qs & project_type_qs & category_qs & year_qs & material_qs & element_qs).distinct()


class PostListView(APIView):

    # permission_classes = (IsAuthenticated, ValidateJWTToken,)
    # authentication_classes=[JSONWebTokenAuthentication,]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = FilterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            queryset = Post.objects.filter(is_active=True).order_by('-created_on')
            if (not request.user.is_authenticated) and ('sort_projects' in data or 'filter_projects' in data):
                raise APIException({'message': 'Please create profile to sort or filter object', 'success': 'False'})

            if not 'sort_projects' in data:
                filtered_qs = custom_filter(data['country'], data['city_or_zipcode'], data['project_type'],
                                            data['project_category'], data['year'], data.get('material'),
                                            data.get('element'), queryset, sort_projects='False')
            else:
                filtered_qs = custom_filter(data['country'], data['city_or_zipcode'], data['project_type'],
                                            data['project_category'], data['year'], data.get('material'),
                                            data.get('element'), queryset, request=request,
                                            sort_projects=data['sort_projects'])
            post_data = PostListSerializer(filtered_qs, many=True, context={'request': request}).data
            # get questions
            question_qs = Question.objects.filter(is_active=True)
            quest_data = QuestionListSerializer(question_qs, many=True, context={'request': request}).data
            if 'filter_projects' in data:
                if data['filter_projects'] == 'true':
                    latest_post = queryset.filter(
                        created_by__in=FollowersAndFollowing.objects.filter(followed_by=request.user).values_list(
                            'followed_to', flat=True))[:15]
                else:
                    latest_post = queryset[:15]
            else:
                latest_post = queryset[:15]
            latest_data = PostListSerializer(latest_post, many=True, context={'request': request}).data
            company = Company.objects.all().annotate(business_type=F('bussiness_area__subscription__id')).values('id',
                                                                                                                 'lat',
                                                                                                                 'lon',
                                                                                                                 'business_type',
                                                                                                                 'name',
                                                                                                                 'picture')

            data = {
                'posts': post_data,
                'questions': quest_data,
                'latest_post': latest_data,
                'business_pins': company
            }

            return Response({
                'data': data,
            }, status=200)
        return Response({
            'message': get_error(serializer)
        }, 400)


class FilterListDateView(APIView):
    def get(self, request):
        data = {}
        data['country'] = CountryCode.objects.all().values('country')
        data['project_type'] = ProjectType.objects.all().values('id', 'type')
        data['category'] = ProjectCategory.objects.all().values('id', 'category')
        return Response({
            'data': data
        }, 200)


class FilterPostListView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def post(self, request, *args, **kwargs):
        logger.debug('Filtered post list post called')
        logger.debug(request.data)
        serializer = FilterPostListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.data
            country = data['country']
            city = data['city']
            zipcode = data['zipcode']
            address = data['address']
            project_type = data['project_type']
            project_category = data['project_category']
            year = data['year']
            sector = data['sector']

            if project_type:
                proj_type = ProjectType.objects.filter(id=project_type).first()
            if project_category:
                proj_category = ProjectCategory.objects.filter(id=project_category).first()
            if sector:
                sector = Sector.objects.filter(id=sector).first()

            queryset = Post.objects.filter(is_active=True)
            if queryset:
                queryset = queryset.filter(
                    Q(country=country) |
                    Q(city=city) |
                    Q(zipcode=zipcode)
                ).distinct()
                if address:
                    queryset = queryset.filter(address__icontains=address).distinct()
                if year:
                    queryset = queryset.filter(year=year).distinct()
                if project_type:
                    queryset = queryset.filter(project_type=proj_type).distinct()
                if project_category:
                    queryset = queryset.filter(project_category=proj_category).distinct()
                if sector:
                    queryset = queryset.filter(sector=sector).distinct()

                serializer = PostListSerializer(queryset, many=True, context={'request': request})
                if serializer.data:
                    return Response({
                        'message': 'Data retrieved successfully',
                        'success': 'True',
                        'data': serializer.data
                    }, status=200, )
            return Response({
                'message': 'No data available',
                'success': 'False',
            }, status=400, )
        return Response({
            'message': 'Data retrieve failed',
            'success': 'False',
            'data': serializer.errors,
        }, status=400, )


class PostDetailView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication, ]

    def get(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except:
            raise serializers.ValidationError({'message': 'Invalid post id'})

        data = PostDetailSerializer(post, context={'request': request}).data
        return Response({
            'data': data
        }, 200)


class LikePostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        serilizer = LikePostSerilizer(data=data)

        if serilizer.is_valid():
            try:
                post = Post.objects.get(id=serilizer.validated_data['post_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid post_id'})
            else:
                if not serilizer.validated_data['is_liked']:
                    try:
                        post_likes = PostLikes.objects.get(post_id=post, liked_by=request.user)
                        post_likes.delete()

                        post.total_likes = F('total_likes') - 1
                        post.save()
                        if post.created_by.pk != request.user.id:
                            context = {
                                'notification_type': '3',
                                'title': 'Like on a post',
                                'body': request.user.username + ' removed like from your post',
                                'id': post.pk,
                                'user_id': [post.created_by.pk, ]
                            }
                            new_notification.send(sender=post, context=context, sender_model_name="posts.{}".format(post.__class__.__name__), sent_user_id=request.user.id)
                        return Response({
                            'message': 'Like Removed successfully',
                        }, 200)
                    except:
                        raise serializers.ValidationError({'message': 'first like this post'})

                obj, created = PostLikes.objects.get_or_create(post_id=post, liked_by=request.user)

                if created:
                    post.total_likes = F('total_likes') + 1
                    post.save()
                if post.created_by.pk != request.user.id:
                    context = {
                        'notification_type': '3',
                        'title': 'Like on a post',
                        'body': request.user.username + ' likes your post',
                        'id': post.pk,
                        'user_id': [post.created_by.pk, ]
                    }
                    new_notification.send(sender=post, context=context, sender_model_name="posts.{}".format(post.__class__.__name__), sent_user_id=request.user.id)
                return Response({
                    'message': 'Liked successfully',
                }, 200)
        return Response({
            'message': get_error(serilizer)
        }, 400)


class CommentOnPostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                post = Post.objects.get(id=request.data['post_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid post id'})

            serializer.save(comment_by=request.user, post_id=post)
            post.total_comments = F('total_comments') + 1
            post.save()
            if post.created_by.pk != request.user.id:
                context = {
                    'notification_type': '2',
                    'title': 'Comment on a post',
                    'body': request.user.username + ' commented on your post',
                    'id': post.pk,
                    'user_id': [post.created_by.pk, ]
                }
                new_notification.send(sender=post, context=context, sender_model_name="posts.{}".format(post.__class__.__name__), sent_user_id=request.user.id)
            return Response({
                'message': 'Commented successfully'
            }, 200)
        return Response({
            'message': get_error(serializer)
        }, 400)


class LikeACommentPostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = LikeCommentSerilizer(data=request.data)

        if serializer.is_valid():
            try:
                comment = Comments.objects.get(id=serializer.validated_data['comment_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid comment_id'})
            else:
                if not serializer.validated_data['is_liked']:
                    try:
                        comment_likes = CommentLike.objects.get(comment_id=comment, liked_by=request.user)
                        comment_likes.delete()
                        comment.total_like = F('total_like') - 1
                        comment.save()

                        return Response({
                            'message': 'Like Removed successfully',
                        }, 200)
                    except:
                        raise serializers.ValidationError({'message': 'first like this post'})

                obj, created = CommentLike.objects.get_or_create(comment_id=comment, liked_by=request.user)

                if created:
                    comment.total_like = F('total_like') + 1
                    comment.save()

                return Response({
                    'message': 'Liked successfully',
                }, 200)

        return Response({
            'message': get_error(serializer)
        }, 400)


class ReportAPostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = ReportACommentSerilizer(data=request.data)
        if serializer.is_valid():
            try:
                reason = ReportReasons.objects.get(id=request.data['reason_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid reason id'})

            try:
                post = Post.objects.get(id=serializer.validated_data['post_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid post id'})
            else:
                obj, created = ReportAPost.objects.get_or_create(post=post, user=request.user)
                if created:
                    post.total_reported = F('total_reported') + 1
                    post.save()

                obj.reason = reason
                obj.save()
                context = {
                    'title': 'New Report',
                    'body': '{} flagged {} post with post_id {}'.format(request.user.username, post.created_by.username, post.id)
                }
                admin_notification.send(sender=post, context=context, notification_by=request.user, notification_type='2',
                                        sender_model_name='posts.{}'.format(post.__class__.__name__))
                return Response({
                    'message': 'reported successfully'
                }, 200)
        raise serializers.ValidationError({'message': get_error(serializer)})


class MarkInvolvementView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = MarkInvolvementSerializer(data=data)
        if serializer.is_valid():

            try:
                post = Post.objects.get(id=data['post_id'])
            except:
                raise serializers.ValidationError({'message': 'Invalid post_id'})

            try:
                inv = InvolvementType.objects.get(id=data['involvement_type'])
            except:
                raise serializers.ValidationError({'message': 'Invalid involvement_type'})

            if not request.user.is_profile_created or request.user.profile_type == '1' or request.user.profile_type == '4':
                raise serializers.ValidationError(
                    {'message': 'Guest and individual profile is not eligible for mark involvement'})

            if request.user.profile_type == '2':  # company
                company = Company.objects.get(user=request.user)

            if request.user.profile_type == '3':
                company = request.user.colleague_company_id

            if not company.bussiness_area.subscription.mark_involvement_in_others_posts:
                return Response({
                    'message': 'You are not eligible for mark involvement'
                }, 400)

            # check subscription plan is active or not
            serializer.save(post_id=post, marked_by=request.user, involvement_type=inv)

            data = PostDetailSerializer(post, context={'request': request}).data
            context = {
                'notification_type': '1',
                'title': 'Involvement on a post',
                'body': request.user.username + ' marked involvement on your post',
                'id': post.pk,
                'user_id': [post.created_by.pk, ],
                'exclude_user_id': [request.user.id, ]
            }
            new_notification.send(sender=post, context=context, sender_model_name="posts.{}".format(post.__class__.__name__), sent_user_id=request.user.id)
            return Response({
                'message': 'Involvement marked successfully',
                'data': data
            }, 200)

        return Response({
            'message': get_error(serializer)
        }, 400)


# ------------ new method to get my projects
class MyProjectsPostDetailView(APIView):
    def get(self, request, *args, **kwargs):
        username = User.objects.filter(username=self.kwargs.get('username'))
        if not username.exists():
            raise serializers.ValidationError({'message': 'Invalid Username'})
        else:
            username = username[0]
            post = Post.objects.filter(Q(created_by=username) | Q(id__in=MarkInvolvement.objects
                                                                  .filter(marked_by=username).values_list('post_id', flat=True)))\
                .filter(is_active=True).order_by('-created_on')
            if not post.exists():
                return Response({
                    'message': 'No Posts by this user',
                    'success': 'True',
                }, status=200, )
            else:
                my_projects = PostListSerializer(post, many=True, context={'request': request})
                return Response({
                    'message': 'Data retrieved',
                    'data': my_projects.data,
                    'success': 'True'
                }, status=200, )
# ------------ end


# ------------ remove post
class RemovePostAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = RemovePostSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                post = Post.objects.get(id=serializer.validated_data['post_id'], is_active=True)
            except:
                raise serializers.ValidationError({'message': 'Invalid post_id'})
            if not post.created_by == request.user:
                raise APIException({'message': 'You can not delete someone else post'})
            post = Post.objects.get(id=post.id, created_by=request.user)
            if serializer.validated_data['sure_delete'] == True:
                post.is_active = False
                post.save()
                return Response({
                    'message': 'Post deleted successfully',
                    'success': "True"
                }, status=200, )
            else:
                raise serializers.ValidationError(
                    {'message': 'Please make sure you selected YES in confirmation dialog box'})
        else:
            return Response({'message': get_error(serializer)}, status=400, )


# --------- end


# ---------- edit post
class EditPostView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *arsg, **kwargs):
        data = request.data
        post = Post.objects.prefetch_related(None).filter(id=self.kwargs.get('post_id'), is_active=True,
                                                          created_by=request.user)
        if not post.exists():
            raise serializers.ValidationError({'message': 'Post doesnt exists or you havent created the post'})
        else:
            serializer = CreatePostSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                tag_objs = []
                tags = list(serializer.data.get('tags').split(','))
                previous_tags = post[0].tags.values_list('tag', flat=True)
                for _ in previous_tags:
                    if _ not in tags:
                        delObj = post[0].tags.get(tag=_)
                        post[0].tags.remove(delObj)
                for tag in tags:
                    obj, created = Tags.objects.get_or_create(tag=tag)
                    if created:
                        obj.created_by = request.user
                        obj.save()
                    tag_objs.append(obj)
                post[0].tags.add(*tag_objs)
                tags_list = list(data.get('image_tag').split(','))
                images = request.FILES.getlist('images')
                if images:
                    for i in range(len(images)):
                        img_obj, img_created = PostImages.objects.get_or_create(post=post[0], image=images[i],
                                                                                image_tag=tags_list[i])
                        if img_created:
                            img_obj.save()
                if 'deleted_images' in request.data and request.data['deleted_images'] != '':
                    deleted_images = list(data.get('deleted_images').split(','))
                    delImgs = PostImages.objects.filter(id__in=deleted_images, post=post[0])
                    delImgs.delete()

                my_dict = {}
                for _ in POST_ALL_PARAMS:
                    if _ in data.keys():
                        if _ == 'project_category':
                            ProjectCategory.objects.filter(category=_)
                        my_dict[_] = data[_]

                try:
                    post.update(**my_dict)
                except Exception as e:
                    raise serializers.ValidationError({'message': str(e)})
                return Response({
                    'message': 'Post updated successfully',
                    'success': 'True',
                    'data': serializer.data
                }, status=200, )
            else:
                raise serializers.ValidationError({'message': get_error(serializer)})
# ------- end
