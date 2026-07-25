"""
groups/urls.py
==============
Part 7 — لوحة تحكم المدرس + فورم إنشاء جروب.
Part 8 — رفع إثبات الدفع.
Part 10 — ترقية سعة الجروب.
Part 11 — انضمام الطالب لمجتمع المدرس.
Part 12 — لوحة "جروباتي" للطالب + صفحة محتوى الجروب (placeholder).
"""

from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('dashboard/', views.teacher_groups_dashboard, name='teacher_dashboard'),
    path('create/', views.create_group, name='create_group'),
    path('category-options/', views.category_options_json, name='category_options_json'),
    path(
        'subscriptions/<int:subscription_id>/payment-proof/',
        views.submit_payment_proof,
        name='submit_payment_proof',
    ),
    path(
        '<int:group_id>/upgrade/',
        views.upgrade_group,
        name='upgrade_group',
    ),
    path(
        'join/<uuid:code>/',
        views.join_teacher_community,
        name='join_teacher_community',
    ),
    path('my-learning/', views.my_learning_groups, name='my_learning_groups'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
]