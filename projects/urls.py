from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # عرض قائمة المشاريع
    path('', views.projects_view, name='project_list'),
    # عرض قائمة الغرف
    path('rooms/', views.room_list, name='room_list'),
    # تفاصيل المشروع
    path('project/<int:project_id>/', views.project_details, name='project_details'),
    # إضافة مشروع
    path('project/add/', views.add_project, name='add_project'),
    # إضافة مهمة
    path('project/<int:project_id>/add_task/', views.add_task, name='add_task'),
    # الانضمام إلى مهمة
    path('task/<int:task_id>/join/', views.join_task, name='join_task'),
    # تقديم حل
    path('task/<int:task_id>/submit/', views.submit_task, name='submit_task'),
    # الموافقة على حل
    path('submission/<int:submission_id>/approve/', views.approve_submission, name='approve_submission'),
    # إضافة تعليق على المشروع
    path('project/<int:project_id>/comment/', views.add_project_comment, name='add_project_comment'),
    # عرض الحلول المقدمة
    path('task/<int:task_id>/submissions/', views.task_submissions, name='task_submissions'),
    # إضافة تعليق على الحل
    path('submission/<int:submission_id>/comment/', views.add_submission_comment, name='add_submission_comment'),
    # تقييم الحل
    path('submission/<int:submission_id>/rate/', views.rate_submission, name='rate_submission'),
    # تمييز الحل
    path('submission/<int:submission_id>/distinguish/', views.distinguish_submission, name='distinguish_submission'),
    # إنشاء غرفة تعاون
    path('room/create/', views.create_room, name='create_room'),
    # تفاصيل الغرفة
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    # طلب انضمام إلى غرفة
    path('room/<int:room_id>/request-join/', views.request_join_room, name='request_join_room'),
    # إدارة طلبات الانضمام
    path('room/<int:room_id>/manage-requests/', views.manage_join_requests, name='manage_join_requests'),
    # الانضمام إلى غرفة (اختياري، يمكن إزالته إذا لم يعد مطلوبًا)
    path('room/<int:room_id>/join/', views.join_room, name='join_room'),
]