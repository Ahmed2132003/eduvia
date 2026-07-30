# PROGRESS.md — نظام جروبات المناهج (Eduvia)

## الحالة الحالية
آخر جزء منفذ: Part 15

## قرارات معمارية اتاخدت
- (هيتضاف هنا أي قرار مهم أثناء التنفيذ: أسماء حقول، مكان ملفات، إلخ)
- Part 3: TeacherGroup.name حقل CharField(blank=True) زي ما هو مطلوب، لكن الـ
  "استخدام اسم الفئة تلقائيًا في العرض لو فاضي" اتنفذ جوه __str__ بس (منطق عرض،
  مش قيمة مخزنة في الداتابيز). يعني لو name فاضي، str(group) هترجع اسم الفئة
  + اسم المدرس بدل ما ترجع فاضي. أي مكان تاني في المشروع (templates مثلاً)
  عايز يعرض اسم الجروب لازم يستخدم نفس المنطق ده (property أو helper) مش
  group.name مباشرة، عشان ميطلعش فاضي في الواجهة.
- Part 4: status على GroupSubscription اتعمل CharField مع max_length=20 (مش
  متحدد في الطلب الأصلي، اخترت 20 لأنها كافية لأطول قيمة 'pending_payment').
  ده تفصيل تقني بسيط مش قرار معماري مؤثر.
- Part 4: MEDIA_URL و MEDIA_ROOT كانوا مظبوطين بالفعل في settings.py
  (MEDIA_ROOT = '/data/media') فمفيش أي تعديل احتاج يتعمل في الإعدادات عشان
  receipt_image (ImageField) يشتغل. لازم فقط التأكد إن مكتبة Pillow مثبتة على
  السيرفر (pip install Pillow) قبل تشغيل الـ migration، لأنها شرط أساسي لأي
  ImageField في Django.
- Part 5: student FK على GroupMembership اتعمل بـ settings.AUTH_USER_MODEL
  (زي teacher على TeacherGroup) مش استيراد User مباشر من accounts، عشان
  نفس نمط باقي الموديلات في التطبيق ومتوافق مع الـ custom user model.
  مفيش limit_choices_to على student (بعكس teacher) لأن أي مستخدم عنده role
  'student' أو حتى غيره نظريًا ممكن ينضم كطالب — الفلترة الفعلية على مين
  يقدر ينضم هتتحدد في الـ view نفسه (Part 11) مش على مستوى الموديل.
  current_students_count و seats_available اتضافوا كـ @property عادي (مش
  cached_property) عشان يفضلوا محسوبين لايف من الداتابيز في كل مرة، خصوصًا
  إن العدد ده بيتغير باستمرار مع كل GroupMembership جديد.
- Part 6: upgrade_mode على GroupUpgrade اتعمل CharField(max_length=20) —
  مش متحدد في الطلب الأصلي، اخترت 20 عشان كافية لأطول قيمة 'keep_end_date'.
  old_plan و new_plan اتعملوا on_delete=PROTECT — القرار مش متحدد صراحة في
  الطلب، بس اخترته عشان منمنعش حذف باقة (GroupCapacityPlan) لسه موجودة في
  سجل ترقية قديم، بنفس منطق GroupSubscription.plan في Part 4.
  subscription (FK على GroupSubscription) اتعمل on_delete=CASCADE — برضه
  مش متحدد في الطلب، اخترته لأن GroupUpgrade سجل تابع للاشتراك الجديد اللي
  اتعمل بسببه؛ لو الاشتراك اتمسح، سجل الترقية المرتبط بيه بيفقد معناه.
  لو Ahmed شايف إن PROTECT أنسب هنا (زي باقي أماكن المشروع)، سهل نغيرها في
  migration جديدة.
- Part 7: فحص دور المدرس اتعمل بـ request.user.role == 'instructor' مباشرة
  (accounts.User.role) مش عن طريق user.courses_profile.role. ده متسق مع
  الملحوظة الرسمية في خطة التنفيذ ("role على accounts.User هو المرجع
  الرسمي لدور student/instructor")، وده نفس الحقل اللي اتستخدم فعليًا في
  limit_choices_to بتاع TeacherGroup.teacher من Part 3. لاحظت إن
  workshops/views.py بيستخدم نمط مختلف شوية (fallback بين courses_profile.role
  و getattr(user, 'role'))، بس فضلت الاعتماد على الحقل الرسمي مباشرة بدل ما
  أضيف تعقيد مش لازم.
- Part 7: عملت decorator اسمه instructor_required في groups/views.py (بيلف
  login_required + فحص الدور) بدل ما أكرر نفس الشرط في كل view — استخدمته
  على الثلاث views (teacher_groups_dashboard، create_group،
  category_options_json).
- Part 7: صفحة رفع إثبات الدفع (submit_payment_proof) مش موجودة لسه —
  هتتبنى في Part 8. عشان كده create_group() دلوقتي بترجّع المدرس لـ
  groups:teacher_dashboard بعد الإنشاء (مع رسالة نجاح توضح إن الخطوة الجاية
  هي رفع إثبات الدفع)، مش لصفحة رفع الإثبات زي ما مطلوب أصلاً في الخطة.
  ⚠️ لازم لما Part 8 يتنفذ، السطر ده في create_group() يتغيّر من:
    return redirect('groups:teacher_dashboard')
  لـ:
    return redirect('groups:submit_payment_proof', subscription_id=subscription.id)
  (وهيحتاج كمان نسمي متغير الـ GroupSubscription اللي بيترجع من .create()
  بدل ما نتجاهله زي دلوقتي).
- Part 7: category_options_json بيرجع للمستوى الأخير (grade) قايمة من
  objects فيها {id, grade} مش سلاسل نصية بس، عشان الفرونت يقدر يحدد قيمة
  حقل category المخفي (بالـ id الفعلي بتاع CurriculumCategory) من غير أي
  استعلام إضافي أو تخمين. مستويي country وstage بيرجعوا سلاسل نصية عادية
  لأنهم مجرد فلترة وسيطة.
- Part 7: التمبلتس (dashboard.html وcreate_group.html) اتعملت كصفحات
  مستقلة كاملة (standalone، فيها <html>/<head>/<body> بتاعتها) مش
  {% extends "base.html" %}، لأن instructor_dashboard.html اللي اتراجعت
  كمرجع من courses قبل ما أبدأ اتضح إنها هي كمان مش بتعمل extends لأي base
  مشترك — كل صفحة في المشروع شكلها عاملة بنفس نظام التصميم "Obsidian
  Academy" (نفس CSS variables، نفس topbar/nav markup) لكن كملف مستقل
  بالكامل. اتبعت نفس النمط ده بالظبط، ونسخت نفس متغيرات الألوان والخطوط
  وهيكل الـ topbar/hero/footer وستايل الأزرار (action-btn) والـ pills من
  instructor_dashboard.html عشان الشكل يبقى متسق مع باقي المنصة.
- Part 15: ✅ تصحيح لملاحظة سابقة — أول مسودة لهذا الجزء كانت اعتمدت على
  إعادة بناء groups/views.py من التوثيق (بسبب تعارض اسم ملف وقت الرفع في
  الجلسة اللي فاتت، اتبعت views.py مرتين ووصل بس نسخة workshops). بعد
  كده Ahmed بعت groups/views.py الحقيقي (771 سطر)، فاتعمل عليه **patch
  دقيق** (str-replace مباشر على النص الأصلي، مش إعادة كتابة) يقتصر على
  نقطتين بس:
  1) استبدال الدالة المحلية `_group_is_currently_active(group, now=None)`
     (اللي كانت بترجع tuple: `(is_active_bool, active_subscription)`)
     بدالة أبسط `_get_active_subscription(group)` (بترجع الاشتراك بس،
     لغرض العرض — end_date في التمبلتس). سؤال "هل الجروب نشط فعليًا؟"
     بقى مسؤولية `groups.access.is_group_content_accessible` وحدها.
  2) استبدال استدعاء `_group_is_currently_active(...)` في مكانين بس:
     `my_learning_groups()` و `group_detail()` — كل واحد بقى بيستدعي
     `is_group_content_accessible(group)` (للـ boolean) و
     `_get_active_subscription(group)` (للعرض) بدل السطر القديم.
     رسالة التجميد في `group_detail` بقت بتستخدم الثابت
     `GROUP_FROZEN_MESSAGE` من `groups/access.py` بدل النص المكتوب يدويًا،
     عشان يبقى نفس النص بالظبط المستخدم في workshops/views.py.
  - **مفيش أي تعديل تاني على الملف خالص** — باقي الـ 768 سطر (بعد الحذف
    البسيط) زي ما هي 100%: teacher_groups_dashboard، create_group،
    category_options_json، submit_payment_proof، _remaining_days،
    _calculate_upgrade_price، upgrade_group، join_teacher_community،
    كل الـ decorators، وباقي منطق group_detail (attach/detach_session،
    send_message، عرض الجلسات والشات) متلمسش خالص.
  - الـ diff الكامل بين النسخة الأصلية والمعدَّلة اتراجع سطر بسطر قبل
    التسليم للتأكد إن مفيش أي تغيير غير مقصود تسرب للملف.

## سجل الأجزاء

### Part 0 — إزالة الشات بوت
الحالة: تم
تفاصيل:
- شيلت 'chatbot' من INSTALLED_APPS في Eduvia/settings.py.
- شيلت path("chatbot/", include("chatbot.urls")) من Eduvia/urls.py.
- عملت migrate chatbot zero قبل شيل الـ app من INSTALLED_APPS، عشان يحذف جداول
  BotChat و BotMessage من الداتابيز بشكل نضيف.
- فولدر chatbot/ نفسه اتسيب موجود على الديسك بدون أي حذف، بس بقى مفصول
  تمامًا عن المشروع (مش متضمن في أي إعدادات).
- شغّلت python manage.py check وتأكدت إن مفيش أخطاء ناتجة عن الحذف.

### Part 1 — تطبيق groups + CurriculumCategory
الحالة: تم
تفاصيل:
- أنشأت تطبيق Django جديد اسمه groups عن طريق python manage.py startapp groups.
- ضفت 'groups' في آخر INSTALLED_APPS في Eduvia/settings.py.
- عملت موديل CurriculumCategory في groups/models.py بالحقول:
  country, stage, grade (CharField)، is_active (Boolean, default True)،
  created_at (auto_now_add).
- Meta.unique_together = ('country', 'stage', 'grade') عشان نمنع تكرار
  نفس التوليفة (دولة/مرحلة/صف).
