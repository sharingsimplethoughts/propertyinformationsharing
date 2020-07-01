from django.db import models
from accounts.models import *
# Create your models here.
# from django.contrib.gis.db import models
from django.utils import timezone


class Sector(models.Model):
    name=models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.name


class ProjectType(models.Model):
    id = models.IntegerField(primary_key=True)
    type=models.CharField(max_length=100,blank=True,null=True)
    is_t_type = models.BooleanField(default=False)
    is_star_type = models.BooleanField(default=False)

    def __str__(self):
        return self.type


class ProjectCategory(models.Model):
    category=models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.category


class Tags(models.Model):
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,related_name='tag_created_by')
    tag = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag


class Post(models.Model):

    name = models.CharField(max_length=400,blank=True,null=True)
    project_type = models.ForeignKey(ProjectType, on_delete=models.CASCADE, related_name='p_project_type')
    project_category = models.ForeignKey(ProjectCategory, blank=True, null=True, on_delete=models.CASCADE, related_name='p_project_category')
    year = models.CharField(max_length=20,blank=True)
    tags = models.ManyToManyField(Tags, blank=True)
    about_post = models.TextField(blank=True, null=True)

    lat = models.CharField(max_length=50, blank=True, null=True)
    lon = models.CharField(max_length=50, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=100, blank=True)

    taged_users = models.ManyToManyField(User, blank=True, related_name='taged_users')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='p_created_by')
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    t_type_start_date = models.DateField(blank=True, null=True)
    t_type_end_date = models.DateField(blank=True, null=True)

    total_comments = models.PositiveSmallIntegerField(default=0)
    total_likes = models.PositiveSmallIntegerField(default=0)
    total_reported = models.PositiveSmallIntegerField(default=0)
    total_shares = models.PositiveSmallIntegerField(default=0)


    def __str__(self):
        return self.name + '--' + self.created_by.username

    def get_created_time(self):
        time = timezone.now()

        if self.created_on.day == time.day and self.created_on.month == time.month and self.created_on.year == time.year:
            if (time.hour - self.created_on.hour) == 0:
                minute = time.minute - self.created_on.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created_on.hour) + " hours ago"
        else:
            time_left = (time - self.created_on).days
            if time_left < 1:

                return str((time-self.created_on).seconds // 3600) + " hours ago"
            elif 1 <= time_left < 30:
                return str(time_left) + " days ago"
            elif 30 <= time_left < 365:
                return str(round(time_left / 30)) + " months ago"
            elif time_left >= 365:
                return str(round(time_left / 365)) + " years ago"
            else:
                return self.created_on


#------------ new model as per new requirements
class PostOwner(models.Model):
    post_id = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE, related_name='owner_post_id')
    owner_id = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='post_owner')
    owner_joined = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
#------------ end


class PostImages(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='post_images')
    image = models.ImageField(upload_to='post_img/')
    image_tag  =models.CharField(max_length=100,blank=True)

    def __int__(self):
        return self.post.id


class PostLikes(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_post_id')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_liked_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post_id', 'liked_by')


class Comments(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    total_like = models.PositiveSmallIntegerField(default=0)

    def get_created_time(self):
        time = timezone.now()

        if self.created.day == time.day and self.created.month == time.month and self.created.year == time.year:
            if (time.hour - self.created.hour) == 0:
                minute = time.minute - self.created.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created.hour) + " hours ago"
        else:
            time_left = (time - self.created).days
            if time_left < 1:
                return str((time -self.created).seconds // 3600) + " hours ago"
            elif 1 < time_left < 30:
                return str(time_left) + " days ago"
            elif 30 <= time_left < 365:
                return  str(round(time_left / 30)) + " months ago"
            elif time_left >= 365:
                return str(round(time_left / 365)) + " years ago"
            else:
                return self.created


class CommentLike(models.Model):
    comment_id = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name='comments_like')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_liked_user')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) +'-' + str(self.comment_id.id)

    class Meta:
        unique_together = ('comment_id', 'liked_by')


class ReportReasons(models.Model):
    reason = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class ReportAPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.ForeignKey(ReportReasons, blank=True, null=True,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


#------------- Flag classes
class PostFlagReasons(models.Model):
    reason = models.CharField(max_length=300)


class FlagPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='flaged_post')
    reason = models.ForeignKey(ProfileFlagReasons, on_delete=models.CASCADE, related_name='flaged_post_reason')
    flaged_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flaged_post_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'flaged_by', )
#----------- end

class InvolvementType(models.Model):
    type = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)


class MarkInvolvement(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='involvement_marked_id')
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_by')
    involvement_type = models.ForeignKey(InvolvementType, on_delete=models.CASCADE)
    keyword_for_element = models.CharField(max_length=500, blank=True)
    keyword_for_material = models.CharField(max_length=500, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='Involvement_images')
    enter_link = models.TextField(blank=True)



