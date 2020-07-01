from django.urls import path

from .views import *

app_name='questions-api'

urlpatterns=[
    path('create',CreateQuestionView.as_view(),name='create'),
    path('question_detail/<str:question_id>', QuestionView.as_view(), name='view'),

    path('like_a_question_post', LikePostAPIView.as_view(), name="like_post"),
    path('comment_on_question_post', CommentOnPostAPIView.as_view(), name="comment_post"),
    path('like_a_question_comment', LikeACommentPostAPIView.as_view(), name="like_comment"),
    path('report_a_question_post', ReportAPostAPIView.as_view(), name="report post"),

]