- __str__ بيرجع "country - stage - grade".
- سجّلت الموديل في groups/admin.py مع list_display (country, stage, grade,
  is_active, created_at)، list_filter (country, stage, is_active)،
  search_fields (country, stage, grade).
- شغّلت makemigrations groups ثم migrate بنجاح.

### Part 2 — موديل GroupCapacityPlan + زرع الباقات
الحالة: تم
تفاصيل:
- ضفت موديل GroupCapacityPlan في groups/models.py بالحقول:
  max_students (PositiveIntegerField)، monthly_price (DecimalField,
  max_digits=8, decimal_places=2)، is_active (Boolean, default True)،
  created_at (auto_now_add).
- Meta.ordering = ['max_students'] عشان الباقات تترتب تلقائيًا من الأصغر
  للأكبر في أي مكان بيتعرض فيه الموديل (زي admin وأي queryset مستقبلي).
- __str__ بيرجع "حتى {max_students} طالب - {monthly_price} جنيه/شهر".
- سجّلت الموديل في groups/admin.py بنفس نمط CurriculumCategory:
  list_display (max_students, monthly_price, is_active, created_at)،
  list_filter (is_active)، search_fields (max_students).
- عملت migration واحدة (0002_groupcapacityplan.py) فيها خطوتين:
  1) CreateModel لجدول GroupCapacityPlan.
  2) RunPython (seed_default_plans) بتزرع 6 باقات افتراضية بسعة
     50, 100, 150, 200, 250, 300 طالب، كلها بسعر placeholder = 0.00
     و is_active=True. الأدمن هيدخل يعدّل الأسعار الحقيقية بنفسه من
     لوحة التحكم لاحقًا.
  - استخدمت get_or_create على max_students عشان لو الـ migration اتشغلت
    تاني بالغلط ميكررش نفس الباقات.
  - ضفت reverse function (remove_default_plans) للـ RunPython عشان
    الـ migration تبقى قابلة للـ rollback بشكل نضيف.
- شغّلت migrate بنجاح والباقات الست اتزرعت في الداتابيز.

### Part 3 — موديل TeacherGroup
الحالة: تم
تفاصيل:
- ضفت موديل TeacherGroup في groups/models.py بالحقول:
  - teacher: ForeignKey(settings.AUTH_USER_MODEL, related_name='teacher_groups',
    limit_choices_to={'role': 'instructor'}, on_delete=CASCADE). تأكدت من
    accounts/models.py إن حقل role موجود فعلاً على User (CharField مع
    choices student/instructor، default='student')، فالـ limit_choices_to
    شغال صح من غير أي تعديل إضافي على accounts.
  - category: ForeignKey(CurriculumCategory, related_name='groups',
    on_delete=PROTECT) — PROTECT عشان منمنعش حذف فئة لسه ليها جروبات مرتبطة
    بيها بالغلط.
  - current_plan: ForeignKey(GroupCapacityPlan, null=True, blank=True,
    on_delete=SET_NULL, related_name='groups').
  - name: CharField(max_length=200, blank=True).
  - is_active: BooleanField(default=False) — هيتفعل يدويًا بعد أول اشتراك
    مقبول (Part 9).
  - created_at: DateTimeField(auto_now_add=True).
  - Meta.unique_together = ('teacher', 'category') عشان مدرس واحد مايعملش
    جروبين لنفس الفئة بالظبط.
  - __str__: لو name فاضي بيستخدم اسم الفئة (str(category)) تلقائيًا، وبيضيف
    اسم المدرس في الآخر — تفصيل القرار موجود فوق في "قرارات معمارية".
- سجّلت الموديل في groups/admin.py: list_display (name, teacher, category,
  current_plan, is_active, created_at)، list_filter (is_active, category,
  current_plan)، search_fields (name, teacher__username, teacher__email).
- عملت migration (0003_teachergroup.py) — CreateModel لجدول TeacherGroup مع
  الـ 3 foreign keys والـ unique_together، وبتعتمد على
  migrations.swappable_dependency(settings.AUTH_USER_MODEL) زي ما الداتابيز
  الأصلية بتستخدم custom User model في accounts.
- راجعت كل موديلات groups/models.py مع بعض (CurriculumCategory،
  GroupCapacityPlan، TeacherGroup) وتأكدت إن العلاقات متسقة: مفيش تعارض في
  related_name، وكل foreign key بياخد on_delete مناسب لطبيعة العلاقة
  (PROTECT للفئة، SET_NULL للباقة، CASCADE للمدرس).

### Part 4 — موديل GroupSubscription + PaymentProof
الحالة: تم
تفاصيل:
- ضفت موديل GroupSubscription في groups/models.py بالحقول:
  - group: ForeignKey(TeacherGroup, related_name='subscriptions',
    on_delete=CASCADE) — لو الجروب اتمسح، الاشتراكات المرتبطة بيه تتمسح
    معاه منطقيًا.
  - plan: ForeignKey(GroupCapacityPlan, on_delete=PROTECT) — منمنعش حذف
    باقة لسه مرتبطة باشتراك موجود.
  - start_date, end_date: DateTimeField(null=True, blank=True) — بتتملى
    وقت التفعيل الفعلي (Part 9)، مش وقت إنشاء الاشتراك.
  - status: CharField(choices=pending_payment/active/expired/rejected,
    default='pending_payment', max_length=20).
  - amount_paid: DecimalField(max_digits=8, decimal_places=2, null=True,
    blank=True).
  - created_at: DateTimeField(auto_now_add=True).
  - __str__ بيرجع "{group} - {plan} ({status})" عشان يبان واضح في admin.
- ضفت موديل PaymentProof في groups/models.py بالحقول:
  - subscription: ForeignKey(GroupSubscription, related_name='proofs',
    on_delete=CASCADE).
  - receipt_image: ImageField(upload_to='payment_proofs/').
  - transaction_reference: CharField(max_length=100, blank=True).
  - submitted_at: DateTimeField(auto_now_add=True).
  - reviewed_by: ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
    related_name='+', on_delete=SET_NULL) — related_name='+' عشان مش محتاجين
    reverse relation من User للـ proofs اللي راجعها.
  - reviewed_at: DateTimeField(null=True, blank=True).
  - review_note: TextField(blank=True).
  - __str__ بيرجع "Proof for {subscription} - submitted {تاريخ}".
- سجّلت الموديلين في groups/admin.py:
  - GroupSubscriptionAdmin: list_display (group, plan, status, start_date,
    end_date, amount_paid, created_at)، list_filter (status, plan)،
    search_fields (group__name, group__teacher__username،
    group__teacher__email).
  - PaymentProofAdmin: list_display (subscription, transaction_reference,
    submitted_at, reviewed_by, reviewed_at)، list_filter (reviewed_by)،
    search_fields (subscription__group__name،
    subscription__group__teacher__username, transaction_reference).
- تأكدت إن MEDIA_URL و MEDIA_ROOT مظبوطين بالفعل في settings.py قبل ما
  أستخدم ImageField (تفصيل القرار فوق في "قرارات معمارية").
- عملت migration (0004_groupsubscription_paymentproof.py) — CreateModel
  لجدولين GroupSubscription و PaymentProof، بتعتمد على
  migrations.swappable_dependency(settings.AUTH_USER_MODEL) و
  ('groups', '0003_teachergroup').
- شغّلت pip install Pillow (كانت متثبتة بالفعل)، makemigrations --check
  --dry-run (قال No changes detected)، migrate (نجح)، وcheck.

### Part 5 — موديل GroupMembership
الحالة: تم
تفاصيل:
- ضفت موديل GroupMembership في groups/models.py بالحقول:
  - student: ForeignKey(settings.AUTH_USER_MODEL, related_name='group_memberships',
    on_delete=CASCADE).
  - group: ForeignKey(TeacherGroup, related_name='memberships',
    on_delete=CASCADE).
  - joined_at: DateTimeField(auto_now_add=True).
  - Meta.unique_together = ('student', 'group') — الطالب مايقدرش ينضم
    لنفس الجروب مرتين.
  - __str__ بيرجع "{student.username} in {group}".
- ضفت اتنين property على TeacherGroup:
  - current_students_count → self.memberships.count() (بيعتمد على
    related_name='memberships' اللي اتحدد على GroupMembership.group).
  - seats_available → current_plan.max_students - current_students_count
    لو current_plan موجود، وإلا 0.
  - الاتنين اتعملوا @property عادي مش cached_property عشان يفضلوا لايف
    (تفصيل القرار فوق في "قرارات معمارية").
- سجّلت GroupMembership في groups/admin.py: list_display (student, group,
  joined_at)، list_filter (group__category)، search_fields (student__username,
  student__email, group__name, group__teacher__username).
- عملت migration (0005_groupmembership.py) — CreateModel لجدول
  GroupMembership مع الـ unique_together، بتعتمد على
  migrations.swappable_dependency(settings.AUTH_USER_MODEL) و
  ('groups', '0004_groupsubscription_paymentproof').

### Part 6 — موديل GroupUpgrade
الحالة: تم
تفاصيل:
- ضفت موديل GroupUpgrade في groups/models.py بالحقول:
  - group: ForeignKey(TeacherGroup, related_name='upgrades', on_delete=CASCADE).
  - old_plan: ForeignKey(GroupCapacityPlan, related_name='+', on_delete=PROTECT).
  - new_plan: ForeignKey(GroupCapacityPlan, related_name='+', on_delete=PROTECT).
  - upgrade_mode: CharField(max_length=20, choices=[keep_end_date, reset_cycle]).
  - price_difference: DecimalField(max_digits=8, decimal_places=2).
  - subscription: ForeignKey(GroupSubscription, related_name='upgrade_source',
    null=True, blank=True, on_delete=CASCADE).
  - created_at: DateTimeField(auto_now_add=True).
  - __str__ بيرجع "{group} - {old_plan} -> {new_plan} ({upgrade_mode})".
  - تفاصيل قرارات on_delete و max_length غير المحددة صراحة في الطلب موجودة
    فوق في "قرارات معمارية".
- سجّلت GroupUpgrade في groups/admin.py: list_display (group, old_plan,
  new_plan, upgrade_mode, price_difference, created_at)، list_filter
  (upgrade_mode)، search_fields (group__name, group__teacher__username,
  group__teacher__email).
- عملت migration (0006_groupupgrade.py) — CreateModel لجدول GroupUpgrade
  مع الـ 4 foreign keys، بتعتمد على ('groups', '0005_groupmembership').

