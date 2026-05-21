from django.urls import path, re_path
from . import views
from . import views_curriculum

app_name = 'courses'

urlpatterns = [
    path('', views.courses_view, name='courses'),
    path('search/', views.search_courses, name='search_courses'),

    # ─── Access Denied (403) ────────────────────────────────────────────────
    path('access-denied/', views.access_denied, name='access_denied'),

    path('enroll/<int:course_id>/<path:course_slug>/', views.enroll_course, name='enroll_course'),

    # Course details
    path('details/<int:course_id>/<path:course_slug>/', views.course_details_view, name='course_details'),
    path('details/<int:course_id>/', views.redirect_old_course_url, name='redirect_old_course_url'),

    # ── Legacy video paths (kept intact) ────────────────────────────────────
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/add_course/', views.add_course, name='add_course'),
    path('instructor/edit_course/<int:course_id>/<path:course_slug>/', views.edit_course, name='edit_course'),
    path('instructor/delete_course/<int:course_id>/<path:course_slug>/', views.delete_course, name='delete_course'),
    path('instructor/add_video/<int:course_id>/<path:course_slug>/', views.add_video, name='add_video'),
    path('instructor/course_videos/<int:course_id>/<path:course_slug>/', views.course_videos, name='course_videos'),
    path('instructor/edit_video/<int:course_id>/<path:course_slug>/<int:video_id>/<path:video_slug>/', views.edit_video, name='edit_video'),
    path('instructor/delete_video/<int:course_id>/<path:course_slug>/<int:video_id>/<path:video_slug>/', views.delete_video, name='delete_video'),
    path('check_enrollment/<int:course_id>/<path:course_slug>/', views.check_enrollment, name='check_enrollment'),
    path('watch/<int:course_id>/<path:course_slug>/<int:video_id>/<path:video_slug>/', views.watch_video, name='watch_video'),
    path('watch/<int:course_id>/<int:video_id>/', views.redirect_old_video_url, name='redirect_old_video_url'),
    path('rate_video/<int:video_id>/<path:video_slug>/', views.rate_video, name='rate_video'),
    path('add_comment/<int:video_id>/<path:video_slug>/', views.add_comment, name='add_comment'),
    path('update_progress/<int:video_id>/<path:video_slug>/', views.update_progress, name='update_progress'),
    path('certificate/<int:course_id>/<path:course_slug>/', views.download_certificate, name='download_certificate'),
    path('get_rating/<int:video_id>/<path:video_slug>/', views.get_rating, name='get_rating'),
    path('instructor/course_videos/<int:course_id>/<path:course_slug>/add_task/<int:video_id>/<path:video_slug>/', views.add_task, name='add_task'),
    path('instructor/add_alternative_quiz/<int:course_id>/<path:course_slug>/<int:video_id>/<path:video_slug>/', views.add_alternative_quiz, name='add_alternative_quiz'),

    # ════════════════════════════════════════════════════════════════════════
    # ── NEW CURRICULUM SYSTEM ────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    # Instructor — builder page
    path(
        'instructor/curriculum/<int:course_id>/<path:course_slug>/',
        views_curriculum.curriculum_builder,
        name='curriculum_builder',
    ),

    # Instructor — Section AJAX
    path('instructor/curriculum/<int:course_id>/section/create/',          views_curriculum.section_create,  name='section_create'),
    path('instructor/curriculum/<int:course_id>/section/<int:section_id>/update/', views_curriculum.section_update, name='section_update'),
    path('instructor/curriculum/<int:course_id>/section/<int:section_id>/delete/', views_curriculum.section_delete, name='section_delete'),
    path('instructor/curriculum/<int:course_id>/section/reorder/',         views_curriculum.section_reorder, name='section_reorder'),

    # Instructor — Lesson AJAX
    path('instructor/curriculum/<int:course_id>/section/<int:section_id>/lesson/create/', views_curriculum.lesson_create,  name='lesson_create'),
    path('instructor/curriculum/<int:course_id>/section/<int:section_id>/lesson/<int:lesson_id>/update/', views_curriculum.lesson_update, name='lesson_update'),
    path('instructor/curriculum/<int:course_id>/section/<int:section_id>/lesson/<int:lesson_id>/delete/', views_curriculum.lesson_delete, name='lesson_delete'),
    path('instructor/curriculum/<int:course_id>/section/<int:section_id>/lesson/reorder/', views_curriculum.lesson_reorder, name='lesson_reorder'),

    # Student — Curriculum overview
    path(
        'curriculum/<int:course_id>/<path:course_slug>/',
        views_curriculum.course_curriculum_view,
        name='course_curriculum',
    ),

    # Student — Lesson view
    path(
        'lesson/<int:course_id>/<path:course_slug>/<int:lesson_id>/',
        views_curriculum.lesson_view,
        name='lesson_view',
    ),

    # Student — Lesson progress AJAX
    path(
        'lesson/progress/<int:lesson_id>/',
        views_curriculum.lesson_progress_update,
        name='lesson_progress_update',
    ),
]
