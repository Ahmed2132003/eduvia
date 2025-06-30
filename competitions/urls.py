from django.urls import path
from . import views

urlpatterns = [
    path('', views.competition_list, name='competition_list'),
    path('create/', views.create_competition, name='create_competition'),
    path('<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('<int:competition_id>/join/', views.join_competition, name='join_competition'),
    path('<int:competition_id>/add-question/', views.add_question, name='add_question'),
    path('<int:competition_id>/edit/', views.edit_competition, name='edit_competition'),
    path('<int:competition_id>/question/<int:question_id>/answer/', views.answer_question, name='answer_question'),
    path('<int:competition_id>/leaderboard/', views.leaderboard, name='leaderboard'),
    path('<int:competition_id>/certificate/', views.download_competition_certificate, name='download_competition_certificate'),
]