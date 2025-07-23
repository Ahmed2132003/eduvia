from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    path('', views.live_session_list, name='live_session_list'),
    path('watch-live/<int:session_id>/<str:slugified_title>/', views.watch_live, name='watch_live'),
    path('watch-recording/<int:recording_id>/<str:slugified_title>/', views.watch_recording, name='watch_recording'),
    path('create-session/', views.create_live_session, name='create_live_session'),
    path('start-live/<int:session_id>/<str:slugified_title>/', views.start_live, name='start_live'),
    path('start-live-stream/<int:session_id>/<str:slugified_title>/', views.watch_live, name='start_live_stream'),
    path('upload-recording/<int:session_id>/<str:slugified_title>/', views.upload_recording, name='upload_recording'),
]