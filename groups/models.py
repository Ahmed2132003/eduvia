import uuid

from django.conf import settings
from django.db import models


class CurriculumCategory(models.Model):
    country = models.CharField(max_length=100)
    stage = models.CharField(max_length=100)
    grade = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('country', 'stage', 'grade')

    def __str__(self):
        return f"{self.country} - {self.stage} - {self.grade}"


class GroupCapacityPlan(models.Model):
    max_students = models.PositiveIntegerField()
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['max_students']

    def __str__(self):
        return f"Up to {self.max_students} students - {self.monthly_price} EGP/month"


class TeacherGroup(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='teacher_groups',
        limit_choices_to={'role': 'instructor'},
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        CurriculumCategory,
        related_name='groups',
        on_delete=models.PROTECT,
    )
    current_plan = models.ForeignKey(
        GroupCapacityPlan,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='groups',
    )
    name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Part 11: كود فريد بيستخدمه الطالب عشان يدخل على "مجتمع المدرس"
    # (رابط انضمام). اتحط على مستوى الجروب (مش على مستوى المدرس مباشرة)
    # عشان نتجنب أي تعديل في accounts.User، لكن الـ view (join_teacher_community)
    # بيستخدم أي كود من أي جروب بتاع المدرس عشان يوصل لكل فئاته المتاحة —
    # تفاصيل القرار في PROGRESS.md (Part 11).
    join_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Part 29 (المرحلة الثانية): وضع الشات الجماعي بتاع الجروب ده — 'open'
    # (الوضع الافتراضي، أي عضو يقدر يكتب) أو 'broadcast_only' (المدرس بس
    # يقدر يبعت رسائل، الطلاب يقدروا يقروا بس). اتحط على TeacherGroup نفسها
    # (مش على GroupChatMessage) لإنه إعداد بيخص الجروب ككل مش رسالة معينة —
    # تفاصيل كاملة في PROGRESS (Part 29).
    CHAT_MODE_CHOICES = [
        ('open', 'open'),
        ('broadcast_only', 'broadcast_only'),
    ]
    chat_mode = models.CharField(
        max_length=20,
        choices=CHAT_MODE_CHOICES,
        default='open',
    )

    class Meta:
        unique_together = ('teacher', 'category')

    def __str__(self):
        display_name = self.name.strip() if self.name else str(self.category)
        return f"{display_name} - {self.teacher.username}"

    @property
    def current_students_count(self):
        return self.memberships.count()

    @property
    def seats_available(self):
        if not self.current_plan:
            return 0
        return self.current_plan.max_students - self.current_students_count


class GroupSubscription(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'pending_payment'),
        ('active', 'active'),
        ('expired', 'expired'),
        ('rejected', 'rejected'),
    ]

    group = models.ForeignKey(
        TeacherGroup,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        GroupCapacityPlan,
        on_delete=models.PROTECT,
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_payment',
    )
    amount_paid = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # ── Part 16: فلاجات تنبيهات انتهاء الاشتراك ──
    # بتمنع تكرار إرسال نفس التنبيه أكتر من مرة لنفس الاشتراك، حتى لو
    # التاسك اليومي اشتغل أكتر من مرة في نفس نافذة الأيام المتبقية.
    # reminder_3days_sent: بيتحط True أول ما تنبيه "هتخلص خلال 3 أيام" يتبعت.
    # reminder_1day_sent: بيتحط True أول ما تنبيه "هتخلص خلال يوم واحد"
    # (الأشد لهجة) يتبعت. الاتنين مستقلين تمامًا عن بعض — ممكن الاشتراك
    # ياخد التنبيه الأول من غير التاني (لو خلص بدري) أو ياخد الاتنين
    # بالترتيب الطبيعي مع اقتراب end_date.
    reminder_3days_sent = models.BooleanField(default=False)
    reminder_1day_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group} - {self.plan} ({self.status})"


class PaymentProof(models.Model):
    subscription = models.ForeignKey(
        GroupSubscription,
        related_name='proofs',
        on_delete=models.CASCADE,
    )
    receipt_image = models.ImageField(upload_to='payment_proofs/')
    transaction_reference = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    def __str__(self):
        return f"Proof for {self.subscription} - submitted {self.submitted_at:%Y-%m-%d}"


