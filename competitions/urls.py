from django.urls import path
from . import views

app_name = 'competitions'

urlpatterns = [
    path('', views.competition_list, name='competition_list'),
    path('create/', views.create_competition, name='create_competition'),
    path('<int:competition_id>/<str:competition_title>/', views.competition_detail, name='competition_detail'),
    path('<int:competition_id>/<str:competition_title>/edit/', views.edit_competition, name='edit_competition'),
    path('<int:competition_id>/<str:competition_title>/join/', views.join_competition, name='join_competition'),
    path('<int:competition_id>/<str:competition_title>/add_question/', views.add_question, name='add_question'),
    path('<int:competition_id>/<str:competition_title>/<int:question_id>/answer/', views.answer_question, name='answer_question'),
    path('<int:competition_id>/<str:competition_title>/certificate/', views.download_certificate, name='download_certificate'),
    path('<int:competition_id>/', views.redirect_old_competition_url, name='redirect_old_competition_url'),
    path('<int:competition_id>/<str:competition_title>/leaderboard/', views.leaderboard, name='leaderboard'),  # أضف هذا السطر
]