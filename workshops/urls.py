from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    path('', views.live_session_list, name='live_session_list'),
    # Part 18: صفحة عامة تسويقية (من غير تسجيل دخول) — لازم تكون قبل
    # أي path فيه <int:...> عشان مايتفسّرش بالغلط، بس عمليًا مفيش تعارض
    # هنا لأن الـ path ده string ثابت بالكامل.
    path('free-preview/', views.free_previews_list, name='free_previews_list'),
    path('watch-live/<int:session_id>/<str:slugified_title>/', views.watch_live, name='watch_live'),
    path('watch-recording/<int:recording_id>/<str:slugified_title>/', views.watch_recording, name='watch_recording'),
    path('create-session/', views.create_live_session, name='create_live_session'),
    path('start-live/<int:session_id>/<str:slugified_title>/', views.start_live, name='start_live'),
    path('start-live-stream/<int:session_id>/<str:slugified_title>/', views.watch_live, name='start_live_stream'),
    path('upload-recording/<int:session_id>/<str:slugified_title>/', views.upload_recording, name='upload_recording'),
]