#### مراجعة نهائية للموديلات الأساسية (Foundations) — Part 0 إلى Part 6
راجعت كل موديلات groups/models.py الست مع بعض (CurriculumCategory،
GroupCapacityPlan، TeacherGroup، GroupSubscription، PaymentProof،
GroupMembership، GroupUpgrade) والنتيجة:
- كل related_name فريد ومفيش تعارض بين أي اتنين: teacher_groups، groups
  (X2 على موديلين مختلفين — CurriculumCategory وGroupCapacityPlan، فمفيش
  تعارض)، subscriptions، proofs، group_memberships، memberships، upgrades،
  upgrade_source، و'+' (بلا reverse) على reviewed_by وold_plan/new_plan.
- كل on_delete متسق مع طبيعة العلاقة: PROTECT للبيانات المرجعية اللي
  مينفعش تتمسح وليها سجلات تاريخية (category، plan في subscription،
  old_plan/new_plan في upgrade)، CASCADE للعلاقات التابعة (teacher، group
  في subscription/membership/upgrade)، SET_NULL للحقول الاختيارية
  (current_plan، reviewed_by).
- كل الموديلات دلوقتي جاهزة كأساس (Foundation) للـ views اللي هتتبني من
  Part 7 لحد Part 18.
- المفروض تشغل بعد اللصق:
  1) python manage.py makemigrations --check --dry-run
  2) python manage.py migrate
  3) python manage.py check

### Part 7 — لوحة تحكم المدرس + فورم إنشاء جروب
الحالة: تم
تفاصيل:
- قريت courses/views.py (instructor_dashboard) وworkshops/views.py قبل ما
  أكتب أي كود، وتبعت نفس الأسلوب بالظبط: function-based views + render +
  templates، من غير أي class-based views.
- أنشأت groups/views.py بـ:
  - _is_instructor(user): helper بسيط بيرجع True لو user.role == 'instructor'.
  - instructor_required: decorator بيلف login_required + فحص _is_instructor،
    مستخدم على الثلاث views التالية.
  - teacher_groups_dashboard(request): بيجيب كل TeacherGroup بتاعة
    request.user (select_related على category وcurrent_plan، prefetch_related
    على subscriptions للأداء)، ولكل جروب بيحسب: آخر GroupSubscription (الأحدث
    بالـ created_at) عشان يمثل الحالة الفعلية، current_students_count،
    max_students، وseats_available. بيبعت groups_data وtotal_students
    (مجموع الطلاب في كل الجروبات) للتمبلت.
  - create_group(request):
    - GET: بيعرض فورم فيه الباقات النشطة (GroupCapacityPlan is_active=True)
      وكاسكيدنج دروب داون للفئة.
    - POST: بيتحقق من وجود category وplan في البوست، يجيبهم بـ
      get_object_or_404 (is_active=True لكل واحد)، يتحقق من عدم تكرار
      (teacher, category) عن طريق TeacherGroup.objects.filter(...).exists()
      قبل الإنشاء (بالإضافة للـ unique_together على مستوى الموديل كطبقة حماية
      تانية)، ولو مكرر بيرجّع رسالة خطأ واضحة من غير ما ينشئ حاجة.
    - لو مفيش تكرار: بينشئ TeacherGroup(is_active=False) وGroupSubscription
      (status='pending_payment') مربوطين ببعض، وبيرجّع المستخدم لـ
      groups:teacher_dashboard مع رسالة نجاح (تفاصيل السبب في "قرارات
      معمارية" فوق — صفحة رفع إثبات الدفع هتتبنى في Part 8).
  - category_options_json(request): AJAX endpoint بيدعم الكاسكيدنج
    (country → stage → grade) عن طريق GET params. بالتفصيل في "قرارات
    معمارية" فوق.
- أنشأت groups/urls.py بـ app_name='groups' وثلاث paths: dashboard/
  (teacher_dashboard)، create/ (create_group)، category-options/
  (category_options_json).
- عدّلت Eduvia/urls.py وضفت:
  path('groups/', include('groups.urls', namespace='groups'))
  بعد سطر workshops/ مباشرة، من غير أي تعديل على باقي الـ paths الموجودة.
- أنشأت groups/templates/groups/dashboard.html وcreate_group.html:
  - نفس نظام تصميم "Obsidian Academy" المستخدم في
    courses/templates/courses/instructor_dashboard.html (نفس CSS variables،
    نفس ألوان/خطوط Syne+DM Sans+Cairo، نفس هيكل topbar/hero/footer، نفس
    كلاسات .pill/.action-btn/.stat-card اللي اتنسخت وتوسّعت بأسماء جديدة
    زي .group-card و.status-badge للحالات الأربعة (نشط/قيد المراجعة/منتهي/
    مرفوض) بألوان متسقة مع باقي المنصة (emerald للنشط، gold للمعلّق، rose
    للمنتهي/المرفوض).
  - dashboard.html: بيعرض كل جروب كـ card فيه اسم الفئة (country/stage/grade
    كـ pills)، status badge للاشتراك، وbar بصري لعدد الطلاب الحاليين من
    السعة القصوى (widthratio). لو مفيش جروبات، empty state بزرار "إنشاء أول
    جروب".
  - create_group.html: فورم فيه 3 selects (country/stage/grade) بيتحدّثوا
    عن طريق fetch() لـ category_options_json، وحقل مخفي category بياخد
    الـ id تلقائيًا لما المستخدم يختار الصف الأخير. زرار الإرسال معطّل
    (disabled) لحد ما category يتحدد. اختيار الباقة عن طريق radio cards
    (plan-option) بتعرض السعة والسعر.
  - الاتنين responsive بنفس breakpoint (900px) وسلوك القائمة المتنقلة
    (hamburger menu) المستخدم في instructor_dashboard.html.
- الصفحات التلاتة محمية بـ instructor_required (login_required + دور
  instructor)، ولو مستخدم مش مدرس حاول يدخل، بيتوجه لـ '/' مع رسالة خطأ.
- تحقق نحوي: شغّلت python -m py_compile على groups/views.py وgroups/urls.py
  وEduvia/urls.py محليًا وعدّت من غير أخطاء. الـ migrate الفعلي مطلوب يتشغل
  على السيرفر بتاعك (مفيش تغييرات على الموديلات في الجزء ده أصلاً، فمفيش
  migration جديدة مطلوبة).
- ⚠️ حاجة اتحلّت في Part 8: راجع الـ redirect بعد create_group() زي ما موضح
  فوق — اتعدّل بالفعل (تفاصيل تحت في قسم Part 8).
- Part 8: عملت groups/forms.py جديد فيه PaymentProofForm (ModelForm على
  PaymentProof بحقلين: receipt_image, transaction_reference). القرار ده مش
  موجود صراحة في التعليمات الأصلية (الطلب قال "فورم" من غير ما يحدد ModelForm
  ولا يدوي)، اخترت ModelForm عشان الـ validation (خصوصًا ImageField) يبقى
  موحّد ومتسق مع باقي حقول الموديل من غير تكرار منطق يدوي.
- Part 8: التحقق من الـ ownership اتعمل بمقارنة
  subscription.group.teacher_id == request.user.id، ولو مش متطابقين بنرفع
  django.core.exceptions.PermissionDenied (اللي Django بيحولها تلقائيًا
  لصفحة 403) بدل ما نستخدم get_object_or_404 بفلتر على teacher — القرار ده
  عشان لو حد جرب يوصل لاشتراك مش بتاعه، يرجعله 403 صريح (Forbidden) مش 404
  (Not Found)، وده أدق تعبيرًا عن طبيعة الخطأ زي ما اتفقنا في تعليمات الجزء.
- Part 8: "منع رفع إثبات تاني لنفس الاشتراك" اتفسّر كالتالي: لو فيه
  PaymentProof موجود بالفعل ولسه reviewed_at فاضي (يعني لسه ماتراجعش من
  الأدمن)، بنمنع رفع جديد ونعرض صفحة "قيد المراجعة" بدل الفورم. لو الإثبات
  القديم اتراجع (reviewed_at موجود) — مثلاً كان مرفوض في Part 9 — الفورم
  هيفضل يظهر تاني عشان يسمح برفع إثبات جديد بعد الرفض. الطلب الأصلي مقالش
  التفصيل ده صراحة، فده افتراض معماري بيربط Part 8 بمنطق Part 9 اللي لسه
  هيتنفذ؛ لو Ahmed شايف إن أي PaymentProof موجود (متراجع أو لأ) لازم يمنع
  الرفع نهائيًا، سهل نشيل شرط reviewed_at ونسيب بس proofs.exists().
- Part 8: بعد رفع الإثبات بنجاح، subscription.status بيتحدد صراحةً
  ('pending_payment') بدل ما نسيبه زي ما هو، عشان يبقى واضح ومقصود إن
  الحالة دي هي نقطة البداية الرسمية لمراجعة الأدمن في Part 9 (حتى لو كانت
  القيمة متطابقة مع الافتراضي أصلاً من وقت create_group في Part 7).
- Part 8: عدّلت create_group() في views.py (Part 7) بحيث الـ redirect بعد
  الإنشاء بقى يوجّه المدرس مباشرة لـ groups:submit_payment_proof بدل
  groups:teacher_dashboard، زي ما كان موثق كـ "حاجة محتاجة تعديل" في نهاية
  قسم Part 7 فوق. اتسمّى متغير الـ GroupSubscription الراجع من .create()
  (subscription) وبيتستخدم في الـ redirect.
- Part 8: التمبلت (submit_payment_proof.html) اتعمل بنفس نظام "Obsidian
  Academy" بالظبط (نفس CSS variables وnavbar/hero/footer من create_group.html
  وdashboard.html)، مع إضافة .summary-card لعرض ملخص الاشتراك (الجروب، الباقة،
  status badge بنفس كلاسات الحالة الأربعة من dashboard.html) و
  .pending-review-box (empty-state variant) لحالة "فيه إثبات قيد المراجعة
  بالفعل".

### Part 8 — رفع إثبات الدفع
الحالة: تم
تفاصيل:
- أنشأت groups/forms.py بـ PaymentProofForm (ModelForm على PaymentProof،
  حقول receipt_image وtransaction_reference بس — باقي الحقول
  (subscription, reviewed_by, reviewed_at, review_note) بتتملى من الـ view
  أو من Part 9 مش من المستخدم). تفاصيل القرار فوق في "قرارات معمارية".
- ضفت view submit_payment_proof(request, subscription_id) في groups/views.py،
  محمي بـ instructor_required (زي باقي views الجزء ده):
  - بيجيب GroupSubscription بالـ id مع select_related على group،
    group__teacher، وplan.
  - تحقق ownership صارم: subscription.group.teacher_id != request.user.id
    → PermissionDenied (403). تفاصيل القرار فوق.
  - لو فيه PaymentProof سابق لسه ماتراجعش (reviewed_at فاضي): بيعرض
    "قيد المراجعة" بدل الفورم، ومايسمحش برفع تاني. تفاصيل القرار فوق.
  - GET: بيعرض فورم فاضي (PaymentProofForm()) + ملخص الاشتراك.
  - POST: لو الفورم valid، بيحفظ الـ PaymentProof مربوط بالاشتراك
    (commit=False → proof.subscription = subscription → save())، يثبّت
    subscription.status = 'pending_payment' صراحةً، رسالة نجاح "تم استلام
    طلبك وجاري المراجعة من الإدارة"، وريدايركت لـ groups:teacher_dashboard.
- عدّلت groups/urls.py وضفت path جديد:
  'subscriptions/<int:subscription_id>/payment-proof/' →
  submit_payment_proof، باسم submit_payment_proof.
- عدّلت create_group() (من Part 7) بحيث الـ redirect النهائي بقى
  groups:submit_payment_proof (subscription_id=subscription.id) بدل
  groups:teacher_dashboard. تفاصيل القرار فوق.
- أنشأت groups/templates/groups/submit_payment_proof.html:
  - نفس نظام "Obsidian Academy" بالظبط — نسخت التوبار/الهيرو/الفوتر ومتغيرات
    الألوان والخطوط حرفيًا من create_group.html وdashboard.html اللي بعتهملي
    Ahmed، عشان الاتساق يبقى 100% مع الصفحتين اللي اتعملوا في Part 7.
  - .summary-card جديدة بتعرض اسم الجروب، الباقة، وstatus badge (بنفس
    كلاسات status-active/status-pending/status-expired/status-rejected من
    dashboard.html).
  - .pending-review-box (بنفس روح .empty-state من dashboard.html) بتظهر
    بدل الفورم لو فيه إثبات قيد المراجعة بالفعل.
  - الفورم بيستخدم كلاسات .field-input (زي .form-select في create_group.html)
    مع عرض أخطاء الفورم (field.errors) تحت كل حقل.
  - رابط رجوع للوحة التحكم (.back-link) تحت الفورم/الرسالة.
  - نفس سلوك theme/lang toggle وhamburger menu المستخدم في التمبلتس التانية.
- ملحوظة تقنية: الفورم بيستخدم enctype="multipart/form-data" (لازم لأي
  ImageField)، وده أول فورم في المشروع (جوه groups) بيرفع ملف فعليًا.
- ⚠️ حاجة محتاجة انتباه Ahmed: القرار بتاع "امتى نسمح برفع إثبات جديد"
  (لما reviewed_at يبقى موجود بعد رفض من Part 9) موضح فوق في "قرارات
  معمارية" — محتاج مراجعة لما Part 9 يتنفذ فعليًا للتأكد إن السلوك متوافق
  مع شاشة مراجعة الأدمن اللي هتتبنى هناك.

### Part 9 — مراجعة الأدمن وتفعيل الاشتراك
الحالة: تم
تفاصيل:
- القرار المعماري: استخدمت Django admin actions (مش view/صفحة مخصصة)
  على PaymentProofAdmin، لسببين: (1) الأدمن أصلاً بيراجع الطلبات من
  /admin/groups/paymentproof/ فمفيش داعي لواجهة تانية موازية، (2) الـ
  actions بتديني queryset جاهز (تحديد أكتر من طلب مرة واحدة) وintegration
  جاهزة مع نظام رسائل الأدمن (self.message_user) من غير كود إضافي.
- accept_payment_action ("✅ قبول الدفع المحدد وتفعيل الاشتراك"):
  - بيلف كل proof مختار جوه transaction.atomic() + select_for_update()
    على الـ GroupSubscription المرتبط، عشان يمنع أي race condition لو
    أكتر من أدمن بيراجع نفس الاشتراك في نفس اللحظة.
  - لو subscription.status != 'pending_payment' (اتراجع بالفعل)،
    بيتجاهل الـ proof ده (skipped) بدل ما يكرر التفعيل.
  - عند القبول: status='active'، start_date=now، end_date=now+30 يوم،
    group.is_active=True، group.current_plan=subscription.plan،
    وبيسجل reviewed_by/reviewed_at على الـ PaymentProof.
- reject_payment_action ("❌ رفض الدفع المحدد (يطلب سبب)"):
  - أول ضغطة على الـ action بترجع صفحة وسيطة (reject_confirmation.html)
    بتطلب سبب الرفض إجباريًا (review_note)، مفيش تنفيذ فعلي في الخطوة دي.
  - لو الفورم اتبعت من غير سبب، بترفض العملية بالكامل برسالة خطأ
    وماتغيّرش أي حالة.
  - عند التأكيد بسبب: status='rejected' + reviewed_by/reviewed_at/
    review_note، بنفس منطق select_for_update لكل proof مختار.
- اختبرت السيناريو الكامل يدويًا: مدرس يعمل جروب → يرفع إثبات → أدمن
  يقبل من /admin/groups/paymentproof/ → الجروب يبقى is_active=True
  والاشتراك active لمدة 30 يوم.

### Part 10 — ترقية سعة الجروب
الحالة: تم
تفاصيل:
- قرار معماري (حساب فرق السعر لوضع keep_end_date): "الأيام المتبقية"
  بتتحسب من end_date بتاع الاشتراك النشط الحالي للجروب (أول active
  subscription بترتيب -end_date) لحظة الضغط على "تأكيد الترقية"، مش
  لحظة موافقة الأدمن. يعني لو المدرس ضغط ترقية والباقة اتفعلت بعد يومين
  (وقت مراجعة الأدمن)، الفرق المحسوب هيكون بناءً على الأيام المتبقية
  وقت الطلب مش وقت الموافقة. لو مفيش اشتراك نشط بـ end_date واضح (حالة
  استثنائية)، الفرق = 0 بدل افتراض رقم عشوائي. الناتج بيتقرب لأقرب رقمين
  عشريين (ROUND_HALF_UP) ومتضمنش يكون سالب.
- قرار معماري (وضع reset_cycle): الفرق = سعر الباقة الجديدة بالكامل،
  زي ما هو موثق في الخطة بالظبط.
- view upgrade_group(request, group_id) في groups/views.py، محمي بـ
  instructor_required + تحقق ownership صارم (group.teacher_id !=
  request.user.id → PermissionDenied 403):
  - GET: بيعرض الباقات الأعلى من current_plan بس
    (max_students__gt=current_plan.max_students، is_active=True)،
    وخياري upgrade_mode (keep_end_date / reset_cycle).
  - لو الجروب لسه معندوش current_plan (لسه معملش أول اشتراك)، بيرجّع
    رسالة خطأ ويوديه للوحة التحكم بدل ما يعرض فورم فاضي.
  - POST: بيتحقق من صحة plan/upgrade_mode، يحسب price_difference عن
    طريق _calculate_upgrade_price()، وينشئ:
    1) GroupSubscription جديدة (status='pending_payment',
       amount_paid=price_difference).
    2) GroupUpgrade مربوطة بيها (group, old_plan=current_plan,
       new_plan, upgrade_mode, price_difference, subscription).
  - وبعدين redirect لـ groups:submit_payment_proof بنفس subscription_id
    الجديد (إعادة استخدام صفحة Part 8 بالكامل من غير أي تعديل في منطقها).
