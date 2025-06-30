from django.urls import path
from . import views

app_name = 'courses'  # Namespace for the courses app

urlpatterns = [
    # Course listing
    path('', views.courses_view, name='courses'),
    # Course enrollment
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    # Course details
    path('details/<int:course_id>/', views.course_details_view, name='course_details'),
    # Search courses
    path('search/', views.search_courses, name='search_courses'),
    # Instructor dashboard
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    # Add course
    path('instructor/add_course/', views.add_course, name='add_course'),
    # Edit course
    path('instructor/edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    # Add video
    path('instructor/add_video/<int:course_id>/', views.add_video, name='add_video'),
    # View course videos
    path('instructor/course_videos/<int:course_id>/', views.course_videos, name='course_videos'),
    # Edit video
    path('instructor/edit_video/<int:course_id>/<int:video_id>/', views.edit_video, name='edit_video'),
    # Check enrollment
    path('check_enrollment/<int:course_id>/', views.check_enrollment, name='check_enrollment'),
    # Watch video
    path('watch/<int:course_id>/<int:video_id>/', views.watch_video, name='watch_video'),
    # Rate video
    path('rate_video/<int:video_id>/', views.rate_video, name='rate_video'),
    # Add comment
    path('add_comment/<int:video_id>/', views.add_comment, name='add_comment'),
    # Update progress
    path('update_progress/<int:video_id>/', views.update_progress, name='update_progress'),
    # Download certificate
    path('certificate/<int:course_id>/', views.download_certificate, name='download_certificate'),
    # Get rating
    path('courses/get_rating/<int:video_id>/', views.get_rating, name='get_rating'),
    # Add task
    path('instructor/add_task/<int:course_id>/<int:video_id>/', views.add_task, name='add_task'),
    # Add alternative quiz
    path('instructor/add_alternative_quiz/<int:course_id>/<int:video_id>/', views.add_alternative_quiz, name='add_alternative_quiz'),
]