class GroupMembership(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='group_memberships',
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        TeacherGroup,
        related_name='memberships',
        on_delete=models.CASCADE,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'group')

    def __str__(self):
        return f"{self.student.username} in {self.group}"


class GroupUpgrade(models.Model):
    UPGRADE_MODE_CHOICES = [
        ('keep_end_date', 'keep_end_date'),
        ('reset_cycle', 'reset_cycle'),
    ]

    group = models.ForeignKey(
        TeacherGroup,
        related_name='upgrades',
        on_delete=models.CASCADE,
    )
    old_plan = models.ForeignKey(
        GroupCapacityPlan,
        related_name='+',
        on_delete=models.PROTECT,
    )
    new_plan = models.ForeignKey(
        GroupCapacityPlan,
        related_name='+',
        on_delete=models.PROTECT,
    )
    upgrade_mode = models.CharField(
        max_length=20,
        choices=UPGRADE_MODE_CHOICES,
    )
    price_difference = models.DecimalField(max_digits=8, decimal_places=2)
    subscription = models.ForeignKey(
        GroupSubscription,
        related_name='upgrade_source',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group} - {self.old_plan} -> {self.new_plan} ({self.upgrade_mode})"


class GroupChatMessage(models.Model):
    """
    Part 14: رسالة شات جماعي جوه جروب معين (TeacherGroup).

    اتحطت هنا في groups/models.py (بدل ما تتربط مباشرة بموديلات
    mentorship.GroupChat / mentorship.GroupMessage الموجودة بالفعل في
    تطبيق تاني)، عشان منربطش تطبيقين مختلفين ببعض بشكل صعب الصيانة —
    mentorship و groups تطبيقين مستقلين تمامًا، وربطهم هيحتاج FK متبادل أو
    استيراد متبادل بين التطبيقين من غير أي فايدة حقيقية هنا (شات الجروبات
    منطقه وصلاحياته مختلفة تمامًا عن شات المينتورشيب: هنا صارم على
    GroupMembership + المدرس صاحب الجروب بس). تفاصيل القرار موثقة في
    PROGRESS.md (Part 14).

    Part 30 (المرحلة الثانية): إرفاق صور/ملفات. الرسالة بقت ممكن تكون
    نص (زي ما كانت)، أو صورة (attachment_image)، أو ملف (attachment_file)
    — حسب message_type. content بقى blank=True لإن رسالة صورة/ملف ممكن
    متبقاش ليها أي نص مصاحب خالص (زي أي تطبيق شات عادي). الفحص الفعلي
    إن الرسالة لازم يكون ليها محتوى فعلي (نص أو مرفق واحد على الأقل)
    بيتم في groups/views.py::group_detail (نفس فلسفة باقي الفورمات في
    المشروع اللي بتتحقق يدويًا في الـ view مش عن طريق Model.clean()) —
    مفيش أي داعي لـ full_clean() هنا لإن الإنشاء دايمًا عن طريق
    .objects.create() بعد تحقق كامل في الـ view.
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'text'),
        ('image', 'image'),
        ('file', 'file'),
    ]

    group = models.ForeignKey(
        TeacherGroup,
        related_name='chat_messages',
        on_delete=models.CASCADE,
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    content = models.TextField(blank=True)
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
    )
    attachment_image = models.ImageField(
        upload_to='group_chat/images/', null=True, blank=True,
    )
    attachment_file = models.FileField(
        upload_to='group_chat/files/', null=True, blank=True,
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.username} in {self.group} @ {self.sent_at:%Y-%m-%d %H:%M}"

    @property
    def attachment_file_name(self):
        """
        Part 30: اسم ملف المرفق بس (من غير مسار group_chat/files/...) —
        property بسيطة بدل ما التمبلت يعتمد على slice بعدد أحرف ثابت
        (اللي كان ممكن يبقى هش لو upload_to اتغيّر لاحقًا).
        """
        if not self.attachment_file:
            return ''
        return self.attachment_file.name.rsplit('/', 1)[-1]


class GroupLiveSession(models.Model):
    """
    Part 22 — المرحلة الثانية: البث المباشر داخل الجروب.

    قرار معماري كامل (المزود المختار LiveKit، والبدائل اللي اتفكر فيها
    ورفضتها) موثق في PROGRESS_PART22.md، قسم "قرارات معمارية اتاخدت
    (Part 22)". الموديل ده بيمثل جلسة بث مباشر واحدة جوه جروب معين —
    مش مرتبط بـ workshops.LiveSession خالص (تطبيق منفصل بالكامل، بنفس
    فلسفة GroupChatMessage في Part 14: عدم ربط تطبيقات مختلفة ببعض من
    غير داعي قوي). room_identifier بيتملى من طبقة التكامل مع مزود الـ
    WebRTC (groups/live_provider.py) اللي اتبنت في Part 23.

    Part 26 (نسخة معدّلة — Manual Recording Upload): كان فيه حقل واحد
    (recording_url، URLField) مخصص لنظام التسجيل التلقائي (LiveKit
    Egress -> S3) اللي اتلغى بالكامل. بدل منه دلوقتي 3 حقول لنظام الرفع
    اليدوي (المدرس بيرفع الفيديو بنفسه بعد ما اللايف يخلص):
      - recording_file: الملف نفسه، بنفس Storage Backend المستخدم فعليًا
        لملفات الكورسات (courses.models.VideoFile.file — FileField عادي
        فوق DEFAULT_FILE_STORAGE المحلي المظبوط في settings.py، بدون أي
        تخزين S3 منفصل).
      - recording_uploaded_at: وقت ما المدرس رفع الملف فعليًا (مش وقت
        انتهاء اللايف نفسه — ended_at موجود بالفعل لده من Part 22).
      - recording_duration: مدة الفيديو (اختياري). مفيش أي كود بيحسبها
        تلقائيًا دلوقتي (محتاج مكتبة تحليل فيديو زي ffprobe مش موجودة في
        المشروع)، فبتفضل فاضية إلا لو حد ملاها يدويًا لاحقًا.
    """
    MODE_CHOICES = [
        ('camera', 'camera'),
        ('screen_share', 'screen_share'),
        ('both', 'both'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'scheduled'),
        ('live', 'live'),
        ('ended', 'ended'),
        ('canceled', 'canceled'),
    ]

    # ملحوظة (بعد فحص makemigrations): استخدمت related_name='group_live_sessions'
    # مش 'live_sessions' — لإن workshops.LiveSession.group (من Part 13) أصلاً
    # بيستخدم related_name='live_sessions' على نفس TeacherGroup ده بالظبط،
    # فاستخدام نفس الاسم هنا كان هيعمل تعارض حقيقي (fields.E304/E305) —
    # الاتنين بيرجعوا على نفس الموديل الهدف (TeacherGroup)، على عكس حالة
    # instructor/group جوه workshops.LiveSession نفسها اللي كانت آمنة لأنهم
    # بيرجعوا على موديلين مختلفين (User وTeacherGroup).
    group = models.ForeignKey(
        TeacherGroup,
        related_name='group_live_sessions',
        on_delete=models.CASCADE,
    )
    # المدرس صاحب الجروب اللي بدأ/جدول الجلسة دي. related_name='+' لإن
    # مفيش حاجة في المشروع محتاجة reverse query "كل الاليفات اللي فلان
    # عملها" دلوقتي (زي نفس القرار في PaymentProof.reviewed_by).
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='+',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='camera')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    # اسم الروم عند مزود الـ WebRTC (LiveKit). blank=True لإنه بيتولد وقت
    # إنشاء الروم فعليًا عند المزود (Part 23)، مش وقت إنشاء الصف في
    # الداتابيز. unique=True عشان مايتكررش روم بنفس الاسم عند المزود.
    room_identifier = models.CharField(max_length=100, unique=True, blank=True)

    # ── Part 26 (نسخة معدّلة — Manual Recording Upload) ──
    # الفيديو نفسه، بنفس Storage Backend المستخدم لملفات الكورسات
    # (courses.VideoFile.file). null=True زيادة عن blank=True لإن
    # FileField ما بيتخزنش فارغ زي CharField بشكل متسق دايمًا لو الحقل
    # null=False على مستوى الداتابيز — نفس نمط الحقول الاختيارية التانية
    # في المشروع (زي PaymentProof.reviewed_by مثلاً).
    recording_file = models.FileField(
        upload_to='group_live_recordings/', null=True, blank=True,
    )
    recording_uploaded_at = models.DateTimeField(null=True, blank=True)
    recording_duration = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.group} ({self.status})"


class GroupLesson(models.Model):
    """
    Part 27 — المرحلة الثانية: الدروس المسجلة (المسار البديل غير-اللايف
    لتوصيل المحتوى جوه الجروب — المدرس بيرفع درس جاهز بدل ما يبث لايف).

    مقارنة الحقول مع courses.models.Lesson (نظام "المنهج الجديد" —
    Section/Lesson، الأحدث والمسجل بالكامل في courses/admin.py بـ
    LessonInline + fieldsets مخصصة، على عكس نظام Video/VideoFile القديم):

    فحصت الملف الحقيقي (courses/models.py) قبل ما أكتب أي حقل هنا. النتيجة
    المهمة: **الفيديو الأساسي في courses.Lesson مخزّن كـ رابط خارجي
    (video_url = URLField)، مش كملف مرفوع (upload_to)** — الـ FileField
    الوحيدة الموجودة في تطبيق courses (VideoFile.file) هي مرفقات إضافية
    اختيارية على نظام Video القديم، مش مسار الفيديو الأساسي في أي من
    النظامين (القديم أو الجديد). القرار هنا: نسخت نفس الأسلوب بالظبط
    (video_url خارجي + video_duration بيتكتب يدويًا من المدرس)، عشان
    نفضل متسقين مع النظام الفعلي الشغال في المشروع، بدل ما نخترع رفع ملف
    (FileField) مالوش نظير حقيقي في أي مكان تاني بالمنصة لتخزين الفيديو
    الأساسي.

    فروق متعمدة عن courses.models.Lesson:
    - مفيش lesson_type (video/text/article) — الجزء ده مخصص بالتحديد
      لـ"الدروس المسجلة" (فيديو بس)، زي ما اتطلب في نص الجزء، فمفيش داعي
      لتعقيد الاختيار بين أنواع محتوى تانية دلوقتي. لو Ahmed عايز دروس
      نصية/مقالات جوه الجروب لاحقًا، سهل نضيف الحقل ده بعدين بنفس فلسفة
      Lesson.lesson_type.
    - مفيش is_preview (معاينة مجانية قبل الاشتراك) — المفهوم المكافئ في
      نظام الجروبات أصلاً موجود على مستوى تسجيلات اللايف
      (workshops.LiveRecording.is_free_preview من Part 18)، مش مطلوب هنا
      صراحة في نص الجزء.
    - مفيش صورة مصغرة (thumbnail): فحصت courses.models كامل — مفيش أي
      صورة على مستوى الدرس/الفيديو في أي من النظامين (القديم أو الجديد)،
      الصورة موجودة بس على مستوى الكورس ككل (Course.image/image_file).
      فمفيش "نفس منطق" نتبعه هنا لصورة مصغرة على مستوى الدرس، فسبتها.
    - created_at: مش موجود في courses.models.Lesson خالص، لكن ضفته هنا
      بنفس نمط باقي موديلات groups كلها (كل موديل في التطبيق ده عنده
      created_at) — تفصيل بسيط اخترته بنفسي مش نسخ حرفي من Lesson.

    is_published و publish_at: زي ما اتطلب بالظبط في نص الجزء، مُجهّزين
    لاستخدامهم في الجدولة التلقائية (Part 31) — مفيش أي منطق نشر تلقائي
    بيستخدمهم فعليًا لسه في الجزء ده (27)، هما بس حقول جاهزة.
    """
    group = models.ForeignKey(
        TeacherGroup,
        related_name='lessons',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    # نفس أسلوب courses.models.Lesson.video_url بالظبط — رابط خارجي،
    # مش رفع ملف. تفاصيل السبب في الـ docstring فوق.
    video_url = models.URLField(max_length=500, blank=True, null=True)
    # نفس أسلوب courses.models.Lesson.video_duration بالظبط — بيتكتب
    # يدويًا من المدرس بالدقايق، مفيش حساب تلقائي من الملف (زي ما هو
    # الحال في courses أصلاً، لإن الفيديو رابط خارجي مش ملف مرفوع).
    video_duration = models.FloatField(
        default=0,
        help_text='مدة الفيديو بالدقايق (بتتكتب يدويًا من المدرس)',
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    publish_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # نفس ordering = ['order'] بتاعة courses.models.Lesson، بس ضفت
        # created_at كـ tie-breaker ثاني (اختيار مني، مش موجود في
        # Lesson الأصلية) عشان لو أكتر من درس بنفس قيمة order بالظبط
        # (زي القيمة الافتراضية 0 قبل ما المدرس يرتبهم يدويًا)، الترتيب
        # يفضل ثابت ومتوقع (الأقدم أول) بدل ما يعتمد على ترتيب الداتابيز
        # الداخلي غير المضمون.
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"[{self.group}] {self.title}"


class GroupAssignment(models.Model):
    """
    Part 33 — المرحلة الثانية: الواجبات داخل الجروب.

    فحصت courses/models.py و courses/views.py الحقيقيين قبل أي كود
    (زي ما اتطلب بالظبط). النتيجة المهمة اللي لازم توثّق هنا بوضوح:
    **نظام "الواجبات" الفعلي الموجود في courses (LessonTask +
    LessonTaskSubmission، النظام الأحدث اللي فيه أنواع mcq/essay/
    file_upload/external_link) نظام تصحيح تلقائي بالكامل** — الدرجة
    (`score`) بتتحسب أوتوماتيك كنسبة مئوية (مقارنة `correct_answer` في
    حالة mcq)، و`passed` بتتحدد أوتوماتيك من `passing_score`. **مفيش أي
    حقل `grade`/`feedback`/`graded_by`/`graded_at` في courses خالص** —
    مفيش تصحيح يدوي من المدرس لأي نوع تسليم هناك، حتى essay/file_upload
    (بيتسجلوا submission بس من غير أي درجة يدوية).

    ده مختلف عن اللي Part 33/34 مطلوبين فعليًا (المدرس "يصحح ويدي درجة"
    بفورم درجة+ملاحظة، زي ما هو موثق صراحة في نص Part 34). القرار هنا:
    **مبنيتش على نمط courses.LessonTask الأوتوماتيكي**، وبنيت بدل منه
    نظام تصحيح **يدوي** بالحقول المطلوبة صراحة في نص Part 33
    (title, description, attachment, due_date, max_grade, created_at)
    — لإن ده التصميم المقصود فعليًا حسب خريطة الأجزاء (Part 34 لاحقًا
    محتاج view تصحيح يدوي من المدرس)، مش لإني بنسخ نمط موجود بالفعل في
    courses (مفيش نمط "تصحيح يدوي" حقيقي هناك أصلاً أقدر أنسخه).

    الحقل الوحيد اللي فعلاً موجود بنفس الروح في courses هو الأسلوب العام
    لتخزين المرفقات (FileField عادي زي courses.VideoFile.file/
    LessonAttachment.file، فوق DEFAULT_FILE_STORAGE المحلي، من غير أي
    تخزين خارجي منفصل) — استخدمت نفس الأسلوب ده هنا لحقل attachment.
    """
    group = models.ForeignKey(
        TeacherGroup,
        related_name='assignments',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    # مرفق اختياري بيرفعه المدرس مع الواجب (ملف تعليمات، ورقة أسئلة، إلخ)
    # — نفس أسلوب تخزين الملفات المستخدم في courses (FileField عادي فوق
    # التخزين المحلي المظبوط في settings.py، بدون أي بنية تخزين جديدة).
    attachment = models.FileField(
        upload_to='group_assignments/attachments/', null=True, blank=True,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    # الدرجة القصوى للواجب — PositiveIntegerField بسيطة (زي "من 100" أو
    # "من 20") بدل DecimalField، لإن الطلب الأصلي مقالش صراحة عايز كسور
    # عشرية في الدرجة، وده أبسط شكل لفورم "درجة + ملاحظة" في Part 34.
    # اخترت القيمة الافتراضية 100 بنفسي (مش متحددة صراحة في الطلب).
    max_grade = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"[{self.group}] {self.title}"

    @property
    def submissions_count(self):
        return self.submissions.count()


class GroupAssignmentSubmission(models.Model):
    """
    Part 33 — تسليم الطالب لواجب معين (GroupAssignment)، مع تصحيح يدوي
    من المدرس. تفاصيل قرار "التصحيح اليدوي" (بدل النمط الأوتوماتيكي
    الموجود فعليًا في courses.LessonTaskSubmission) موثقة كاملة في
    docstring الموديل GroupAssignment فوق.

    unique_together = ('assignment', 'student'): الطالب بيسلّم مرة واحدة
    بس لكل واجب — زي ما اتطلب بالظبط في نص Part 33 ("الطالب يقدر يعدّل
    تسليمه لحد ما يتصحح"). القرار العملي: التعديل بعد التصحيح (لما
    grade/graded_at يبقوا معمولين) هيتمنع من الـ view نفسه في Part 34
    (مش من الموديل هنا)، بنفس فلسفة كل الفحوصات التانية في المشروع اللي
    بتتم يدويًا في الـ view مش عن طريق Model.clean().
    """
    assignment = models.ForeignKey(
        GroupAssignment,
        related_name='submissions',
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='group_assignment_submissions',
        on_delete=models.CASCADE,
    )
    content = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='group_assignments/submissions/', null=True, blank=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    # ── تصحيح المدرس ──
    # null=True (مش بس blank=True) لإن الدرجة مالهاش قيمة حقيقية قبل ما
    # المدرس يصححها — صفر هنا معناه "اتصححت بصفر"، مش "لسه ما اتصححتش"،
    # فالـ null هو الفارق الصحيح بين الحالتين.
    grade = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} -> {self.assignment} ({'graded' if self.graded_at else 'pending'})"

    @property
    def is_graded(self):
        return self.graded_at is not None


class GroupTodoItem(models.Model):
    """
    Part 35 — المرحلة الثانية: قائمة To-Do بسيطة للمدرس والطالب.

    قرار المكان (groups مش core): البرومبت سايب الاختيار مفتوح ("أو تطبيق
    core لو شايف إنه أنسب مكان معماريًا"). اخترت groups/models.py بدل ما
    أعمل تطبيق core جديد لموديل واحد بسيط، للأسباب دي:
    - الاستخدام الرئيسي المتوقع (لينك "مهامي" في dashboard.html
      وmy_learning_groups.html) أصلاً جوه سياق تطبيق groups.
    - كل الموديلات المشابهة (الواجبات GroupAssignment، الدروس GroupLesson،
      اللايف GroupLiveSession) موجودة في نفس التطبيق ده.
    - عمل تطبيق Django جديد بالكامل (app جديد في INSTALLED_APPS، migrations
      خاصة بيه) لموديل واحد فيه FK اختياري لـ TeacherGroup كان هيبقى تعقيد
      زيادة عن الحاجة الفعلية للجزء ده.
    لو Ahmed شايف إن "المهام اليومية" هتكبر مستقبلاً (تطبيق مستقل بمنطقه
    الخاص)، سهل نفصلها بعدين بـ migration بسيطة (نقل الموديل لتطبيق جديد).

    group اختياري (null=True, blank=True) عشان المهمة ممكن تكون شخصية
    بالكامل (مش مرتبطة بأي جروب) — زي ما اتطلب بالظبط في نص الجزء.
    on_delete=CASCADE على group (مش SET_NULL) لإن مهمة مرتبطة بجروب اتمسح
    منطقيًا بتفقد سياقها بالكامل، فأنسب تتمسح معاه بدل ما تفضل معلّقة
    بجروب مش موجود.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='todo_items',
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        TeacherGroup,
        related_name='todo_items',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Part 36 (المرحلة الثانية): فلاج بيمنع تكرار إرسال تذكير المهمة أكتر
    # من مرة، بنفس منطق reminder_3days_sent/reminder_1day_sent على
    # GroupSubscription (Part 16) بالظبط — بيتحط True أول ما التذكير
    # يتبعت بنجاح، والتاسك الدوري بيستبعد أي مهمة الفلاج بتاعها True.
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        # المهام المعلّقة (is_done=False) أول حاجة، مرتبة بالأقرب ميعادًا،
        # وبعدين المهام المخلّصة. ده تحسين بسيط اخترته بنفسي فوق مجرد
        # "مرتبة بـ due_at" المطلوبة صراحة في النص — بيخلي المهام المهمة
        # (لسه معلّقة) تظهر فوق تلقائيًا في my_todo_list من غير أي فرز إضافي
        # في الـ view نفسه.
        ordering = ['is_done', 'due_at', '-created_at']

    def __str__(self):
        return f"{self.owner.username}: {self.title}"