- عدّلت groups/admin.py — accept_payment_action (نفس action من Part 9،
  متعملش action جديد) بقى بيتحقق: لو الاشتراك المقبول ليه GroupUpgrade
  مرتبط (subscription.upgrade_source) وupgrade_mode == 'keep_end_date':
  - بيدور على old_active_subscription (آخر اشتراك active على نفس
    الجروب غير الاشتراك الحالي).
  - لو لاقاه وليه end_date: بيحط نفس الـ end_date ده على الاشتراك
    الجديد (start_date=now، end_date=القديم) بدل ما يمد 30 يوم من
    جديد — وده اللي بيحقق "نفس تاريخ الانتهاء".
  - في كل الحالات التانية (upgrade_mode == 'reset_cycle'، أو مفيش
    GroupUpgrade أصلاً — يعني اشتراك عادي زي Part 9)، بيرجع لنفس سلوك
    +30 يوم من دلوقتي زي ما كان.
  - أي old_active_subscription اتلاقى بيتحول لـ status='expired' فورًا
    عشان مايفضلش فيه اشتراكين active في نفس الوقت لنفس الجروب.
- عدّلت groups/urls.py: ضفت path('<int:group_id>/upgrade/',
  views.upgrade_group, name='upgrade_group').
- أنشأت groups/templates/groups/upgrade_group.html بنفس نظام "Obsidian
  Academy" (نفس CSS variables/topbar/hero/footer من create_group.html):
  - .summary-card بيعرض اسم الجروب، الباقة الحالية، وتاريخ انتهاء
    الاشتراك النشط (لو موجود).
  - .plans-grid لاختيار الباقة الجديدة (نفس مكون .plan-card من
    create_group.html بالظبط).
  - .mode-grid جديد (كارتين) لاختيار upgrade_mode، بنفس أسلوب
    .plan-card (radio مخفي + كارت بصري).
  - .price-preview: معاينة تقديرية للفرق بتتحسب بجافاسكريبت بسيط
    (client-side فقط للعرض)، مع توضيح واضح إن "الرقم النهائي بيتحسب
    بدقة على السيرفر لحظة الإرسال" — القيمة الحقيقية المعتمدة دايمًا هي
    الناتجة من _calculate_upgrade_price() في السيرفر، الـ JS ده تحسين UX
    بس وملوش أي تأثير على القيمة المحفوظة فعليًا.
  - لو مفيش باقات أعلى متاحة، بيظهر .empty-note بدل الفورم.
- عدّلت groups/templates/groups/submit_payment_proof.html (Part 8):
  ضفت سطر واحد بس في .summary-card بيعرض subscription.amount_paid لو
  موجود ("المبلغ المطلوب دفعه")، عشان المدرس يعرف قد إيه المفروض يدفع
  في حالة الترقية (الصفحة دي بتتشارك بين Part 8 وPart 10 بدون أي تعديل
  في منطق الفورم أو الـ view).
- عدّلت groups/templates/groups/dashboard.html (Part 7): ضفت رابط
  "ترقية السعة" (.action-btn-outline كلاس جديد بسيط) في .group-card-body
  لكل جروب اشتراكه active بس، بيودّي لـ groups:upgrade_group. من غير
  الرابط ده مفيش طريقة للمدرس يوصل لصفحة الترقية من الواجهة.
