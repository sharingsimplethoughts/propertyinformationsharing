from django.urls import path
from django.conf.urls import url
from .views import *
app_name='posts-api'


urlpatterns=[
    path('project_type_list',ProjectTypeListView.as_view(),name='project_type_list'),
    path('project_category_list',ProjectCategoryListView.as_view(),name='project_category_list'),
    path('create',CreatePostView.as_view(),name='create'),
    path('filter_post_list',FilterPostListView.as_view(),name='filter_project_list'),
    path('get_tag_list', GetTagListView.as_view(), name='tag_list'),
    path('get_users_list_for_tag', GetUsersListView.as_view(), name='user_list'),
    path('get_home_page_data', PostListView.as_view(), name='get_post_by_list_view'),
    path('filter_list_data', FilterListDateView.as_view(), name='filter_list'),

    #---------- new
    url(r'my_projects/(?P<username>[a-zA-Z0-9]+)$',MyProjectsPostDetailView.as_view(),name='get_my_projects'),
    path('remove_post', RemovePostAPIView.as_view(), name='remove_post'),
    url(r'edit_post/(?P<post_id>[0-9]+)$', EditPostView.as_view(), name='edit_post'),
    path('search_post', SearchPostView.as_view(), name='search_post'),
    #---------- end

    path('project_post_detail/<str:post_id>', PostDetailView.as_view(), name='project_post_detail'),
    path('mark_involvement', MarkInvolvementView.as_view(), name='project_post_detail'),

    path('like_a_post', LikePostAPIView.as_view(), name="like_post"),
    path('comment_on_post', CommentOnPostAPIView.as_view(), name="comment_post"),
    path('like_a_comment', LikeACommentPostAPIView.as_view(), name="like_comment"),
    path('report_a_post', ReportAPostAPIView.as_view(), name="report post"),

]
