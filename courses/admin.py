from django.contrib import admin
from .models import Course , Video ,Comment , UserProfile , UserTaskSubmission , AlternativeQuiz , Task
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Task)
admin.site.register(AlternativeQuiz)
admin.site.register(UserTaskSubmission)