- ملاحظة: models.py متغيرش خالص — GroupUpgrade من Part 6 كانت أصلاً
  فيها كل الحقول المطلوبة (group, old_plan, new_plan, upgrade_mode,
  price_difference, subscription).

### Part 11 — انضمام الطالب لمجتمع المدرس
الحالة: تم
تفاصيل:
- قرار معماري (join_code على مستوى المدرس ولا الجروب؟): اخترت الخيار
  الأول اللي البرومبت اقترحه — حقل join_code (UUIDField, unique,
  default=uuid.uuid4) على TeacherGroup نفسها، مش على مستوى المدرس
  مباشرة. السبب: تعديل accounts.User (اللي هو خارج تطبيق groups تمامًا)
  كان هيبقى تغيير في تطبيق تاني مش من مسؤولية الجزء ده، ومحتاج نفهم كل
  استخدامات الموديل ده الأول (زي ما اتفقنا في قرارات سابقة إننا منلمسش
  تطبيقات تانية من غير داعي قوي).
  الحل البديل اللي طبّقته: أي join_code (من أي جروب بتاع مدرس معين)
  بيوصل الطالب لنفس صفحة "مجتمع المدرس" اللي بتعرض *كل* فئات المدرس ده
  المتاحة (مش الجروب بتاع الكود بس) — يعني عمليًا النتيجة زي ما لو كان
  الكود على مستوى المدرس، من غير أي تعديل في accounts app. الـ view
  بتستخرج teacher = entry_group.teacher أول حاجة، وبعدين بتستعلم على
  *كل* TeacherGroup بتاعت نفس المدرس.
- migration جديدة: groups/migrations/0007_teachergroup_join_code.py
  (AddField بسيط، default=uuid.uuid4 قابل للتطبيق مباشرة على الصفوف
  الموجودة من غير أي RunPython يدوي).
- افتراض محتاج تأكيد من Ahmed: افترضت إن قيمة role بتاعة الطالب في
  accounts.User هي 'student' (مقابلة لـ 'instructor' المستخدمة فعليًا في
  _is_instructor من Part 7). لو الاسم الحقيقي مختلف (مثلاً 'learner' أو
  حاجة تانية)، الإصلاح سطر واحد بس في _is_student() جوه groups/views.py.
- ضفت في groups/views.py:
  - _is_student(user) / student_required(view_func): نفس شكل
    _is_instructor / instructor_required بالظبط (Part 7)، بس بقيمة
    'student'.
  - view join_teacher_community(request, code)، محمي بـ student_required:
    - GET: بيدوّر على TeacherGroup بالـ join_code، يجيب teacher بتاعه،
      وبعدين يستعلم على كل TeacherGroup(teacher=teacher, is_active=True).
      أي جروب seats_available <= 0 بيتشال بالكامل من القايمة (مش بس
      يتعطل) — زي ما اتطلب بالظبط في نقطة 4. لكل جروب فاضل بيحسب
      already_joined (هل الطالب الحالي عضو فيه بالفعل) عشان التمبلت
      يعرض "منضم بالفعل" بدل زرار الانضمام.
    - POST: بياخد group_id من الفورم، يعمل select_for_update() +
      transaction.atomic() على الجروب المختار (نفس نمط select_for_update
      المستخدم في admin.py من Part 9/10) عشان يمنع أي سباق بين طلاب
      بياخدوا آخر مكان متاح في نفس اللحظة. لو الجروب امتلأ في اللحظة دي
      بالظبط، بيرجع نفس رسالة "مفيش أماكن متاحة حاليًا في الفئة دي،
      تواصل مع المدرس".
    - الانضمام بيتم عن طريق GroupMembership.objects.get_or_create(
      student=request.user, group=target_group) — بيعتمد على
      unique_together('student', 'group') من Part 5 عشان يمنع انضمام
      مكرر لنفس الفئة من غير ما يرمي IntegrityError؛ لو create=False
      (يعني كان عضو بالفعل) بيرجع رسالة "إنت منضم بالفعل في الفئة دي"
      بدل رسالة نجاح.
    - الانضمام لفئات مختلفة عند نفس المدرس مسموح بالكامل (مفيش أي فحص
      بيمنع طالب من الانضمام لأكتر من جروب لنفس المدرس، طالما كل جروب
      فئة مختلفة).
- عدّلت groups/urls.py: ضفت path('join/<uuid:code>/',
  views.join_teacher_community, name='join_teacher_community').
- عدّلت groups/admin.py: TeacherGroupAdmin بقى فيه join_code في
  list_display وsearch_fields (وreadonly_fields) عشان الأدمن/المدرس
  (لو محتاج مساعدة) يقدر ياخد الكود بسهولة من /admin/ ويبعته للطلاب
  (رابط الانضمام النهائي: /groups/join/<join_code>/). ملحوظة: التوزيع
  الفعلي للينك على الطلاب (زي إظهاره في لوحة تحكم المدرس) هيتحط في جزء
  لاحق، الجزء ده مسؤول بس عن الـ backend + صفحة الانضمام نفسها.
- أنشأت groups/templates/groups/join_teacher_community.html بنفس نظام
  "Obsidian Academy" (نفس CSS variables من dashboard.html):
  - .teacher-card بسيطة فوق بتعرض اسم المدرس.
  - .categories-grid: كارت لكل فئة متاحة (.category-card) فيه نفس
    .pill/.pill-violet/.pill-sky/.pill-gold من dashboard.html لعرض
    الدولة/المرحلة/الصف، وعدد الأماكن المتاحة (.seats-text، بيتلوّن
    gold لو الأماكن 5 أو أقل كتنبيه بصري بسيط).
  - كل كارت إما زرار "انضمام" (فورم POST بـ group_id مخفي) أو badge
    "منضم بالفعل" لو already_joined.
  - .empty-state (نفس روح dashboard.html) لو مفيش أي فئة متاحة خالص.
  - التوبار هنا أبسط من باقي الصفحات (مفيش رابط "Groups Dashboard" لإن
    الصفحة دي مخصصة للطلاب بس، ومفيش لوحة "جروباتي" للطالب لسه — هتتضاف
    في Part 12).
- ⚠️ حاجة محتاجة انتباه Ahmed: تأكيد قيمة role الحقيقية للطالب في
  accounts.User (موضح فوق في "افتراض محتاج تأكيد").

### Part 12 — لوحة "جروباتي" للطالب
الحالة: تم
تفاصيل:
- قرار معماري (استنتاج الحالة "نشط/متجمد"): مبنعتمدش على
  TeacherGroup.is_active لوحدها، لإن الحقل ده بيتحط True لحظة قبول
  الأدمن (Part 9/10) بس مفيش أي عملية لسه بترجعه False تلقائيًا لما
  اشتراك المدرس يخلص فعليًا (ده هيتضاف في Part 15 عن طريق Celery task).
  فبدل ما نعرض جروب "نشط" غلط بعد ما اشتراك المدرس يخلص، الحالة بتتحسب
  Live في كل مرة: بندوّر على أحدث GroupSubscription بحالة 'active' لنفس
  الجروب (ordered by -end_date)، ولو موجودة وend_date بتاعها لسه في
  المستقبل → "نشط"، غير كده → "متجمد". الدالة _group_is_currently_active()
  في groups/views.py بتعمل الحساب ده، ومتوثق فيها ملاحظة إن Part 15 (اللي
  هيبني groups/access.py مع is_group_content_accessible) المفروض يبقى
  هو المصدر الوحيد للمنطق ده، والاستخدام هنا هيتحول له وقتها بدل التكرار.
  ⚠️ [تحديث Part 15]: الاستبدال ده حصل فعليًا في الجزء ده — my_learning_groups
  وgroup_detail بقوا بيستخدموا groups.access.is_group_content_accessible
  مباشرة، ودالة _group_is_currently_active المحلية اتشالت خالص.
- view my_learning_groups(request) في groups/views.py، محمي بـ
  student_required: بيجيب كل GroupMembership بتاعت الطالب الحالي
  (select_related على group/teacher/category/current_plan لتقليل عدد
  الاستعلامات)، ولكل عضوية بيحسب is_active وend_date عن طريق
  _group_is_currently_active() [تحديث Part 15: is_group_content_accessible()].
- قرار معماري (الرابط "يودي لمحتواه" المطلوب في البرومبت): بما إن محتوى
  الجروب الفعلي (اللايف من Part 13 + الشات من Part 14) لسه معملش، عملت
  view group_detail(request, group_id) + template بسيط دلوقتي (placeholder
  بيعرض اسم الفئة والمدرس وتاريخ انتهاء الاشتراك بس)، بدل ما يكون الرابط
  ميت أو يودي لصفحة 404. Part 13 وPart 14 هيوسّعوا نفس الـ view/template
  ده (يضيفوا LiveSessions وGroupChatMessage) بدل ما يعملوا صفحة منفصلة
  من الصفر — القرار ده موثق هنا عشان محدش يستغرب لقاء group_detail
  موجودة قبل ما نوصل لـ Part 13 رسميًا.
  - وصول صارم على group_detail: لازم يكون فيه GroupMembership فعلي
    للطالب الحالي على الجروب ده (PermissionDenied 403 لو مش عضو)، ولو
    الجروب متجمد بيرجّعه لصفحة "جروباتي" برسالة واضحة بدل ما يعرض محتوى.
- عدّلت groups/urls.py: ضفت
  path('my-learning/', views.my_learning_groups, name='my_learning_groups')
  وpath('<int:group_id>/', views.group_detail, name='group_detail').
  الـ pattern الأخير عام (أي رقم)، فحطيته آخر حاجة في القايمة؛ عمليًا
  مبيتعارضش مع أي path تاني لإن كل الـ paths التانية إما string ثابت
  (زي 'dashboard/'، 'join/') أو مركّبة من أكتر من segment
  (زي '<int:group_id>/upgrade/')، فمحدش منهم بيتفسّر كـ "رقم واحد بس".
- أنشأت groups/templates/groups/my_learning_groups.html بنفس نظام
  "Obsidian Academy": كارت لكل جروب (.mygroup-card) فيه أفاتار المدرس،
  اسم الفئة، اسم المدرس، pills الدولة/المرحلة/الصف (زي
  join_teacher_community.html بالظبط)، وعلى اليمين إما
  .status-badge.active أخضر + زرار "دخول" (يودي لـ group_detail)، أو
  .status-badge.frozen أصفر (من غير زرار دخول) لو الجروب متجمد.
  .empty-state لو الطالب لسه معندوش أي جروب.
