from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string

class LiveSession(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='live_sessions',
        limit_choices_to={'courses_profile__role': 'instructor'}
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='live_sessions_participated',
        blank=True
    )
    meet_link = models.URLField(max_length=500, blank=True, help_text="Google Meet link for the live session")
    session_image = models.URLField(max_length=500, blank=True, null=True, help_text="Enter the image url (example: PostImage)")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    # Part 13 — نظام جروبات المناهج: لو الجلسة دي تابعة لجروب مدرس معين
    # (groups.TeacherGroup)، بتبقى خاصة بأعضاء الجروب ده بس (مش عامة في
    # القايمة العادية). null=True/blank=True عشان الجلسات العادية (مش
    # تابعة لأي جروب) تفضل شغالة بالظبط زي ما هي من غير أي تأثير.
    # on_delete=SET_NULL عشان لو الجروب اتمسح، الجلسة نفسها والتسجيل
    # المرتبط بيها يفضلوا موجودين (يرجعوا جلسة عادية مش تابعة لحد).
    # ملحوظة: related_name='live_sessions' هنا مش بيتعارض مع
    # related_name='live_sessions' بتاع instructor فوق، لإنهم بيرجعوا
    # على موديلين مختلفين تمامًا (User من ناحية، TeacherGroup من ناحية
    # تانية) — كل واحد بيضيف accessor على الموديل التاني بتاعه لوحده.
    group = models.ForeignKey(
        'groups.TeacherGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='live_sessions',
    )

    def __str__(self):
        return f"{self.title} - {self.start_time}"

class LiveRecording(models.Model):
    live_session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='recordings')
    video_file = models.URLField(max_length=500, help_text="enter the recorded url video after the live session")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Part 18 — معاينة مجانية تسويقية: لو التسجيل ده اتعلّم كـ "معاينة
    # مجانية" (is_free_preview=True)، بيظهر في صفحة عامة (من غير تسجيل
    # دخول) بهدف تسويقي: تعريف الزوار بمستوى محتوى المدرس قبل ما ينضموا
    # فعليًا لجروبه. default=False عشان كل التسجيلات القديمة تفضل خاصة
    # زي ما هي، والمدرس/الأدمن هو اللي بيقرر يدويًا أنهي تسجيل يتحط
    # كمعاينة مجانية (عن طريق لوحة الأدمن، تفاصيل القرار في PROGRESS.md
    # Part 18 — مفيش view/فورم مخصص للمدرس لتعليم المحتوى في الجزء ده).
    is_free_preview = models.BooleanField(default=False)

    def __str__(self):
        return f"Recording for {self.live_session.title} - {self.uploaded_at}"