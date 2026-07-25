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
    """
    group = models.ForeignKey(
        TeacherGroup,
        related_name='chat_messages',
        on_delete=models.CASCADE,
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.username} in {self.group} @ {self.sent_at:%Y-%m-%d %H:%M}"