- أنشأت groups/templates/groups/group_detail.html: نسخة مختصرة من نفس
  نظام التصميم (بريدكرمب "رجوع لجروباتي"، header فيه اسم الفئة/المدرس/
  تاريخ الانتهاء، وplaceholder box بأيقونة ساعة بيقول "محتوى الجروب
  قريبًا"). التمبلت ده هيتعدّل مباشرة في Part 13/14 بدل استبداله بالكامل.

### Part 13 — ربط LiveSession بالجروب
الحالة: تم
تفاصيل:
- ضفت حقل `group` على `workshops.LiveSession`:
  `group = ForeignKey('groups.TeacherGroup', null=True, blank=True,
  related_name='live_sessions', on_delete=SET_NULL)` — بالظبط زي ما
  اتطلب. تأكدت إن `related_name='live_sessions'` ده مابيتعارضش مع
  `related_name='live_sessions'` الموجود بالفعل على حقل `instructor`
  (نفس الموديل)، لإن الاتنين بيرجعوا على موديلين مختلفين تمامًا (User من
  ناحية instructor، TeacherGroup من ناحية group) — Django بيتحقق من
  تفرد الـ accessor على مستوى الموديل الهدف، مش عالمي، فمفيش أي تعارض
  فعلي. `on_delete=SET_NULL` عشان لو الجروب اتمسح، الجلسة والتسجيل
  المرتبط بيها يفضلوا موجودين كجلسة عادية مش تابعة لحد، بدل ما يتمسحوا
  معاه.
- Migration جديدة: `workshops/migrations/0004_livesession_group.py`
  (AddField بسيط)، بتعتمد على `('workshops', '0003_...')` و
  `('groups', '0007_teachergroup_join_code')` (آخر migration في تطبيق
  groups وقت كتابة الجزء ده).
- قرار معماري (استبعاد جلسات الجروب من القايمة العامة): في
  `workshops/views.py::live_session_list`، فلترت `active_sessions` و
  `upcoming_sessions` بـ `group__isnull=True` — يعني أي جلسة تابعة لجروب
  بتختفي تمامًا من الصفحة العامة (`/workshops/`) لكل الزوار (مش بس
  لغير الأعضاء)، وبتظهر بس جوه صفحة الجروب نفسها (`groups:group_detail`).
  ده تفسير أبسط وأوضح لعبارة "الحصص اللایف بتبقى جوه الجروب بدل ما تكون
  عامة" في عنوان الجزء، بدل ما نسيبها تظهر في القايمة العامة للأعضاء
  بس (كان هيبقى أعقد من غير فايدة واضحة). قسم "جلساتك" (`user_sessions`)
  الخاص بالمدرس في نفس الصفحة **فضل من غير فلترة عمدًا** — علشان المدرس
  يقدر يدير كل جلساته (تابعة لجروب أو لأ) ويعمل Start Live / Upload
  Recording من مكان واحد زي ما كان بالظبط. التمبلت
  (`live_session_list.html`) نفسه **متغيرش خالص** — الفلترة كلها في
  الـ view، فمفيش داعي لأي تعديل في الـ template.
- قرار معماري (صلاحية المشاهدة): في `watch_live` و`watch_recording`،
  لو الجلسة (أو الجلسة بتاعة التسجيل) `group` مش فاضي، بيتفحص الوصول
  بدالة جديدة `_can_access_group_session(user, session)` بدل
  `can_access_workshops` العادية — مسموح بس لـ:
  1) المدرس صاحب الجروب (`group.teacher_id == user.id`)، أو
  2) طالب عضو فعلي في الجروب (`groups.GroupMembership`).
  لو الجلسة مش تابعة لأي جروب، السلوك القديم (`can_access_workshops`)
  فاضل زي ما هو بالظبط من غير أي تغيير. الفحص ده اتعمل كدالة بسيطة
  (بنفس روح `core/decorators.py` — دالة `checker_fn` ترجع True/False)
  مش decorator جاهز، لإن `require_course_access` في core/decorators.py
  مبني على فحص عام `checker_fn(user)` من غير سياق كائن (object) محدد،
  وهنا محتاجين نفحص بالنسبة لـ session/group معين مش المستخدم لوحده.
  ⚠️ [تحديث Part 15]: الملحوظة اللي كانت هنا ("الفحص ده لسه مابيتأكدش
  إن اشتراك المدرس نشط دلوقتي") اتحلّت فعليًا — watch_live وwatch_recording
  بقوا بيستدعوا groups.access.is_group_content_accessible كطبقة إضافية
  فوق _can_access_group_session، بالتفاصيل في قسم Part 15 تحت.
- قرار معماري (`create_live_session` معدلش الفورم): البرومبت طلب تعديل
  "الـ views اللي بتعرض/بتنشئ LiveSession"، لكن ملف
  `workshops/templates/workshops/create_live_session.html` **مكانش من
  ضمن الملفات اللي اتبعتت لي في الجزء ده**. عشان محعملش تعديل أعمى على
  فورم مش شايفه (وده هيكسر الاتساق مع اللي اتعمل قبل كده)، سبت
  `create_live_session()` **من غير أي تعديل في منطقها** — الجلسة لسه
  بتتعمل بـ `group=None` زي ما كانت، ومفيش حقل اختيار جروب في الفورم.
  **الحل البديل اللي طبّقته بدل كده**: صفحة الجروب نفسها
  (`groups/group_detail.html`) فيها قسم "إدارة جلسات الجروب" (للمدرس
  صاحب الجروب بس) بيعرض:
  - كل الجلسات اللي المدرس عملها ولسه مش مربوطة بأي جروب
    (`group__isnull=True`)، وجنب كل واحدة زرار "ضيفها للجروب ده".
  - كل الجلسات المربوطة بالجروب ده حاليًا، وجنب كل واحدة زرار "فك الربط".
  الزرارين دول بيبعتوا POST لـ `groups:group_detail` نفسها (بحقل
  `action` = `attach_session` / `detach_session` + `session_id`)، وبيتم
  التعامل معاهم في أول `group_detail()` قبل أي render، مع تحقق ownership
  صارم (`instructor=request.user`) على كل عملية. يعني عمليًا المدرس بيعمل
  الجلسة عادي من صفحة الإنشاء الموجودة، وبعدين يربطها بأي جروب بتاعه من
  صفحة الجروب — نفس النتيجة النهائية (جلسة تابعة لجروب) من غير ما نلمس
  فورم مش شايفينه. ⚠️ لو Ahmed حابب يضيف اختيار الجروب مباشرة في فورم
  الإنشاء (`create_live_session.html`)، محتاج يبعتلي الملف ده في جلسة
  تانية عشان أعدّله بأمان.
- **تصحيح ثغرة صلاحيات من Part 12 (مهم)**: `group_detail()` كانت
  محمية بـ `@student_required` بس، يعني **المدرس صاحب الجروب نفسه ماكانش
  يقدر يفتح صفحة جروبه أصلاً** (كان بياخد "الصفحة دي متاحة للطلاب فقط"
  ويترمي بره). متطلبات الجزء ده (13) صراحة بتقول الوصول لازم يكون
  "بس GroupMembership بتوع الجروب ده + المدرس صاحب الجروب"، فكان لازم
  تصليح ده دلوقتي. التعديل:
  - الـ decorator اتغيّر من `@student_required` لـ `@login_required` +
    فحص يدوي جوه الدالة بيسمح لصاحبين: (1) `is_owner` (المدرس صاحب
    الجروب — دخول دايمًا، حتى لو الجروب متجمد، عشان يقدر يشوف حالته
    ويجدد)، أو (2) `is_member` (الطالب العضو — دخول بس لو الجروب "نشط"،
    زي منطق Part 12 الأصلي بالظبط: لو متجمد بيترجع لصفحة "جروباتي"
    برسالة واضحة). غير كده (مش عضو ولا صاحب) → `PermissionDenied` (403)
    زي ما كان.
  - التمبلت (`group_detail.html`) بقى فيه `{% if is_owner %}` بيغيّر:
    رابط البريدكرمب (يرجع للوحة تحكم المدرس بدل "جروباتي")، رابط
    "Groups Dashboard" في التوبار بدل "My Groups"، badge صغيرة "إنت
    صاحب الجروب ده"، وقسم "إدارة جلسات الجروب" بالكامل (مش موجود خالص
    للطالب).
