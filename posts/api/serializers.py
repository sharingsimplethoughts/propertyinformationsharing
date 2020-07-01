from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from PropInfoShare.settings import REMOTE_BASE_URL
from rest_framework import serializers
from rest_framework.exceptions import APIException
import datetime
from accounts.models import *
from posts.models import *
from questions.models import Question
from django.db.models import Q,F

class FilterSerializer(serializers.Serializer):
    country = serializers.CharField(allow_blank=True, error_messages={'required': 'country key is required'})
    city_or_zipcode = serializers.CharField(allow_blank=True,error_messages={'required': 'city_or_zipcode is required'})
    project_type = serializers.CharField(allow_blank=True, error_messages={'required': 'project_type key is required'})
    project_category = serializers.CharField(allow_blank=True, error_messages={'required': 'project_category key is required'})
    year = serializers.CharField(allow_blank=True, error_messages={'required': 'year key is required'})


class ProjectTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProjectType
        fields='__all__'


class ProjectCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProjectCategory
        fields='__all__'


class SectorListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Sector
        fields='__all__'

class PostImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = [
            'image',
            'image_tag'
        ]


class GetUserListForTagSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        return instance.get_full_name()

    class Meta:
        model = User
        fields =[
            'id',
            'name',
            'username',
            'profile_image',
            'email'
        ]

def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except:
        raise serializers.ValidationError('incorrect data format, should be YYYY-MM-DD')



class CreatePostSerializer(serializers.Serializer):
    name=serializers.CharField(error_messages={'required': 'name key is required', 'blank':'name field is required'})

    project_type=serializers.CharField(error_messages={'required': 'project_type key is required', 'blank':'project_type field is required'})
    project_category=serializers.CharField(allow_blank=True, error_messages={'required': 'project_category key is required'})

    year=serializers.CharField(allow_blank=True, error_messages={'required': 'year key is required', 'blank':'year field is required'})
    tags=serializers.CharField(allow_blank=True, error_messages={'required': 'tag key is required'})
    about_post=serializers.CharField(error_messages={'required': 'about_post key is required', 'blank':'about_post field is required'})

    lat=serializers.CharField(error_messages={'required': 'lat key is required', 'blank':'lat field is required'})
    lon=serializers.CharField(error_messages={'required': 'lon key is required', 'blank':'lon field is required'})

    taged_users = serializers.ListField(allow_empty=True, error_messages={'required': 'taged_users key is required'})
    t_type_start_date = serializers.CharField(allow_null=True,  error_messages={'required': 't_type_start_date key is required'})
    t_type_end_date= serializers.CharField(allow_null=True,  error_messages={'required': 't_type_end_date key is required'})
    country = serializers.CharField(error_messages={'required': 'country key is required', 'blank':'country field is required'})
    city = serializers.CharField(error_messages={'required': 'city key is required', 'blank':'city field is required'})
    zip_code = serializers.CharField(allow_blank=True, error_messages={'required': 'zip_code key is required', 'blank':'zip_code field is required'})
    street = serializers.CharField(allow_blank=True, error_messages={'required': 'street key is required', 'blank':'street field is required'})

    #---------- new field
    email_id = serializers.ListField(allow_empty=True, required=False, child=serializers.EmailField(allow_blank=True))
    #----------- end

    #------- new requirement fields
    post_owner = serializers.CharField(allow_blank=True, required=False)
    is_owner = serializers.BooleanField(default=True)
    is_owner_registered = serializers.BooleanField(default=False)
    #--------- end

    # image_tag = serializers.ListField(allow_empty=True, error_messages={'required': 'image_tag key is required'})
    image_tag = serializers.CharField(allow_null=True, allow_blank=True, error_messages={'required': 'image_tag key is required'})

    def validate(self, data):
        project_type=data['project_type']
        project_category=data['project_category']

        if not data['is_owner']:
            if 'is_owner_registered' not in data:
                raise serializers.ValidationError({'message':'is_owner_registered is required, if is_owner key is False'})
            elif 'post_owner' not in data:
                raise serializers.ValidationError({'message':'post_owner key is required, if is_owner is False'})
            elif data['post_owner'] == "":
                raise serializers.ValidationError({'message':'post_owner field can not be blank, if is_owner is False'})

        if data.get('t_type_start_date')!=None:
            validate_date(data.get('t_type_start_date'))

        if data.get('t_type_end_date')!=None:
            validate_date(data.get('t_type_end_date'))

        if project_category:
            proj_cat=ProjectCategory.objects.filter(id=project_category).first()
            if not proj_cat:
                raise APIException({
                    'message':'Project category is not valid',
                })

        proj_type=ProjectType.objects.filter(id=project_type).first()
        if not proj_type:
            raise APIException({
                'message':'Project type in not valid',
            })

        if proj_type.is_star_type:
            if project_category=="":
                raise serializers.ValidationError('Project category is required')
            if not proj_type.is_t_type and data['year']=="":
                raise serializers.ValidationError('Year is required')
            if proj_type.is_t_type and  (data['t_type_start_date']==None or data['t_type_end_date']==None):
                raise serializers.ValidationError('Start date and end date is required')

        elif proj_type.is_t_type and (data['t_type_start_date'] == None or data['t_type_end_date'] == None):
            raise serializers.ValidationError('Start date and end date is required')

        elif not proj_type.is_star_type and not proj_type.is_t_type and data['year']=="":
            raise serializers.ValidationError('year is required')


        return data


class ProjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = '__all__'

class PostListSerializer(serializers.ModelSerializer):
    post_image = serializers.SerializerMethodField()
    project_type = serializers.SerializerMethodField()
    project_category  = serializers.SerializerMethodField()
    #---------- new  created-by is owner id
    created_by = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    def get_current_owner(self, instance):
        return PostOwner.objects.select_related('owner_id', 'post_id').get(post_id=instance)

    def get_created_by(self, instance):
        return instance.created_by.username

    def get_created_by_name(self, instance):
        return Company.objects.get(user=instance.created_by).name if instance.created_by.profile_type == '2' else instance.created_by.name

    def get_post_image(self, instance):
        qs =  PostImages.objects.filter(post=instance)
        data = PostImagesSerializer(qs.first(), context={'request':self.context.get('request')}).data
        return data

    def get_project_type(self, instance):
        return ProjectTypeSerializer(instance.project_type).data

    def get_project_category(self, instance):
        if instance.project_category:
            return instance.project_category.category

    class Meta:
        model=Post
        fields= [
            'id',
            'name',
            'project_type',
            'project_category',
            'year',
            'lat',
            'lon',
            'country',
            'city',
            'post_image',
            'created_on',
            't_type_start_date',
            't_type_end_date',
            'created_by',
            'created_by_name'
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id',
            'lat',
            'lon'
        ]


class FilterPostListSerializer(serializers.ModelSerializer):
    country=serializers.CharField(allow_blank=True,allow_null=True)
    city=serializers.CharField(allow_blank=True,allow_null=True)
    zipcode=serializers.CharField(allow_blank=True,allow_null=True)
    address=serializers.CharField(allow_blank=True,allow_null=True)
    project_type=serializers.CharField(allow_blank=True,allow_null=True)
    project_category=serializers.CharField(allow_blank=True,allow_null=True)
    year=serializers.CharField(allow_blank=True,allow_null=True)
    sector=serializers.CharField(allow_blank=True,allow_null=True)

    class Meta:
        model=Post
        fields=('country','city','zipcode','address','project_type','project_category','year','sector')

    def validate(seld, data):
        country=data['country']
        city=data['city']
        zipcode=data['zipcode']
        address=data['address']
        project_type=data['project_type']
        project_category=data['project_category']
        year=data['year']
        sector=data['sector']

        if project_type:
            proj_obj=ProjectType.objects.filter(id=project_type).first()
            if not proj_obj:
                raise APIException({
                    'message':'Project type is not valid',
                    'success':'False'
                })
        if project_category:
            proj_cat=ProjectCategory.objects.filter(id=project_category).first()
            if not proj_cat:
                raise APIException({
                'message':'Project category is not valid',
                'success':'False'
                })
        if sector:
            sector=Sector.objects.filter(id=sector).first()
            if not sector:
                raise APIException({
                    'message':'Sector is not valid',
                    'success':'False'
                })
        return data

class PostImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = [
            'id',
            'image',
            'image_tag'
        ]


class UserPostDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    company_name =serializers.SerializerMethodField()

    def get_company_name(self, instance):
        if instance.profile_type == '2':
            comp = Company.objects.get(user=instance)
            return comp.name
        elif instance.profile_type=='3':
            return instance.colleague_company_id.name
        else:
            return ''

    def get_name(self, instance):
        if instance.profile_type=='4':
            return 'Guest'
        else:
            return instance.username

    def get_profile_image(self, instance):
        if instance.profile_type == '1':
            if instance.profile_image:
                return REMOTE_BASE_URL + instance.profile_image.url
            return ''
        elif instance.profile_type == '2':
            if instance.profile_image:
                return REMOTE_BASE_URL+ instance.profile_image.url
            return ''

        elif instance.profile_type == '3':
            if instance.colleague_company_id.picture:
                return REMOTE_BASE_URL+instance.colleague_company_id.picture.url
            return ''
        else:
            return ''

    class Meta:
        model = User
        fields = [
            'name',
            'profile_image',
            'company_name',
        ]


class CommentListSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comment_by = UserPostDetailSerializer()

    def get_is_liked(self, instance):
        qs = CommentLike.objects.filter(comment_id=instance, liked_by=self.context.get('request').user)
        if qs.exists():
            return True
        return False

    def get_created(self, instance):
        return instance.get_created_time()



    class Meta:
        model = Comments
        fields = [
            'id',
            'comment_by',
            'content',
            'total_like',
            'created',
            'is_liked'
        ]


class MarkInvolvementSerializerList(serializers.ModelSerializer):

    company_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_profile_image(self, instance):
        if instance.marked_by.profile_type=='3':
            if instance.marked_by.colleague_company_id.picture:
                return REMOTE_BASE_URL+ instance.marked_by.colleague_company_id.picture.url
            return ''
        else:
            obj = Company.objects.get(user=instance.marked_by)
            if obj.picture:
                return REMOTE_BASE_URL+obj.picture.url
            return ''

    def get_company_name(self, instance):
        if instance.marked_by.profile_type == '3':
            return instance.marked_by.colleague_company_id.name
        else:
            obj = Company.objects.get(user=instance.marked_by)
            return obj.name

    def get_name(self, instance):
        return instance.marked_by.username


    class Meta:
        model = MarkInvolvement
        fields = [
            'id',
            'involvement_type',
            'company_name',
            'profile_image',
            'name',
            'enter_link',
            'image'
        ]


#----------- tag serializer
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['tag', 'created_on']
#------------- end


