from django.contrib import admin
from .models import Competition, Question, Participant, Answer

# Inline for Questions to be edited within Competition
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of empty forms to display
    fields = ('text', 'question_type', 'choices', 'correct_answer', 'points', 'coins')
    list_display = ('text', 'question_type')

# Inline for Participants to be viewed within Competition
class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0  # No extra forms, only show existing
    fields = ('user', 'total_xp', 'total_coins', 'joined_at')
    readonly_fields = ('user', 'total_xp', 'total_coins', 'joined_at')
    can_delete = False

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'start_time', 'end_time', 'is_active', 'is_ongoing')
    list_filter = ('is_active', 'start_time', 'instructor')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_time'
    inlines = [QuestionInline, ParticipantInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'question_time_limit', 'is_active')
        }),
    )

    def is_ongoing(self, obj):
        return obj.is_ongoing
    is_ongoing.boolean = True
    is_ongoing.short_description = 'Ongoing'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'competition', 'question_type', 'points', 'coins')
    list_filter = ('competition', 'question_type')
    search_fields = ('text', 'competition__title')
    fieldsets = (
        (None, {
            'fields': ('competition', 'text', 'question_type')
        }),
        ('Answer Details', {
            'fields': ('choices', 'correct_answer', 'points', 'coins')
        }),
    )

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'competition', 'total_xp', 'total_coins', 'joined_at')
    list_filter = ('competition',)
    search_fields = ('user__username', 'competition__title')
    readonly_fields = ('joined_at', 'total_xp', 'total_coins')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('participant', 'question', 'answer_text', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'question__competition')
    search_fields = ('participant__user__username', 'question__text', 'answer_text')
    readonly_fields = ('submitted_at', 'is_correct')