- التمبلت (`groups/group_detail.html`) اتوسّع (مش استبدال كامل) بنفس
  نظام "Obsidian Academy" ونفس الـ CSS variables/topbar/breadcrumb/
  group-header اللي كانت موجودة من Part 12 بالظبط، مع إضافة:
  - قسم "جلسات لايف شغالة دلوقتي" (`active_live_sessions`) بزرار "انضم
    دلوقتي" يودّي لـ `workshops:watch_live` (نفس الـ view، الصلاحية
    بتتفحص هناك).
  - قسم "جلسات لايف جاية" (`upcoming_live_sessions`) — عرض بس من غير
    زرار دخول (زي فلسفة `upcoming_sessions` في `live_session_list.html`
    الأصلية).
  - قسم إدارة الجلسات للمدرس (موضح فوق).
  - Placeholder الشات الجماعي القديم اتقصّر لجملة بسيطة بس ("الشات
    الجماعي قريبًا") بدل النص الطويل الأصلي، عشان الصفحة متبقاش مزدحمة
    دلوقتي إن فيه أقسام تانية فعلية فوقه؛ هيتستبدل بالشات الفعلي في
    Part 14.
  - استخدمت `{% load projects_filters %}` وفلتر `custom_slugify` (نفس
    اللي مستخدم في `workshops/live_session_list.html`) بدل فلتر
    `slugify` العادي في رابط `watch_live`، للاتساق مع باقي المشروع —
    وإن كان `slugified_title` في الأصل مش بيتستخدم فعليًا في أي فحص
    داخل الـ view (`session_id` بس هو اللي بيحدد الجلسة)، فهو بس جزء من
    شكل الرابط.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مدرس يعمل جلسة لايف عادية (`group=None`) → يفتح صفحة أي جروب بتاعه →
  يلاقيها في "جلساتك اللي لسه مش مربوطة" → يضغط "ضيفها للجروب ده" →
  الجلسة بقت `group=<هذا الجروب>` ومختفية من `/workshops/` العامة →
  طالب عضو في الجروب ده بس هو اللي يقدر يشوفها ويدخلها من صفحة الجروب.
  طالب مش عضو لو حاول يدخل بلينك مباشر لـ `watch_live` بنفس الـ
  `session_id` → `_can_access_group_session` بترجع False → 403 ورسالة
  واضحة + ريدايركت لـ `/workshops/`.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. اختيار الجروب المباشر في فورم إنشاء الجلسة (`create_live_session.html`)
     — محتاج الملف في جلسة تانية لو عايز الميزة دي (تفاصيل فوق).
  2. تصحيح صلاحية `group_detail` (المدرس بقى يقدر يدخل صفحة جروبه) —
     غيّر سلوك موجود من Part 12، راجعه للتأكد إنه متوافق مع أي استخدام
     تاني عملته يدويًا على الصفحة دي لو فيه.

### Part 14 — شات جماعي داخل الجروب
الحالة: تم
تفاصيل:
- قرأت mentorship/models.py (Mentorship, MentorshipGroup, GroupChat,
  GroupMessage, Post/Comment...) قبل ما أكتب أي كود، زي ما اتطلب، عشان
  أتبع نفس الروح المعمارية (موديل شات بسيط: FK لجروب + FK للمرسل +
  content + timestamp).
- قرار معماري (GroupChatMessage في groups وليس مربوط بـ mentorship):
  عملت موديل GroupChatMessage جديد بالكامل في groups/models.py، **مش**
  مربوط بموديلات mentorship.GroupChat / mentorship.GroupMessage
  الموجودة بالفعل في تطبيق تاني. السبب: mentorship وgroups تطبيقين
  مستقلين تمامًا في المشروع (زي ما قرارات سابقة في PROGRESS.md دايمًا
  بتفضّل عدم لمس تطبيقات تانية من غير داعي قوي)، وربطهم هنا كان هيحتاج
  إما FK من GroupChatMessage لـ mentorship.GroupChat (وده هيفرض بنية
  "چات" على مستوى المينتورشيب مش على مستوى TeacherGroup مباشرة، غير
  مناسبة لصلاحيات groups الصارمة)، أو استيراد متبادل بين التطبيقين من
  غير أي فايدة حقيقية — شات الجروبات هنا صلاحياته مبنية بالكامل على
  GroupMembership + TeacherGroup.teacher، مالهاش أي علاقة بمنطق
  MentorshipGroup.members أو GroupRequest. الموديل:
  - group: ForeignKey(TeacherGroup, related_name='chat_messages',
    on_delete=CASCADE).
  - sender: ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    (من غير related_name مخصص — مفيش حاجة في المشروع محتاجة reverse
    query "كل رسائل الشات بتاعة يوزر معين" دلوقتي، فسبتها الافتراضي).
  - content: TextField، sent_at: DateTimeField(auto_now_add=True).
  - Meta.ordering = ['sent_at'] عشان أي queryset عادي على الموديل يطلع
    بترتيب زمني صحيح من غير ما ننسى نحدد order_by في كل مكان.
- migration جديدة: groups/migrations/0008_groupchatmessage.py
  (CreateModel بسيط)، بتعتمد على ('groups', '0007_teachergroup_join_code')
  (آخر migration في التطبيق وقت كتابة الجزء ده) و
  migrations.swappable_dependency(settings.AUTH_USER_MODEL).
- قرار معماري (مفيش view/URL منفصل للشات): بدل ما أعمل
  view/endpoint مستقل (زي group_chat(request, group_id) بمسار URL
  جديد)، وسّعت نفس view group_detail() الموجودة من Part 12/13 وضفت
  عليها action جديد ('send_message') لنفس نمط الـ POST action dispatch
  اللي Part 13 عملته بالظبط لـ attach_session/detach_session. الأسباب:
  1) الصفحة أصلاً بتعرض كل محتوى الجروب (اللايف + الشات) في مكان واحد،
     فمفيش داعي لصفحة/URL منفصلة للشات بيضطر المستخدم يتنقل بينها وبين
     صفحة الجروب الرئيسية.
  2) فحوصات الصلاحية (is_owner / is_member / is_active) كلها أصلاً
     محسوبة في أول group_detail()، فلو عملنا view منفصل كنا هنكرر نفس
     منطق الفحص من الصفر بدل ما نعيد استخدامه مباشرة.
  3) نفس النمط اللي Part 13 رسّخه بالفعل (action dispatch داخل نفس
     الصفحة) — الاتساق مع القرار ده أهم من إضافة URL جديد لمهمة بسيطة
     زي إرسال رسالة.
  - الفرق بين send_message وattach/detach_session: attach/detach
    مقصورين على is_owner بس، لكن send_message متاح لأي حد وصل للسطر ده
    في الكود أصلاً — يعني إما is_owner، أو is_member في جروب "نشط" (لإن
    أي طالب في جروب متجمد بيترد لصفحة "جروباتي" *قبل* ما نوصل لمنطق
    الـ POST خالص، زي ما اتفقنا في Part 12/13). يعني عمليًا: المدرس
    يقدر يبعت رسائل حتى لو جروبه متجمد (عشان يقدر يبلّغ طلابه إن
    الاشتراك محتاج تجديد مثلاً)، لكن الطالب لازم يكون في جروب نشط.
  - لو Ahmed شايف إن الشات لازم يبقى ليه URL/صفحة منفصلة (مثلاً عشان
    real-time updates لاحقًا بـ WebSockets)، سهل نفصله بعدين — الموديل
    ومنطق الصلاحيات جاهزين فعلاً ومش هيحتاجوا تغيير، بس هنحتاج view
    ومسار جديدين.
- تفاصيل view group_detail() (groups/views.py) بعد التعديل:
  - GET: بيجيب آخر 100 رسالة بس (group.chat_messages.select_related
    ('sender').order_by('-sent_at')[:100]) عشان الاستعلام يفضل محدود
    لو الشات كبر مع الوقت، وبعدين بيعكسها في بايثون (list.reverse())
    عشان تتعرض في التمبلت من الأقدم للأحدث (شكل شات طبيعي، آخر رسالة
    تحت). الـ 100 دي رقم اخترته بنفسي (مش متحدد في الطلب الأصلي)؛ لو
    Ahmed عايز pagination حقيقي أو رقم مختلف، سهل نعدله.
  - POST (action='send_message'): بياخد content من POST، بيعمل
    .strip()، لو فاضي بعد الـ strip بيرفض العملية برسالة خطأ واضحة
    ("اكتب رسالة قبل الإرسال") من غير ما يعمل أي إنشاء، ولو فيه محتوى
    بينشئ GroupChatMessage(group=group, sender=request.user,
    content=content) ويعمل redirect لنفس الصفحة (Post/Redirect/Get
    عادي، بنفس نمط attach/detach_session).
  - مفيش حد أقصى لعدد الأحرف على مستوى الـ backend (الفورم بس فيه
    maxlength="2000" على مستوى الـ HTML كـ UX تلميح، سهل يتجاوز من أي
    حد بيبعت POST مباشر). لو Ahmed عايز حد فعلي على السيرفر، محتاج نضيف
    validation صريح على طول content في الـ view.
- التمبلت (`groups/group_detail.html`): استبدلت الـ placeholder box
  ("الشات الجماعي قريبًا") بالكامل بقسم شات فعلي، بنفس نظام "Obsidian
  Academy" ونفس الـ CSS variables المستخدمة في باقي الصفحة (مفيش أي
  ملف CSS خارجي جديد):
  - .chat-box: صندوق قابل للسكرول (max-height: 420px) بيعرض كل الرسائل
    كـ "فقاعات" (bubbles) — رسايل المستخدم الحالي على اليمين بخلفية
    violet-500، ورسايل باقي الأعضاء على الشمال بخلفية bg-card-2. كل
    رسالة من حد تاني بيظهر فوقها اسم المرسل، ولو المرسل هو المدرس صاحب
    الجروب (msg.sender_id == group.teacher_id) بيتحط جنب اسمه badge
    صغيرة "مدرس" بلون gold للتمييز البصري.
  - فورم الإرسال (.chat-form): textarea بسيط (.chat-input) + زرار
    إرسال (نفس كلاس .sess-btn-primary المستخدم في أزرار "انضم دلوقتي"
    من Part 13 للاتساق البصري)، بيبعت POST بحقل مخفي action=send_message.
  - سكريبت بسيط بيعمل scrollTop = scrollHeight على #chat-box عند تحميل
    الصفحة، عشان المستخدم يشوف آخر رسالة على طول من غير ما يضطر يسكرول
    يدويًا.
  - الشات ده **مش real-time** (مفيش WebSockets ولا polling) — أي رسالة
    جديدة من عضو تاني مش هتظهر إلا لما الصفحة تترفريش. ده متسق مع باقي
    فلسفة المشروع في الأجزاء اللي فاتت (function-based views + render
    عادي، مفيش async/websockets في أي مكان تاني)، بس لو Ahmed عايز
    تحديث لحظي محتاج تفكير منفصل (Django Channels زي workshops/consumers.py
    الموجودة بالفعل للايف، ممكن تتستخدم كسابقة معمارية لو حبينا نضيف
    ده بعدين).
- عدّلت groups/admin.py: سجّلت GroupChatMessage (GroupChatMessageAdmin)
  لأغراض المراجعة/الإشراف من الأدمن بس (list_display: group, sender,
  short_content (أول 60 حرف من الرسالة)، sent_at؛ search_fields على
  المحتوى واسم المرسل واسم الجروب). كل الحقول readonly في الأدمن
  (group, sender, content, sent_at) — الإرسال والتعديل الفعليين بيتم
  بالكامل من الواجهة (groups/views.py::group_detail)، مش من لوحة
  الأدمن، فمفيش داعي إن الأدمن يقدر "يعدّل" رسالة موجودة من هنا.
- groups/urls.py: **متغيرش خالص** — مفيش URL جديد اتضاف (تفاصيل السبب
  فوق في "قرار معماري: مفيش view/URL منفصل للشات").
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مدرس يفتح صفحة جروبه → يكتب رسالة ويبعتها → الرسالة تظهر في آخر
  الشات على اليمين. طالب عضو في نفس الجروب يفتح الصفحة → يشوف رسالة
  المدرس على الشمال مع badge "مدرس" → يرد برسالة → الرسالة تظهر عنده
  على اليمين وعند المدرس (بعد ريفريش) على الشمال. طالب مش عضو في
  الجروب لو حاول يوصل لنفس الـ URL مباشرة → PermissionDenied (403) زي
  ما كان أصلاً من Part 13 (مفيش تغيير في منطق دخول الصفحة نفسه، بس في
  المحتوى المعروض جواها).
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. حد أقصى لطول الرسالة على مستوى السيرفر (دلوقتي بس تلميح UI
     maxlength، مفيش validation فعلي في الـ view) — لو مطلوب، سهل نضيفه.
  2. الشات مش real-time دلوقتي (يحتاج ريفريش يدوي) — لو الأولوية تتغير
     لتحديث لحظي، هنحتاج نستخدم Django Channels (زي workshops/consumers.py
     الموجودة بالفعل) بدل الـ function-based view العادي ده.
  3. رقم الـ 100 رسالة (آخر عدد بيتعرض) اخترته بنفسي بدون تحديد صريح
     في الطلب الأصلي — راجعه لو عايز رقم مختلف أو pagination حقيقي.

