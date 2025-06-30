from django.contrib import admin
from .models import Project, Task, TaskSubmission, ProjectComment
from django.utils import timezone

# إجراء جماعي للموافقة على تقديمات المهام
def approve_submissions(modeladmin, request, queryset):
    for submission in queryset:
        if not submission.approved:
            submission.approved = True
            submission.approved_at = timezone.now()
            submission.feedback = "تمت الموافقة بواسطة الإدارة"
            submission.save()
            # تحديث حالة المهمة إلى مكتملة
            submission.task.completed = True
            submission.task.completed_at = timezone.now()
            submission.task.save()
    modeladmin.message_user(request, "تمت الموافقة على التقديمات المحددة بنجاح.")
approve_submissions.short_description = "الموافقة على التقديمات المحددة"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'status', 'category', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('instructor',)  # لتحسين الأداء عند اختيار المحاضر
    list_per_page = 25

    # عرض المهام المرتبطة داخل صفحة المشروع
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tasks')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'priority', 'completed', 'due_date', 'xp_reward', 'coins_reward')
    list_filter = ('priority', 'completed', 'due_date', 'project__status')
    search_fields = ('title', 'description', 'project__title')
    list_editable = ('priority', 'completed', 'xp_reward', 'coins_reward')
    raw_id_fields = ('project', 'assigned_to')
    list_per_page = 25

    # عرض الطلاب المعينين في عمود
    def get_assigned_to(self, obj):
        return ", ".join([user.username for user in obj.assigned_to.all()])
    get_assigned_to.short_description = "الطلاب المعينون"

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'student', 'submitted_at', 'approved', 'approved_at')
    list_filter = ('approved', 'submitted_at', 'approved_at')
    search_fields = ('task__title', 'student__username', 'description')
    actions = [approve_submissions]  # إضافة الإجراء الجماعي
    raw_id_fields = ('task', 'student')
    list_per_page = 25

    # تحديث المكافآت تلقائيًا عند الموافقة يتم عبر الـ Signal في النماذج
    def save_model(self, request, obj, form, change):
        if obj.approved and not obj.approved_at:
            obj.approved_at = timezone.now()
            obj.task.completed = True
            obj.task.completed_at = timezone.now()
            obj.task.save()
        super().save_model(request, obj, form, change)

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__title', 'user__username', 'content')
    raw_id_fields = ('project', 'user')
    list_per_page = 25

    # عرض معاينة مختصرة للتعليق
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = "معاينة التعليق"