from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('find-mentor/', views.find_mentor, name='find_mentor'),
    path('request-mentorship/<int:mentor_id>/', views.request_mentorship, name='request_mentorship'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('create-group/', views.create_group, name='create_group'),
    path('request-join/<int:group_id>/', views.request_join_group, name='request_join_group'),
    path('manage-requests/<int:group_id>/', views.manage_group_requests, name='manage_group_requests'),
    path('rate-mentor/<int:mentorship_id>/', views.rate_mentor, name='rate_mentor'),
    path('become-mentor/', views.become_mentor, name='become_mentor'),
    path('mentor-dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('community-feed/', views.community_feed, name='community_feed'),
    path('group/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('post/<int:post_id>/comments/', views.post_comments, name='post_comments'),
]