class PostDetailSerializer(serializers.ModelSerializer):
    created_on = serializers.SerializerMethodField()
    project_type = ProjectTypeListSerializer()
    project_category = ProjectCategoryListSerializer()
    post_images = serializers.SerializerMethodField()
    is_reported = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()
    report_reasons = serializers.SerializerMethodField()
    involvements_types = serializers.SerializerMethodField()
    created_on_at = serializers.SerializerMethodField()
    #-------- new
    created_by = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_by_user = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()


    def get_created_on(self, instance):
        return instance.get_created_time()

    def get_created_on_at(self, instance):
        return instance.created_on

    def get_involvements_types(self, instance):
        return InvolvementType.objects.all().values('id', 'type')

    def get_report_reasons(self, instance):
        return ReportReasons.objects.all().values('id', 'reason')

    def get_is_liked(self, instance):
        qs = PostLikes.objects.filter(post_id=instance, liked_by=self.context.get('request').user)
        if qs.exists():
            return True
        return False

    def get_is_reported(self, instance):
        qs = ReportAPost.objects.filter(post_id=instance, user=self.context.get('request').user)
        if qs.exists():
            return True
        return False

    def get_comments(self, instance):
        qs = Comments.objects.filter(post_id=instance).order_by('-created')
        data = CommentListSerializer(qs, many=True, context={'request':self.context.get('request')}).data
        return data

    def get_involvements(self, instance):

        qs = MarkInvolvement.objects.filter(post_id=instance).order_by('-id')
        types = qs.values('involvement_type__type','involvement_type__id').order_by('involvement_type__id')
        data = {}
        for type in types:
            data[type['involvement_type__type']]=MarkInvolvementSerializerList(qs.filter(involvement_type__id=type['involvement_type__id']),many=True, context={'request':self.context.get('request')}).data

        return data

    def get_post_images(self, instance):
        qs = PostImages.objects.filter(post=instance)
        data = PostImagesSerializer(qs, many=True, context={'request':self.context.get('request')}).data
        return data

    #--------- new method
    def get_created_by_name(self, instance):
        if instance.created_by.colleague_company_id:
            return Company.objects.get(id=instance.created_by.colleague_company_id.id).name
        return instance.created_by.name

    def get_created_by(self, instance):
        return instance.created_by.username

    def get_created_by_user(self, instance):
        return True if self.context.get('request').user.id == instance.created_by.id else False

    def get_tags(self, instance):
        return TagSerializer(Post.objects.get(id=instance.id).tags.all(), many=True).data
    #-------- end

    class Meta:
        model = Post
        fields = [
            'id',
            'name',
            'project_type',
            'project_category',
            'year',
            'about_post',
            'lat',
            'lon',
            'city',
            'country',
            'zip_code',
            'street',
            'created_on',
            't_type_start_date',
            't_type_end_date',
            'total_comments',
            'total_likes',
            'total_reported',
            'total_shares',
            'post_images',
            'is_liked',
            'is_reported',
            'comments',
            'involvements',
            'report_reasons',
            'involvements_types',
            'created_on_at',
            'created_by',
            'created_by_user',
            'created_by_name',
            'tags'
        ]


class LikePostSerilizer(serializers.Serializer):
    post_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    is_liked = serializers.BooleanField(error_messages={'required': 'is_liked key is required', 'blank': 'is_liked is required'})


#--------- remove post serialize
class RemovePostSerializer(serializers.Serializer):
    post_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    sure_delete = serializers.BooleanField(error_messages={'required': 'sure_delete key is required', 'blank': 'sure_delete is required'})
#---------- end


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    content = serializers.CharField(error_messages={'required': 'content key is required', 'blank': 'content is required'})

    class Meta:
        model = Comments
        fields = [
            'post_id',
            'content',
        ]


class LikeCommentSerilizer(serializers.Serializer):
    comment_id = serializers.CharField(error_messages={'required': 'comment_id key is required', 'blank': 'comment_id is required'})
    is_liked = serializers.BooleanField(error_messages={'required': 'is_liked key is required', 'blank': 'is_liked is required'})


class ReportACommentSerilizer(serializers.Serializer):
    post_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    reason_id = serializers.CharField(error_messages={'required': 'reason_id key is required', 'blank': 'reason_id is required'})


class MarkInvolvementSerializer(serializers.ModelSerializer):
    post_id = serializers.CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    involvement_type = serializers.CharField(error_messages={'required': 'involvement_type key is required', 'blank': 'involvement_type is required'})
    keyword_for_element = serializers.CharField(error_messages={'required': 'keyword_for_element key is required', 'blank': 'keyword_for_element is required'})
    keyword_for_material = serializers.CharField(error_messages={'required': 'keyword_for_material key is required', 'blank': 'keyword_for_material is required'})
    enter_link = serializers.CharField(allow_blank=True,error_messages={'required': 'enter_link key is required', 'blank': 'enter_link is required'})

    class Meta:
        model = MarkInvolvement
        fields = [
            'post_id',
            'involvement_type',
            'keyword_for_element',
            'keyword_for_material',
            'image',
            'enter_link'
        ]