from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([Post,ProjectCategory,ReportAPost,MarkInvolvement,ProjectType,ReportReasons,InvolvementType, Tags,PostLikes,Comments,CommentLike, PostImages, FlagPost, PostFlagReasons, PostOwner])