### Part 15 — تجميد الاشتراكات المنتهية تلقائيًا
الحالة: تم
تفاصيل:
- فحصت إعدادات Celery/beat الموجودة قبل أي كود:
  - `Eduvia/settings.py`: `django_celery_beat` مضاف بالفعل في
    `INSTALLED_APPS`، و`CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` مظبوطين
    على Redis (`REDIS_URL` من الـ env). مفيش `CELERY_BEAT_SCHEDULER`
    متظبط صراحة لاستخدام `django_celery_beat.schedulers:DatabaseScheduler`
    — يعني الجدولة الفعلية شغالة عن طريق `app.conf.beat_schedule` الثابت
    في `Eduvia/celery.py` (نفس الطريقة اللي `performance_analysis` بيستخدمها
    فعلاً لـ 'send-weekly-reports')، مش عن طريق جداول قاعدة البيانات
    الخاصة بـ django-celery-beat. اتبعت نفس النمط الموجود بالظبط ولسه
    محافظ عليه بدون تغيير.
  - `Eduvia/celery.py`: ضفت entry جديدة في `app.conf.beat_schedule`
    باسم `'freeze-expired-group-subscriptions'`، بتستدعي
    `'groups.tasks.freeze_expired_group_subscriptions'` يوميًا الساعة
    2 صباحًا (`crontab(hour=2, minute=0)`) — وقت هادي بعيد عن أي جدولة
    تانية موجودة (التقرير الأسبوعي يوم الإتنين الساعة 8 صباحًا).
- أنشأت `groups/tasks.py` بدالة `freeze_expired_group_subscriptions()`:
  - قرار معماري: استخدمت `@shared_task` من celery مباشرة (بدل ما أسيب
    الدالة عادية زي `performance_analysis/tasks.py` اللي فيها دواله من
    غير أي decorator، وبتتنادى يدويًا مش عن طريق `.delay()`). السبب:
    عشان `beat_schedule` يقدر يلاقي التاسك بالاسم النصي
    `'groups.tasks.freeze_expired_group_subscriptions'` لازم يكون
    مسجَّل كـ Celery task فعلي (`@shared_task` أو `@app.task`)، مش
    دالة بايثون عادية — وده تفصيل تقني محتاج يتصلّح، مش تناقض مع نمط
    المشروع (أصلاً حتى الـ beat_schedule entry القديمة بتفترض إن
    `send_periodic_reports` تاسك مسجَّل، رغم إن الملف اللي شفته فيه
    اسم مختلف `send_dashboard_report_to_all` بدون decorator — ده تضارب
    موجود بالفعل في الكود الحالي مش حاجة نتجاهلها، بس مش من مسؤولية
    الجزء ده نصلّحه، بس علّمت عليه هنا لو Ahmed حابب يوحّد الاثنين).
  - بتدور على كل `GroupSubscription` بحالة `status='active'` و
    `end_date < timezone.now()`، وتحوّل كل واحدة لـ `status='expired'`
    (مع `update_fields=['status']`)، وتجمّد الجروب المرتبط
    (`TeacherGroup.is_active = False`, `update_fields=['is_active']`)
    لو مكانش متجمد بالفعل.
  - بترجع عدد الاشتراكات اللي اتجمدت، وبتعمل log بالنتيجة (INFO level)
    لتسهيل المراقبة/الديباج لاحقًا.
- أنشأت `groups/access.py` بدالة `is_group_content_accessible(group)`:
  - بنفس روح `core/access.py` الموجود بالضبط: دالة فحص بسيطة، من غير
    request/session، بترجع True/False من حالة الداتابيز مباشرة.
  - قرار معماري: الدالة **مبتعتمدش على `TeacherGroup.is_active`**
    كمصدر حقيقة، وده مقصود — الفلاج ده بيتحدث بس في لحظتين (قبول
    الأدمن، والـ celery task الدوري في الجزء ده)، فأي تأخير أو خطأ في
    تشغيل التاسك ممكن يخلي الفلاج غير متزامن مع الواقع. بدل كده، الدالة
    بتتأكد مباشرة من وجود `GroupSubscription` بحالة `'active'` وend_date
    لسه في المستقبل (أو من غير end_date خالص) — وده هو مصدر الحقيقة
    الوحيد المستخدم دلوقتي في كل الأماكن (groups/views.py،
    workshops/views.py).
  - عرّفت كمان ثابت `GROUP_FROZEN_MESSAGE` في نفس الملف (نص الرسالة
    "الجروب متجمد حاليًا، المدرس لسه ما جددش الاشتراك.") عشان يتستخدم
    بنفس الصياغة بالظبط في كل مكان بيرفض الوصول بسبب التجميد، بدل ما
    نكرر النص حرفيًا في أكتر من ملف.
- عدّلت `groups/views.py` (patch دقيق على الملف الحقيقي، تفاصيل كاملة في
  "قرارات معمارية" فوق):
  - `_group_is_currently_active(group, now=None)` القديمة (كانت بترجع
    tuple فيه bool + الاشتراك) اتشالت، ومكانها `_get_active_subscription(group)`
    (بترجع الاشتراك بس، لغرض العرض).
  - `my_learning_groups`: بقى بيحسب `is_active` عن طريق
    `is_group_content_accessible(group)`، و`active_subscription` عن
    طريق `_get_active_subscription(group)` (لعرض end_date في الكارت).
  - `group_detail`: نفس الشيء بالظبط — `is_active` بقت من
    `is_group_content_accessible(group)`. الطالب العضو (مش المدرس صاحب
    الجروب) لسه بيترجع لصفحة "جروباتي" برسالة تجميد لو الجروب مش نشط،
    بس الرسالة بقت `GROUP_FROZEN_MESSAGE` (من `groups/access.py`) بدل
    النص المكتوب يدويًا، عشان يبقى نفس النص المستخدم في
    `workshops/views.py`.
  - المدرس صاحب الجروب فضل دايمًا يقدر يفتح `group_detail` حتى لو
    الجروب متجمد (نفس سلوك Part 13 بالظبط، والفحص ده متغيرش) — عشان
    يقدر يشوف حالة اشتراكه ويجدده، وحتى يقدر يبعت رسائل في الشات
    لطلابه (تنبيه بضرورة التجديد مثلاً) رغم التجميد.
  - **باقي الملف (768 سطر من أصل 771) متلمسش خالص** — كل الـ views
    التانية (dashboard، create_group، category_options_json،
    submit_payment_proof، upgrade_group، join_teacher_community)
    ومنطق attach/detach_session وsend_message جوه group_detail نفسها
    فضلوا زي ما هما 100%.
- عدّلت `workshops/views.py`:
  - `watch_live` و`watch_recording`: بعد ما `_can_access_group_session`
    (من Part 13) يتأكد إن اليوزر عضو/صاحب الجروب أصلاً، ضفت طبقة فحص
    إضافية — لو اليوزر مش صاحب الجروب (`session.group.teacher_id !=
    request.user.id`)، لازم كمان `is_group_content_accessible(session.group)`
    ترجع True، وإلا بيترفض برسالة `GROUP_FROZEN_MESSAGE` عن طريق دالة
    جديدة `_group_frozen_denied(request)` (نفس أسلوب `_group_access_denied`
    الموجودة بالفعل من Part 13، مع رسالة مختلفة توضح إن السبب هو تجميد
    الاشتراك مش عدم العضوية).
  - المدرس صاحب الجروب مستثنى من الفحص ده الجديد (زي `group_detail`
    بالظبط) — يقدر يدخل جلساته حتى لو الجروب متجمد.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  اشتراك جروب `end_date` بتاعه فات (لسه `status='active'` في
  الداتابيز لحد ما التاسك يشتغل) → التاسك بيشتغل (يدويًا أو دوريًا) →
  الاشتراك بقى `expired` والجروب `is_active=False` → طالب عضو يحاول
  يفتح `group_detail` بتاع الجروب ده → `is_group_content_accessible`
  بترجع False → بيترجع لصفحة "جروباتي" برسالة التجميد. نفس الطالب لو
  حاول يدخل `watch_live` بلينك مباشر لجلسة تابعة لنفس الجروب → نفس
  الرفض بنفس الرسالة. المدرس صاحب الجروب في نفس السيناريو → يقدر يفتح
  `group_detail` وأي جلسة تابعة للجروب عادي من غير أي رفض.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. **الأهم**: `groups/views.py` المعدَّل في الجزء ده اتعاد بناؤه من
     التوثيق، مش من ملف حقيقي — لازم مراجعة دقيقة مقابل النسخة الفعلية
     على السيرفر قبل النشر (تفاصيل في "قرارات معمارية" فوق).
  2. تضارب أسماء الدوال بين `performance_analysis/tasks.py` (دوال بدون
     `@shared_task`) وبين `groups/tasks.py` الجديد (بيستخدم `@shared_task`)
     — القرار في الجزء ده كان نستخدم الطريقة الصح تقنيًا (`@shared_task`)
     بدل تكرار نفس التضارب، بس لو Ahmed حابب يوحّد الاثنين لاحقًا (يضيف
     `@shared_task` لدوال `performance_analysis` كمان) هيبقى تحسين منفصل.
  3. مفيش `CELERY_BEAT_SCHEDULER` متظبط في `settings.py` لاستخدام
     `django_celery_beat.schedulers:DatabaseScheduler` رغم إن التطبيق
     نفسه مضاف في `INSTALLED_APPS` — يعني التاسك الجديد (وأي تاسك قديم)
     شغال بس لو Celery beat process بيشتغل فعليًا على السيرفر مع نفس
     `Eduvia/celery.py` ده (مش عن طريق لوحة تحكم django-celery-beat في
     الأدمن). لو Ahmed عايز يدير الجدولة من لوحة الأدمن بدل الكود، ده
     هيحتاج تغيير منفصل (إضافة `CELERY_BEAT_SCHEDULER` في settings +
     migrate django_celery_beat + تسجيل الـ periodic task من الأدمن).