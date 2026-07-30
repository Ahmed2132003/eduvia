# PROGRESS_PART16.md — نظام جروبات المناهج (Eduvia)
### (ملف بروجرس جديد بيبدأ من Part 16 — الأجزاء 0 إلى 15 موثقة في PROGRESS.md الأصلي)

## الحالة الحالية
آخر جزء منفذ: Part 21 (آخر جزء في الخطة كلها — تنقيح شاشات الأدمن + مراجعة اتساق شاملة نهائية)

## قرارات معمارية اتاخدت (Part 16)

- **طريقة الإرسال**: استخدمت `django.core.mail.send_mail` البسيطة (بنفس
  النمط الموجود فعليًا في `accounts/views.py::register_view` لإرسال كود
  التحقق بالإيميل) بدل نمط `performance_analysis/tasks.py` (اللي بيبني
  `EmailMessage` مع مرفق PDF كامل عن طريق `generate_dashboard_report_pdf`
  و`ReportLab`). السبب: تنبيه انتهاء الاشتراك رسالة نصية بسيطة (تذكير +
  تفاصيل)، مش تقرير مفصّل محتاج مرفق أو موديل تسجيل زي
  `PerformanceReport`. `send_mail` هو أبسط قالب إرسال موجود بالفعل
  وشغال بنفس `EMAIL_BACKEND`/`EMAIL_HOST_USER` المظبوطين في
  `settings.py` من غير أي إعداد إضافي مطلوب.
- **مفيش قالب HTML للإيميل**: الإيميلات بتتبعت كنص عادي (plain text) عن
  طريق `send_mail` مباشرة، مش عن طريق `render_to_string` لقالب HTML زي
  `email_report.html`. القرار ده مقصود — تنبيه نصي بسيط ومباشر أنسب هنا
  من قالب HTML كامل، وده متسق مع `send_mail` المستخدمة في تسجيل الحساب
  في `accounts/views.py`. لو Ahmed عايز شكل HTML منسّق للتنبيهات دي
  لاحقًا، سهل نضيف قالب ونستخدم `EmailMultiAlternatives` بدل `send_mail`.
- **الفلاجات (`reminder_3days_sent` / `reminder_1day_sent`)**: اتضافوا
  على `GroupSubscription` نفسها (مش على موديل منفصل) بـ
  `BooleanField(default=False)`. القرار ده بسيط ومباشر ومتسق مع الطلب
  الأصلي في البرومبت. كل فلاج مستقل تمامًا عن التاني — الفحص بيعتمد بس
  على "الفلاج اتبعت قبل كده ولا لأ" وقت التشغيل، مش على تسجيل تاريخ آخر
  إرسال، عشان يفضل بسيط وواضح ويمنع أي تكرار فعليًا.
- **نافذة "خلال 3 أيام" و"يوم واحد بالظبط"**: بما إن التاسك بيشتغل
  **يوميًا** (مش لحظيًا)، فسّرت "خلال 3 أيام" كـ
  `0 < (end_date - now) <= 3 days`، و"يوم واحد بالظبط" كـ
  `0 < (end_date - now) <= 1 day`. يعني عمليًا: أول ما الاشتراك يدخل في
  نافذة الـ 3 أيام، هياخد التنبيه العادي مرة واحدة بس (الفلاج بيمنع
  التكرار في تشغيلات التاسك التالية لنفس النافذة)، وأول ما يدخل نافذة
  الـ يوم الواحد هياخد التنبيه العاجل مرة واحدة بس، بنفس المنطق. الاتنين
  مستقلين — اشتراك ممكن ياخد الاتنين بالترتيب الطبيعي مع اقتراب
  `end_date`، أو ياخد واحد بس لو التاسك اتشغل لأول مرة والـ `end_date`
  قريب أصلاً من البداية (نادر، بس ممكن يحصل لو الاشتراك اتفعل والتجديد
  قريب جدًا من وقت التفعيل نفسه).
- **مفيش تعديل على `freeze_expired_group_subscriptions` (Part 15)**:
  التاسك الجديد (`send_subscription_expiry_reminders`) منفصل تمامًا،
  وبيفلتر بس على `status='active'`، فمفيش أي تداخل أو تضارب بين
  التاسكين. جدولتهم في `beat_schedule` في وقتين مختلفين (2 صباحًا
  للتجميد، 9 صباحًا للتنبيهات) — تفاصيل السبب في تعليق `celery.py` نفسه.
- **حماية من غياب الإيميل**: لو `teacher.email` فاضي (حالة نظرية، لأن
  التسجيل بيتطلب إيميل أصلاً)، دالة `_send_expiry_reminder_email` بترجع
  `False` وتسجّل تحذير (`logger.warning`) بدل ما ترمي Exception يوقف
  باقي التاسك — يعني لو مدرس واحد معندوش إيميل صالح، باقي المدرسين
  هياخدوا تنبيهاتهم عادي.
- **معالجة الأخطاء لكل اشتراك على حدة**: كل عملية إرسال (لكل اشتراك)
  متلفوفة في `try/except` منفصل جوه اللوب — لو إرسال إيميل واحد فشل (زي
  مشكلة مؤقتة في SMTP)، باقي الاشتراكات في نفس التشغيلة بتكمل عادي
  ومفيش أي اشتراك تاني بيضيع تنبيهه بسبب فشل واحد بس.
- **الفلاجات بتتحدث بس بعد نجاح الإرسال فعليًا**: `subscription.save()`
  بتحصل جوه الـ `try` بعد نداء `_send_expiry_reminder_email` مباشرة —
  يعني لو الإرسال فشل (استثناء)، الفلاج بيفضل `False` والاشتراك هيتحاول
  تاني في تشغيلة التاسك الجاية (اليوم اللي بعده)، بدل ما "يضيع" التنبيه
  نهائيًا بسبب فشل مؤقت.

## قرارات معمارية اتاخدت (Part 17)

- **موديل الحضور**: مفيش أي موديل/حقل جديد اتعمل — `workshops.LiveSession`
  أصلاً فيها حقل `participants` (`ManyToManyField`) جاهز ومستخدم بالفعل
  في `watch_live` (`session.participants.add(request.user)`) من قبل
  الجزء ده. استخدمت نفس الحقل ده كمصدر الحقيقة لـ "هل ده أول حضور
  للطالب في الجلسة دي ولا لأ"، زي ما اتطلب بالظبط في البرومبت ("استخدم
  أي موديل حضور/participants موجود").
- **مكان القيمة الثابتة**: عملت ملف جديد `groups/constants.py` فيه
  `LIVE_SESSION_ATTENDANCE_XP = 20`. اخترت `groups` (مش `workshops` ومش
  `settings.py`) لأن القيمة دي جزء من منطق "مكافآت نظام الجروبات" مش
  منطق `workshops` العام، بنفس روح باقي قرارات المشروع اللي بتفضّل
  إبقاء منطق الجروبات مركزي في تطبيق `groups` قدر الإمكان. الرقم `20`
  نفسه اخترته بنفسي — مفيش تحديد صريح للقيمة في الطلب الأصلي.
- **مين اللي بياخد XP**: بس الطالب، مش المدرس صاحب الجروب. الفحص
  `session.group.teacher_id == user.id` بيستبعد المدرس صراحة — هو صاحب
  الجلسة مش "حاضر" بمعنى الكلمة، وده متسق مع فلسفة كل الفحوصات التانية
  في `workshops/views.py` (Part 13/15) اللي دايمًا بتفرّق بين "صاحب
  الجروب" و"عضو فيه".
- **نطاق التطبيق: لايف سيشن جوه جروب بس**: XP بتتمنح بس للجلسات التابعة
  لجروب (`session.group_id` مش فاضي)، مش لأي جلسة لايف عادية في المنصة.
  ده تفسير حرفي لعبارة الطلب الأصلي "لما يحضر لايف سيشن **جوه جروب**".
  لو Ahmed عايز XP لكل حضور لايف بغض النظر عن الجروب، التعديل بسيط (شيل
  شرط `session.group_id is None: return`).
- **مفيش XP لمشاهدة التسجيل (`watch_recording`)**: المكافأة مقصورة على
  "الحضور" الفعلي وقت اللايف (`watch_live`) بس، زي ما البرومبت نص على
  "يحضر" مش "يشوف تسجيل". `watch_recording` متغيرتش خالص في الجزء ده.
- **منع التكرار**: الفحص (`session.participants.filter(id=user.id).exists()`)
  بيحصل **قبل** `.add()` مباشرة في نفس الـ view، مش عن طريق `created`
  flag من `.add()` نفسها (`ManyToManyField.add()` مبترجعش أي إشارة تقول
  إن ده كان موجود بالفعل ولا لأ، على عكس `get_or_create()` على موديل
  عادي). يعني كل مرة الطالب يفتح `watch_live` لنفس الجلسة، الفحص بيحصل
  من الأول، لكن XP هتتمنح مرة واحدة بس (أول مرة الطالب يبقى مش موجود في
  `participants`).
- **الإرسال synchronous جوه نفس الـ request**: تحديث `profile.xp` بيحصل
  مباشرة جوه `watch_live` (مش عن طريق Celery task منفصل زي Part 15/16)
  — عملية بسيطة (تحديث رقم واحد) مش محتاجة تعقيد async، وده متسق مع
  حجم العملية الفعلي.
- **مفيش أي تعديل على `accounts/models.py`**: `Profile.xp` أصلاً
  `PositiveIntegerField(default=0)` وكافي تمامًا للاستخدام هنا —
  `profile.xp += LIVE_SESSION_ATTENDANCE_XP` ثم `save(update_fields=['xp'])`،
  بنفس نمط التحديثات الجزئية (`update_fields`) المستخدم فعليًا في باقي
  المشروع (زي `groups/tasks.py` من Part 15/16).
- **`Profile.objects.get_or_create(user=user)`**: استخدمتها كطبقة حماية
  إضافية بس (نظريًا الـ `Profile` بيتعمل تلقائيًا عن طريق `post_save`
  signal على `User` في `accounts/models.py`، فمن المفروض يكون موجود
  دايمًا) — لو لأي سبب نادر مكانش موجود، الكود مايفشلش بـ
  `Profile.DoesNotExist`.
- **مفيش فحص لمنع منح XP لو الجروب متجمد**: القرار ده مقصود — لو الطالب
  وصل أصلاً لصفحة `watch_live` (يعني عدّى كل فحوصات `is_group_content_accessible`
  من Part 15 بنجاح)، فده معناه الجروب أصلاً نشط، فمفيش داعي لفحص إضافي
  مكرر هنا. لو الجروب متجمد، الطالب أصلاً هيترفض قبل ما يوصل لسطر منح
  الـ XP خالص.

## قرارات معمارية اتاخدت (Part 18)

- **أنهي موديل هو "المحتوى المسجل جوه الجروب"؟**: اخترت `workshops.LiveRecording`
  (مش `LiveSession` نفسها). السبب: `LiveRecording` هي التسجيل الفعلي
  (`video_file`) اللي أي حد يقدر يشوفه من غير قيود توقيت، على عكس
  `LiveSession` اللي هي الحدث اللايف نفسه (له `start_time`/`end_time`
  وبيتقفل بعد ما يخلص). "معاينة مجانية" منطقيًا لازم تكون محتوى دائم
  متاح للمشاهدة وقت ما الزائر يفتح الصفحة، فالتسجيل هو الاختيار
  المنطقي الوحيد.
- **حقل `is_free_preview`**: اتحط على `LiveRecording` مباشرة
  (`BooleanField(default=False)`)، مش على `LiveSession`. القرار برضه
  متسق مع النقطة اللي فوق — التعليم بـ "معاينة مجانية" منطقه مرتبط
  بالمحتوى المشاهَد (الفيديو) مش بالحدث اللايف نفسه.
- **مين بيعلّم المحتوى كمعاينة مجانية؟**: البرومبت الأصلي مقالش صراحة
  "اعمل view/فورم للمدرس يعلّم بيه"، فاخترت إن التعليم يتم من **لوحة
  الأدمن** (`workshops/admin.py::LiveRecordingAdmin`) بدل ما أعمل شاشة
  جديدة في واجهة المدرس. نفس النمط بالظبط اتبع في Part 9 (قبول/رفض
  الدفع عن طريق admin actions مش view مخصص) — لو فيه شاشة أدمن أصلاً
  المدرس/الأدمن بيستخدمها، مفيش داعي لواجهة موازية لمهمة بسيطة كده.
  ضفت `is_free_preview` في `list_display` **و** `list_editable` (قابل
  للتعديل مباشرة من صفحة القايمة، من غير ما تفتح كل تسجيل لوحده) + حقل
  `list_filter` + action جماعي (`toggle_free_preview`) لتبديل حالة أكتر
  من تسجيل مرة واحدة. لو Ahmed عايز المدرس نفسه (مش بس الأدمن) يقدر
  يعلّم تسجيلاته هو بس من واجهة `groups:group_detail`، ده تحسين منفصل
  سهل (زر toggle بسيط + POST action زي `attach_session`/`detach_session`
  من Part 13).
- **نطاق الصفحة العامة: تسجيلات الجروبات بس**: `free_previews_list`
  بتفلتر على `live_session__group__isnull=False` بالإضافة لـ
  `is_free_preview=True` — يعني تسجيل معلّم كمعاينة مجانية لكن مش تابع
  لأي جروب (`group=None`) **مش هيظهر** في الصفحة. السبب: الهدف
  التسويقي الوحيد المطلوب في البرومبت هو "زرار واضح يودي المستخدم
  لصفحة انضمام المدرس (Part 11)"، وده مسار مبني بالكامل على وجود جروب
  (`join_code`). تسجيل من غير جروب مالوش صفحة انضمام منطقية نودّي
  المستخدم ليها، فاستبعاده أنسب من عرضه بزرار مالوش معنى.
  **ملحوظة مهمة**: عمليًا التسجيلات كلها حاليًا تابعة لجلسات بترتبط
  بجروبات بس عن طريق الربط اليدوي اللي المدرس بيعمله من صفحة الجروب
  (Part 13 — "ضيف جلسة موجودة لهذا الجروب")؛ يعني أي تسجيل لجلسة اتربطت
  بجروب هيبقى مؤهل للمعاينة المجانية أوتوماتيك أول ما الأدمن يعلّمه.
- **الصفحة "عامة" فعليًا من غير أي فحص وصول**: `free_previews_list`
  view **مفيهاش `@login_required`** عمدًا (خلاف كل الـ views التانية في
  `workshops/views.py`) — ده الفرق الجوهري المطلوب في البرومبت
  ("صفحة عامة من غير تسجيل دخول"). الزرار "شاهد المعاينة" بيودّي مباشرة
  لـ `video_file` (رابط خارجي، فتح في تاب جديد) من غير أي فحص
  `_can_access_group_session` أو `is_group_content_accessible` — وده
  المقصود بالظبط: المحتوى ده معلّم عمدًا كـ "مجاني للكل" فمفيش أي داعي
  لتطبيق فحوصات العضوية عليه.
- **زرار "انضم للمدرس" واستخدام `join_code`**: كل عنصر معاينة بيودّي
  لـ `groups:join_teacher_community` بـ `code=item.live_session.group.join_code`
  — بنفس آلية Part 11 بالظبط (join_code بيوصل لكل فئات نفس المدرس، مش
  بس الفئة بتاعة الجروب اللي فيه التسجيل ده). لو الزائر مش مسجّل دخول،
  الرابط هيوصله لصفحة الانضمام اللي أصلاً محمية بـ `student_required`
  (`login_required` + دور)، فهيتحول تلقائيًا لصفحة اللوجين الأول — ده
  سلوك متوقع وصحيح (المسار الطبيعي: شوف المعاينة → اتسجل/اعمل حساب →
  انضم).
- **مفيش أي migration أو تعديل على `groups`**: الجزء ده كله في
  `workshops` (موديل، أدمن، view، url، تمبلت). مفيش أي لمس لأي ملف في
  `groups` — استخدمت بس `join_code` الموجود بالفعل من Part 11 كمرجع.
- **التمبلت**: نسخت نظام "Obsidian Academy" حرفيًا من
  `join_teacher_community.html` (نفس CSS variables، topbar، hero،
  footer، pills) وأضفت مكونات جديدة بأسماء واضحة (`.preview-card`,
  `.preview-badge`, `.preview-btn-watch`, `.preview-btn-join`,
  `.cta-band`) بنفس روح ألوان ومسافات المكونات الموجودة، من غير ما
  أضيف أي ملف CSS خارجي. الصفحة دي أبسط من `join_teacher_community.html`
  في التوبار (مفيش `coins-chip` ولا رابط "Performance" لأن الصفحة ممكن
  تتفتح من زائر مش مسجّل دخول أصلاً).

## سجل الأجزاء

### Part 16 — تنبيهات قبل انتهاء الاشتراك
الحالة: تم
تفاصيل:
- فحصت `performance_analysis/tasks.py` و`performance_analysis/utils.py`
  و`accounts/views.py` قبل أي كود، عشان أتبع نظام إيميل موجود بالفعل
  بدل ما أعمل واحد جديد من الصفر (زي ما اتطلب في البرومبت). القرار
  والسبب موضحين فوق في "قرارات معمارية".
- ضفت حقلين على `GroupSubscription` في `groups/models.py`:
  - `reminder_3days_sent = models.BooleanField(default=False)`
  - `reminder_1day_sent = models.BooleanField(default=False)`
  - مفيش أي تعديل تاني على الموديل أو باقي الملف — كل الموديلات
    التانية (`CurriculumCategory`, `GroupCapacityPlan`, `TeacherGroup`,
    `PaymentProof`, `GroupMembership`, `GroupUpgrade`,
    `GroupChatMessage`) فضلت زي ما هي 100% من غير أي لمس.
- عملت migration جديدة `groups/migrations/0009_groupsubscription_reminder_flags.py`
  — `AddField` بسيط لحقلين، `depends` على `('groups', '0008_groupchatmessage')`
  (آخر migration في التطبيق). مفيش أي `RunPython` مطلوب — القيمة
  الافتراضية `False` مناسبة تمامًا لكل الصفوف الموجودة بالفعل.
- ضفت في `groups/tasks.py` (جنب تاسك `freeze_expired_group_subscriptions`
  الموجود من Part 15، من غير أي تعديل عليه):
  - `_send_expiry_reminder_email(subscription, urgent=False)`: دالة
    داخلية (مش `@shared_task`) بتبني نص الإيميل (عنوان + محتوى مختلفين
    حسب `urgent`) وتبعته بـ `send_mail` لإيميل `subscription.group.teacher`.
    تفاصيل قرار عدم استخدام قالب HTML فوق في "قرارات معمارية".
  - `send_subscription_expiry_reminders()`: الـ `@shared_task` الرئيسية
    للجزء ده. بتعمل استعلامين منفصلين (3 أيام، يوم واحد) بنفس الشروط
    الموضحة فوق في "قرارات معمارية"، وبترجع dict فيه عدد كل نوع تنبيه
    اتبعت (`{'sent_3days': N, 'sent_1day': M}`) لسهولة المراقبة/الديباج.
- عدّلت `Eduvia/celery.py`: ضفت entry جديدة في `app.conf.beat_schedule`
  باسم `'send-subscription-expiry-reminders'`، بتستدعي
  `'groups.tasks.send_subscription_expiry_reminders'` يوميًا الساعة 9
  صباحًا (`crontab(hour=9, minute=0)`) — بعد تاسك التجميد بساعتين، وفي
  وقت مناسب لساعات شغل عادية (مش نص الليل زي تاسك التجميد اللي مفيش
  داعي يكون في وقت مختلف لأنه مش بيبعت حاجة للمستخدم مباشرة). تفاصيل
  السبب الكامل في تعليق الملف نفسه.
- **مفيش أي تعديل على `groups/views.py` أو أي template** — الجزء ده
  كله backend/tasks بس، زي ما اتطلب بالظبط في البرومبت (مفيش أي شاشة
  جديدة للمدرس أو الطالب).
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. مفيش حد أقصى لمحاولات إعادة الإرسال (`retry`) على مستوى Celery
     نفسه لو `send_mail` فشلت بسبب مشكلة SMTP مؤقتة — التاسك حاليًا
     بيسجّل الخطأ في اللوج ويكمل، والاشتراك هيتحاول تاني في تشغيلة
     اليوم الجاي بس (لأن الفلاج فضل `False`). لو عايز retry أسرع (زي
     كل ساعة مثلاً) بدل ما يستنى لليوم اللي بعده، سهل نضيف
     `@shared_task(bind=True, max_retries=3)` مع `self.retry()`.
  2. الإيميل بيتبعت نص عادي (plain text) مش HTML — لو عايز شكل مطابق
     لهوية Eduvia البصرية زي `email_report.html`، محتاج قالب HTML جديد
     + `EmailMultiAlternatives` بدل `send_mail`.
  3. توقيت الساعة 9 صباحًا (Africa/Cairo، حسب `TIME_ZONE` في
     `settings.py`) اخترته بنفسي — مفيش تحديد صريح في الطلب الأصلي، لو
     عايز وقت مختلف سهل نغيّر الـ `crontab` في `celery.py` بسطر واحد.

### Part 17 — مكافآت XP للحضور
الحالة: تم
تفاصيل:
- قريت `accounts/models.py` (`Profile.xp`, `Profile.coins`) و
  `workshops/models.py` (`LiveSession.participants`) و
  `workshops/views.py` كاملة قبل أي كود، عشان أتأكد مفيش نظام XP/coins
  تاني موجود بالفعل في المشروع محتاج أتبعه بدل ما أخترع حاجة جديدة —
  الملفات اللي اتبعتت كانت كافية (مفيش أماكن تانية بتعدّل `profile.xp`
  ظهرت في الملفات المتاحة).
- عملت ملف جديد `groups/constants.py` فيه ثابت واحد:
  `LIVE_SESSION_ATTENDANCE_XP = 20`. تفاصيل قرار المكان والقيمة فوق في
  "قرارات معمارية".
- عدّلت `workshops/views.py`:
  - ضفت imports جديدة: `from accounts.models import Profile` و
    `from groups.constants import LIVE_SESSION_ATTENDANCE_XP`.
  - ضفت دالة جديدة `_grant_group_attendance_xp(user, session)` (helper
    داخلي بس، مش view) بتنفّذ منطق المنح كامل (الفحوصات + التحديث)
    — تفاصيل كل شرط فوق في "قرارات معمارية".
  - عدّلت `watch_live()`: ضفت نداء `_grant_group_attendance_xp(request.user, session)`
    مباشرة قبل السطر الموجود بالفعل `session.participants.add(request.user)`
    (السطر ده نفسه متغيرش). باقي منطق `watch_live` (فحوصات Part 13/15)
    فضل زي ما هو 100% من غير أي لمس.
  - `watch_recording()`، `live_session_list()`، `create_live_session()`،
    `start_live()`، `upload_recording()`، وكل الـ helpers التانية
    (`_can_access_group_session`, `_group_access_denied`,
    `_group_frozen_denied`, `_is_instructor`, `_slugify_title`,
    `_access_denied`) **متلمستش خالص** — نفس الكود بالحرف من Part 15.
- **مفيش أي migration جديدة مطلوبة** — الجزء ده معملش أي تعديل على أي
  موديل (`Profile.xp` كان موجود بالفعل، `LiveSession.participants` كان
  موجود بالفعل).
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  طالب عضو في جروب يفتح `watch_live` لجلسة تابعة للجروب ده لأول مرة →
  `_grant_group_attendance_xp` بتلاقي `already_attended=False` →
  `profile.xp` بتزيد بـ 20 → `session.participants.add()` بتضيفه.
  نفس الطالب يفتح نفس الرابط تاني (يرفريش الصفحة مثلاً) →
  `already_attended=True` → مفيش أي زيادة تانية في XP. المدرس صاحب
  الجروب يفتح نفس الجلسة → الدالة بترجع فورًا من غير أي منح (شرط
  `teacher_id == user.id`). طالب يفتح جلسة لايف عادية (`group=None`) →
  الدالة بترجع فورًا من غير أي منح (شرط `group_id is None`).
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. قيمة الـ XP (`20`) اخترتها بنفسي — مفيش تحديد صريح في الطلب
     الأصلي. لو عايز رقم مختلف، التعديل سطر واحد بس في
     `groups/constants.py`.
  2. مفيش أي مكافأة Coins في الجزء ده (البرومبت الفعلي طلب XP بس رغم
     إن عنوان الـ Part في الخريطة "مكافآت Coins/XP") — لو عايز Coins
     كمان للحضور، سهل نضيف ثابت تاني (`LIVE_SESSION_ATTENDANCE_COINS`)
     ونفس منطق المنح في نفس الدالة.
  3. مفيش أي إشعار/رسالة بصرية للطالب توضح إنه أخد XP (زي toast أو
     badge في `watch_live.html`) — الزيادة بتحصل في الـ backend بس من
     غير أي تغيير على أي template. لو عايز إشعار بصري، محتاج تعديل على
     `workshops/templates/workshops/watch_live.html` (الملف ده مكانش
     متاح في الجزء ده).

### Part 18 — معاينة مجانية تسويقية + ملخص نهائي
الحالة: تم
تفاصيل:
- قريت `workshops/urls.py`، `groups/urls.py`، `workshops/admin.py`،
  وقالبين تمبلت موجودين (`join_teacher_community.html`,
  `live_session_list.html`) قبل أي كود، عشان آخد نظام الـ URLs المتبع
  ونظام التصميم "Obsidian Academy" حرفيًا بدل ما أخترع حاجة جديدة.
- ضفت حقل `is_free_preview = models.BooleanField(default=False)` على
  `workshops.LiveRecording` في `workshops/models.py`. تفاصيل قرار
  اختيار الموديل ده تحديدًا فوق في "قرارات معمارية".
- عملت migration جديدة `workshops/migrations/0005_liverecording_is_free_preview.py`
  — `AddField` بسيط، بتعتمد على `('workshops', '0004_livesession_group')`
  (آخر migration في التطبيق). مفيش أي `RunPython` مطلوب.
- عدّلت `workshops/admin.py`:
  - `LiveRecordingAdmin`: ضفت `is_free_preview` في `list_display` و
    `list_editable` (تعديل مباشر من صفحة القايمة) و`list_filter`.
  - ضفت action جماعي جديد `toggle_free_preview` (بنفس نمط
    `toggle_session_active` الموجود بالفعل على `LiveSessionAdmin`) لتبديل
    حالة `is_free_preview` لأكتر من تسجيل مختار مرة واحدة.
  - `LiveSessionAdmin` **متغيرتش خالص**.
- ضفت view جديد `free_previews_list(request)` في `workshops/views.py`
  — **من غير `@login_required`** (الفرق الجوهري المطلوب). بتفلتر
  `LiveRecording.objects.filter(is_free_preview=True, live_session__group__isnull=False)`
  مع `select_related` مناسب لتقليل عدد الاستعلامات (`live_session`,
  `live_session__group`, `live_session__group__teacher`,
  `live_session__group__category`)، وبترجعهم مرتبين `-uploaded_at`
  (الأحدث الأول). باقي الـ views (`watch_live`, `watch_recording`,
  `live_session_list`, `create_live_session`, `start_live`,
  `upload_recording`) وكل الـ helpers **متلمستش خالص** من Part 17.
- عدّلت `workshops/urls.py`: ضفت
  `path('free-preview/', views.free_previews_list, name='free_previews_list')`
  قبل بقية الـ paths (مفيش أي تعارض فعلي، لأنه string ثابت بالكامل).
- أنشأت `workshops/templates/workshops/free_previews_list.html`:
  - نفس نظام "Obsidian Academy" حرفيًا (نفس CSS variables/topbar/hero/
    footer من `join_teacher_community.html`)، مع مكونات جديدة:
    `.preview-card` (كارت لكل تسجيل معاينة، فيه badge "معاينة مجانية"،
    عنوان الجلسة، اسم المدرس، pills الفئة الدراسية)، وزرارين واضحين:
    `.preview-btn-watch` (رابط خارجي مباشر لـ `video_file`، بيفتح في
    تاب جديد) و`.preview-btn-join` (بيودّي لـ
    `groups:join_teacher_community` بـ `join_code` بتاع الجروب).
  - `.cta-band` جديدة في آخر الصفحة (لو فيه معاينات) بعبارة تسويقية
    بسيطة تحفّز الزائر على الانضمام.
  - `.empty-state` (نفس روح باقي الصفحات) لو مفيش أي معاينة مجانية
    متاحة لسه.
  - التوبار هنا أبسط من `join_teacher_community.html` (مفيش
    `coins-chip` ولا رابط "Performance") لأن الصفحة ممكن تتفتح من زائر
    مش مسجّل دخول أصلاً.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  أدمن يفتح `/admin/workshops/liverecording/` → يعلّم تسجيل تابع لجلسة
  مربوطة بجروب كـ `is_free_preview=True` → زائر (من غير تسجيل دخول)
  يفتح `/workshops/free-preview/` → يشوف كارت التسجيل ده مع اسم المدرس
  والفئة → يضغط "شاهد المعاينة" (يفتح `video_file` مباشرة) → يضغط
  "انضم للمدرس" → لو مش مسجّل دخول بيتحول لصفحة اللوجين أول، وبعدها
  لصفحة `join_teacher_community` بتاعة نفس المدرس.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. مفيش view/فورم في واجهة المدرس نفسها لتعليم تسجيلاته كمعاينة
     مجانية — التعليم دلوقتي من لوحة الأدمن بس (تفاصيل السبب فوق). لو
     عايز المدرس يقدر يعمل ده بنفسه من `groups:group_detail`، ده تحسين
     منفصل بسيط.
  2. مفيش حد أقصى لعدد المعاينات المعروضة في الصفحة (`free_previews_list`
     بترجع كل النتائج من غير `[:N]` أو pagination) — لو عدد التسجيلات
     المعلّمة كبر مع الوقت، ممكن نحتاج pagination بسيطة زي الفكرة
     المستخدمة في `groups/views.py::group_detail` (آخر 100 رسالة شات).

## ملخص وظيفي (Part 0 → Part 18)

الجزء ده تلخيص شامل لكل الأجزاء الوظيفية (functional) اللي اتعملت في
نظام جروبات المناهج، قبل ما ندخل أجزاء تنقيح التصميم (Part 19-21).

### إيه اللي اتعمل (نظرة عامة)

نظام كامل يسمح لمدرس (`role='instructor'`) إنه ينشئ "جروب" لفئة دراسية
معينة (دولة/مرحلة/صف)، يشترك في باقة سعة شهرية (دفع يدوي بإثبات صورة +
مراجعة أدمن)، يستقبل طلاب ينضموا برابط دعوة، يدير حصص لايف وشات جماعي
جوه الجروب ده، والنظام بيدير دورة حياة الاشتراك تلقائيًا (تجميد عند
الانتهاء + تنبيهات قبلها)، مع مكافآت بسيطة للحضور وصفحة تسويقية عامة
لجذب طلاب جدد.

- **Part 0**: إزالة تطبيق الشات بوت المكسور من المشروع بالكامل + تجهيز
  أول نسخة من `PROGRESS.md`.
- **Part 1-6 (الأساسيات/Foundations)**: بناء تطبيق `groups` وكل
  الموديلات الأساسية: `CurriculumCategory` (فئة دراسية)،
  `GroupCapacityPlan` (باقات سعة ثابتة، 6 باقات مزروعة مبدئيًا)،
  `TeacherGroup` (الجروب نفسه، مربوط بمدرس + فئة + باقة حالية)،
  `GroupSubscription` + `PaymentProof` (دورة الاشتراك الشهري وإثبات
  الدفع اليدوي)، `GroupMembership` (عضوية الطالب)، `GroupUpgrade`
  (سجل عمليات ترقية السعة).
- **Part 7-8 (المدرس)**: لوحة تحكم المدرس (عرض جروباته وحالة كل واحد)،
  فورم إنشاء جروب جديد (اختيار فئة بكاسكيدنج + باقة)، وصفحة رفع إثبات
  الدفع.
- **Part 9 (الأدمن)**: مراجعة وقبول/رفض طلبات الدفع من لوحة أدمن Django
  (admin actions مع `select_for_update` لمنع race conditions)، وده اللي
  بيفعّل الاشتراك فعليًا (`status='active'`, `end_date`, تفعيل الجروب).
- **Part 10 (المدرس)**: ترقية سعة الجروب — المدرس يختار باقة أعلى ووضع
  ترقية (`keep_end_date` أو `reset_cycle`)، والفرق بيتحسب ويتحول
  لاشتراك جديد يمر بنفس مسار رفع الإثبات ومراجعة الأدمن.
- **Part 11 (الطالب)**: انضمام الطالب لمجتمع المدرس عن طريق رابط دعوة
  (`join_code` على مستوى الجروب، بيوصل لكل فئات نفس المدرس)، مع حماية
  ضد التسجيل في نفس الفئة مرتين وضد تجاوز السعة القصوى (`select_for_update`).
- **Part 12 (الطالب)**: لوحة "جروباتي" — الطالب يشوف كل الجروبات
  المنضم فيها وحالتها (نشط/متجمد)، ورابط لصفحة محتوى كل جروب
  (`group_detail`) اللي اتوسّعت لاحقًا في Part 13/14.
- **Part 13 (المحتوى)**: ربط `workshops.LiveSession` بالجروب (حقل
  `group`)، إخفاء جلسات الجروبات من القايمة العامة، وحصر الوصول لها على
  عضو/صاحب الجروب. تصحيح ثغرة صلاحيات اكتُشفت (المدرس نفسه ماكانش يقدر
  يفتح صفحة جروبه في Part 12).
- **Part 14 (المحتوى)**: شات جماعي داخل صفحة الجروب (`GroupChatMessage`،
  موديل مستقل عن `mentorship` الموجود بالفعل عمدًا)، متكامل جوه نفس
  `group_detail` view بدل صفحة منفصلة.
- **Part 15 (الأتمتة)**: Celery task يومية (`freeze_expired_group_subscriptions`)
  بتجمّد أي اشتراك خلص، ودالة مركزية `groups.access.is_group_content_accessible`
  بقت هي مصدر الحقيقة الوحيد لـ "هل محتوى الجروب متاح دلوقتي؟" في كل
  أماكن الوصول (بدل الاعتماد على فلاج `is_active` وحده).
- **Part 16 (الأتمتة)**: Celery task تانية يومية بتبعت تنبيهين
  للمدرس بالإيميل قبل انتهاء اشتراكه (3 أيام / يوم واحد)، بفلاجات
  (`reminder_3days_sent`, `reminder_1day_sent`) بتمنع تكرار الإرسال.
- **Part 17 (النمو)**: مكافأة XP ثابتة للطالب أول مرة يحضر جلسة لايف
  تابعة لجروب (باستخدام `LiveSession.participants` الموجود بالفعل كمصدر
  تتبع الحضور، من غير أي موديل جديد).
- **Part 18 (النمو)**: حقل `is_free_preview` على `LiveRecording` +
  صفحة عامة (`/workshops/free-preview/`، من غير تسجيل دخول) تعرض
  التسجيلات المعلّمة كمعاينة مجانية مع زرار مباشر لصفحة انضمام المدرس
  (Part 11).

### أهم القرارات المعمارية المتكررة عبر الأجزاء كلها

- **`accounts.User.role`** هو المرجع الرسمي الوحيد لدور
  student/instructor في كل فحوصات الصلاحيات — اتجنبنا أي مصدر بديل
  (زي `courses_profile.role`) داخل تطبيق `groups` عمدًا.
- **الوصول لمحتوى الجروب** دايمًا بيتفحص Live من قاعدة البيانات (مش من
  فلاج `is_active` المخزّن)، عن طريق `groups.access.is_group_content_accessible`
  بعد Part 15 — عشان يبقى دقيق حتى لو تأخر أي Celery task.
- **مفيش ربط قسري بين تطبيقات مختلفة**: `GroupChatMessage` (Part 14)
  اتعمل مستقل عن `mentorship.GroupChat` الموجود، و`join_code` (Part 11)
  اتحط على `TeacherGroup` مش على `accounts.User` — كلها قرارات بتفضّل
  عدم لمس تطبيقات تانية من غير داعي قوي.
- **Function-based views + render + templates مستقلة (Obsidian Academy)**
  عبر كل الأجزاء، من غير أي class-based views ولا REST API منفصل، ومن
  غير `{% extends "base.html" %}` (كل صفحة standalone بنفس CSS
  variables) — بنفس الأسلوب المستخدم فعليًا في باقي المشروع (`courses`,
  `workshops`) قبل ما تطبيق `groups` يتعمل.
- **الأتمتة (Celery)**: أي منطق "لازم يحصل تلقائيًا بمرور الوقت" (تجميد
  اشتراكات، تنبيهات) اتحط في `groups/tasks.py` كـ `@shared_task` مستقلة
  ومجدولة عن طريق `app.conf.beat_schedule` في `Eduvia/celery.py`، بدل
  ما يتم التحقق منه Lazily في كل request.
- **تحديثات جزئية (`update_fields`)** مستخدمة باستمرار عبر التاسكات
  والـ views لتقليل تأثير التحديثات على الداتابيز، وكل عملية حساسة
  (قبول دفع، انضمام لجروب فيه سعة محدودة) بتستخدم
  `select_for_update()` + `transaction.atomic()` لمنع race conditions.
- **قرارات غير محسومة صراحة في الطلب الأصلي** (زي مدة الاشتراك 30 يوم،
  حد أقصى 100 رسالة شات، قيمة XP=20، إلخ) اتوثقت دايمًا بوضوح في قسم
  "قرارات معمارية" بدل ما تتفرض بصمت — عشان يسهل على Ahmed يراجعها
  ويغيّرها بسطر واحد لو مختلف معاها.

## قرارات معمارية اتاخدت (Part 19)

- **مراجعة الهوية البصرية الفعلية**: فتحت `instructor_dashboard.html`
  و`add_course.html` (اللي بعتهملي Ahmed) قبل أي تعديل، وقارنتهم بالـ
  4 تمبلتس المستهدفة (`dashboard.html`, `create_group.html`,
  `submit_payment_proof.html`, `upgrade_group.html`). التوثيق:
  - **نظام الألوان**: CSS variables تحت `:root` بنفس الأسماء بالظبط في
    كل صفحات المنصة (`--bg-base`, `--bg-panel`, `--bg-card`,
    `--bg-card-2`, `--border`, `--border-glow`, `--violet-400/500/600`,
    `--gold-400`, `--emerald-400`, `--rose-400`, `--sky-400`,
    `--text-h`, `--text-p`, `--text-muted`, `--radius-sm/md/lg/xl`)،
    مع نسخة `[data-theme="light"]` مقابلة لكل متغير. اسم النظام نفسه
    موثّق في تعليق أعلى كل ملف: **"Obsidian Academy"**.
  - **الخطوط**: `Syne` (عناوين/`--font-display`)، `DM Sans` (نص عادي/
    `--font-body`)، `Cairo` (عربي/`--font-arabic`، بيتفعل تلقائيًا لما
    `lang="ar"`).
  - **الكروت**: خلفية `var(--bg-panel)` أو `var(--bg-card)`، حدود
    `1px solid var(--border)`، `border-radius: var(--radius-lg)` أو
    `--radius-xl`، وglow خفيف (`box-shadow: var(--glow)`) على الكروت
    الرئيسية (زي `.form-card` في `add_course.html`، `.course-row` في
    `instructor_dashboard.html`).
  - **الأزرار**: `.action-btn` بمتغيرات لونية (`-curriculum`, `-warning`,
    `-danger`, `-success`, `-info`, `-outline`)، و`.hero-btn`/`.submit-btn`
    بتدرّج بنفسجي (`linear-gradient(135deg, var(--violet-500), var(--violet-600))`).
  - **الأيقونات**: Font Awesome 6 Free (نفس CDN في كل صفحة).
  - **النتيجة**: الأربع تمبلتس المستهدفة كانت بالفعل مبنية بنفس نظام
    "Obsidian Academy" حرفيًا من الأجزاء السابقة (Part 7/8/10) — نفس
    الـ CSS variables، نفس التوبار/الهيرو/الفوتر، نفس `.pill`/
    `.status-badge`/`.action-btn`. يعني الشغل في الجزء ده كان **تنقيح
    وتوحيد دقيق**، مش إعادة بناء من الصفر.
- **إصلاح حقيقي (مش تجميلي بس) في `submit_payment_proof.html`**: كان
  فيه اتساق بصري ناقص — الفورم كان بيعرض `{{ form.receipt_image }}` و
  `{{ form.transaction_reference }}` مباشرة (رندر Django الافتراضي)،
  اللي بيطلع `<input>` عادي من غير أي class، رغم إن الـ CSS class
  `.field-input` كانت معرّفة في الملف نفسه من غير ما تتستخدم فعليًا على
  أي عنصر — يعني كانت هتظهر بستايل المتصفح الافتراضي (أبيض، بلا حواف
  متسقة) وسط صفحة داكنة بالكامل، تكسير واضح للتجربة البصرية. الإصلاح
  (CSS/HTML/template بس، من غير أي لمس لـ `groups/forms.py`):
  - استبدلت الرندر الافتراضي بعناصر `<input>` يدوية بنفس `name`/`id`
    اللي Django متوقعها (`{{ form.field.html_name }}`,
    `{{ form.field.id_for_label }}`) — بنفس الأسلوب المتبع فعليًا في
    `add_course.html` (اللي بيستخدم `<input name="title" value="{{ form.title.value|default:'' }}">`
    بدل `{{ form.title }}`)، فده مش اختراع نمط جديد، ده اتباع نمط
    موجود بالفعل في المشروع.
  - حقل الصورة (`receipt_image`) بقى `.upload-zone` (drag & drop +
    click)، بمعاينة صورة حية (`.img-preview-wrap`) قبل الإرسال — نفس
    مكوّن `add_course.html` بالحرف (نفس أسماء الكلاسات، نفس سلوك
    الـ JS)، عشان رفع "صورة إيصال" بصريًا هو نفس نوع المهمة اللي
    `add_course.html` بيحلها لصورة الكورس.
  - حقل النص (`transaction_reference`) بقى `<input class="field-input">`
    عادي — الكلاس ده كان موجود في الـ CSS بالفعل من غير استخدام،
    فاستخدمته زي ما كان مقصود منه أصلاً.
  - الفحوصات القديمة (`{% if form.field.errors %}`) والـ `id_for_label`
    اتسابوا زي ما هما، فربط `<label for="...">` بالحقل فضل شغال صح،
    وأي أخطاء validation من الـ backend (Part 8) لسه بتتعرض بنفس
    المكان بالظبط.
  - القرار ده اتاخد بعد تأكد إن `PaymentProofForm` (Part 8) نفسها
    (`groups/forms.py`) **متلمستش خالص** — التعديل كله في التمبلت.
- **توحيد التوبار (Glass effect) عبر الأربع صفحات**: كان فيه فرق بسيط
  بين `.topbar` في الأربع تمبلتس المستهدفة (`z-index: 100`,
  `backdrop-filter: blur(14px)`) وبين التوبار الفعلي المستخدم في
  `instructor_dashboard.html`/`add_course.html` (`z-index: 600`,
  `backdrop-filter: blur(20px) saturate(180%)`). وحّدت القيمتين في
  الأربع ملفات لتبقى مطابقة تمامًا للمرجع — `z-index: 600` أهم عمليًا
  (بيمنع أي عنصر تاني في الصفحة يظهر فوق التوبار بالغلط)، و
  `saturate(180%)` بيدي نفس تأثير "الزجاج المصنفر" الغني اللي باقي
  المنصة شكلها بيه.
- **حركة دخول (`cardReveal`) على كروت الفورم**: `create_group.html`،
  `submit_payment_proof.html`، و`upgrade_group.html` كان الـ `.form-card`
  فيها ثابت (من غير أي animation)، بينما `add_course.html` (نفس نوع
  المكوّن بالظبط — كارت فورم مركزي) عنده حركة دخول ناعمة
  (`cardReveal .5s cubic-bezier(.34,1.56,.64,1)`) + `box-shadow: var(--glow)`.
  ضفت نفس الحركة والظل للتلات كروت عشان يبقى إحساس التنقل بين صفحات
  الجروبات وصفحات الكورسات متطابق تمامًا. `dashboard.html` متلمستش في
  النقطة دي لأنها أصلاً عندها حركة `fadeUp` مماثلة على كروت الجروبات.
- **`dashboard.html`، `create_group.html`، `upgrade_group.html`**: بعد
  المراجعة الكاملة (status badges، capacity bar، plan cards، mode
  cards، price preview، empty states، responsive breakpoint 900px)،
  الملفات التلاتة دي كانت متسقة بالفعل مع الهوية البصرية الموثقة فوق —
  التعديل الوحيد فيهم هو توحيد التوبار (وanimation الكارت في الاتنين
  التانيين) الموضح فوق، من غير أي تغيير تاني.
- **الموبايل/Responsive**: راجعت breakpoint الـ `900px` (قايمة
  navigation بتتحول لقايمة منسدلة + hamburger) في الأربع ملفات — نفس
  السلوك بالظبط في كل واحد، ومطابق لسلوك `instructor_dashboard.html`.
  `plans-grid`/`mode-grid` عندهم `auto-fill`/breakpoint خاص بيهم
  (480px للـ mode-grid في `upgrade_group.html`) بيفضل شغال صح على
  الشاشات الصغيرة من غير أي تعديل مطلوب.
- **مفيش أي لمس لمنطق backend**: `groups/views.py`، `groups/forms.py`،
  `groups/models.py`، `groups/urls.py` — ولا سطر واحد اتغيّر في أي
  ملف Python. التعديلات كلها CSS/HTML/JS جوه الأربع تمبلتس بس، زي ما
  اتطلب بالظبط في تعليمات الجزء.

## سجل الأجزاء (تابع)

### Part 19 — تنقيح واجهات المدرس بصريًا
الحالة: تم
تفاصيل:
- راجعت `instructor_dashboard.html` و`add_course.html` (الملفات المرجعية
  اللي بعتهملي Ahmed) ووثّقت نظام "Obsidian Academy" البصري بالكامل —
  تفاصيل كاملة فوق في "قرارات معمارية اتاخدت (Part 19)".
- عدّلت `groups/templates/groups/dashboard.html`:
  - توحيد `.topbar` (`z-index: 100 → 600`,
    `backdrop-filter: blur(14px) → blur(20px) saturate(180%)`) ليطابق
    التوبار الفعلي في `instructor_dashboard.html`.
  - باقي الملف (stats grid، group cards، status badges، capacity bar،
    action buttons، empty state، فوتر، JS الثيم/اللغة) **متلمسش خالص**
    — كان بالفعل متسق مع الهوية البصرية الموثقة.
- عدّلت `groups/templates/groups/create_group.html`:
  - نفس توحيد `.topbar`.
  - ضفت `box-shadow: var(--glow)` وحركة دخول `cardReveal` على
    `.form-card`، بنفس القيم المستخدمة في `add_course.html`.
  - باقي الملف (cascading dropdowns، plan cards، submit button، JS
    الخاص بالـ AJAX) **متلمسش خالص**.
- عدّلت `groups/templates/groups/submit_payment_proof.html`:
  - نفس توحيد `.topbar` ونفس إضافة `cardReveal`/`glow` على `.form-card`.
  - **الإصلاح الأهم**: استبدلت `{{ form.receipt_image }}` و
    `{{ form.transaction_reference }}` (رندر Django الافتراضي، بلا أي
    ستايل) بعناصر HTML يدوية بنفس أسماء/معرّفات الحقول، مطبّق عليها
    `.field-input`/`.upload-zone` — تفاصيل كاملة فوق في "قرارات
    معمارية". ضفت كمان CSS جديد (`.upload-zone`, `.upload-zone-icon`,
    `.upload-zone-text`, `.upload-chosen`, `.img-preview-wrap`) وJS
    جديد (`handleReceiptSelect`, drag & drop على `#upload-zone`) —
    الاتنين منسوخين بنفس المنطق من `add_course.html`.
  - باقي الملف (`.summary-card`, `.status-badge`, `.pending-review-box`,
    الرسائل، رابط الرجوع) **متلمسش خالص**.
- عدّلت `groups/templates/groups/upgrade_group.html`:
  - نفس توحيد `.topbar`.
  - نفس إضافة `cardReveal`/`glow` على `.form-card`.
  - باقي الملف (`.plans-grid`, `.mode-grid`, `.price-preview` وJS
    المعاينة الحية للفرق، `.empty-note`) **متلمسش خالص**.
- **مفيش أي ملف Python اتلمس في الجزء ده** — `groups/views.py`،
  `groups/forms.py`، `groups/models.py`، `groups/urls.py` زي ما هما
  100%، زي ما اتطلب بالظبط ("متلمسش أي منطق backend").
- اختبرت (بصريًا عن طريق مراجعة الكود، مفيش سيرفر فعلي هنا) إن:
  - التوبار في الأربع صفحات بقى بنفس القيم بالظبط زي
    `instructor_dashboard.html` (z-index وglass effect).
  - فورم رفع إثبات الدفع بقى فيه `upload-zone` تفاعلية (drag & drop +
    معاينة صورة) بدل `<input type="file">` عادي أبيض، وحقل رقم
    العملية بقى بنفس ستايل باقي حقول المنصة.
  - أي `name`/`id` لحقول الفورم اتحافظ عليها بالظبط زي ما Django
    محتاجها (`html_name`, `id_for_label`)، فالـ POST هيوصل لـ
    `PaymentProofForm` بدون أي تغيير مطلوب في `groups/forms.py` أو
    `groups/views.py`.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. حقل `transaction_reference` دلوقتي عليه placeholder "(اختياري)" —
     ده افتراض بصري بس مبني على إن الحقل `blank=True` في
     `PaymentProofForm` (Part 8)؛ لو الحقل مطلوب فعليًا، شيل كلمة
     "اختياري" من الـ placeholder في التمبلت (سطر واحد).
  2. المعاينة الحية لصورة الإيصال (`img-preview-wrap`) بتستخدم
     `FileReader` في المتصفح (client-side بالكامل) — نفس تحديد حجم 5
     ميجا المستخدم في `add_course.html` (`file.size > 5 * 1024 * 1024`)
     اتنسخ هنا كـ UX تلميح بس؛ الحد الفعلي (لو موجود) لازم يكون على
     مستوى `PaymentProofForm`/`ImageField` في الـ backend، ومحتاج
     Ahmed يتأكد إن القيمتين متطابقتين لو حابب يضبط حد مختلف.
  3. لسه معملتش أي تعديل على `group_detail.html` (Part 12/13/14) —
     الملف ده بره نطاق Part 19 (اللي بيغطي بس Part 7/8/10 حسب خريطة
     الأجزاء)، وهيتغطى في Part 20 (تنقيح واجهات الطالب) حسب الخطة
     الأصلية.

## قرارات معمارية اتاخدت (Part 20)

- **مصدر الملفات**: اشتغلت مباشرة على النسخ الفعلية اللي بعتهالي Ahmed
  (`join_teacher_community.html`, `my_learning_groups.html`,
  `group_detail.html`) بعد Part 11/12/13/14 — مش نسخة قديمة من ذاكرتي،
  ومفيش أي إعادة بناء من التوثيق (نفس الدرس اللي اتعلمناه من مشكلة
  Part 15).
- **توحيد التوبار (Glass effect)**: نفس النمط اللي اتعمل في Part 19 —
  الثلاث ملفات كانت لسه على القيم القديمة
  (`z-index: 100`, `backdrop-filter: blur(14px)`) لأنها اتعملت في
  Part 11/12/13/14 قبل ما يتحدد المرجع البصري النهائي في Part 19.
  وحّدتهم لـ `z-index: 600` و`backdrop-filter: blur(20px) saturate(180%)`
  زي كل صفحات المنصة الأخرى دلوقتي.
- **توحيد أسماء كلاسات حالة الاشتراك**: لاحظت إن `my_learning_groups.html`
  كانت مستخدمة نمط تسمية مختلف عن `dashboard.html` (اللي اتحدد رسميًا
  في Part 19 كمرجع الحالة): `dashboard.html` بيستخدم
  `class="status-badge status-active"` (CSS selector منفصل `.status-active`)،
  بينما `my_learning_groups.html` كانت مستخدمة
  `class="status-badge active"` (CSS selector مركّب `.status-badge.active`).
  النتيجة البصرية كانت متطابقة أصلاً (نفس الألوان)، لكن التسمية مختلفة
  — وحّدتها لنفس نمط `dashboard.html` بالظبط: `.status-active` /
  `.status-frozen` (الحالة الجديدة "متجمد" مالهاش مقابل في dashboard،
  فاستخدمت لون `status-pending` نفسه — gold — لأن "متجمد" برضه حالة
  "محتاجة انتباه" مش "خطأ نهائي" زي rejected/expired).
- **حركة الدخول (`fadeUp`)**: `dashboard.html` (المرجع من Part 19)
  عنده `@keyframes fadeUp` على `.group-card`. ضفت نفس الحركة بالظبط
  على `.category-card` (join)، `.mygroup-card` (my learning groups)،
  و`.session-row` (group detail) — نفس القيم (`.35s ease both`)، عشان
  إحساس "دخول المحتوى" يبقى متطابق في كل صفحات المنصة.
- **حالة "مفيش أماكن متاحة" في `join_teacher_community.html`**: البرومبت
  طلب صراحة عرض الحالة دي "بلون مختلف واضح". لاحظت إن منطق الـ backend
  الحالي (موثق في Part 11) بيشيل أي جروب `seats_available <= 0` بالكامل
  من القايمة (`rows`) قبل ما توصل للتمبلت خالص — يعني عمليًا الحالة دي
  مش هتظهر أبدًا للطالب في الوضع الحالي (بدل ما تتلوّن بلون مختلف،
  الكارت بيختفي تمامًا). بما إن التعليمات صريحة إني "متلمسش أي منطق
  backend" في الجزء ده، ضفت الحالة البصرية دي في التمبلت كطبقة **دفاعية**
  (`class="seats-text none"` بلون rose + نص "مفيش أماكن متاحة" بدل
  الرقم) تتفعّل لو `seats_available <= 0` وصلت فعلاً للتمبلت — دلوقتي
  مش هتتفعّل عمليًا بسبب الفلترة في الـ view، لكنها هتشتغل صح تلقائيًا
  لو Ahmed غيّر منطق الـ backend لاحقًا (مثلاً لو حب يعرض الجروبات
  الممتلئة بدل ما يخفيها تمامًا، زي واتساب "الجروب مليان"). وثّقت
  التفصيل ده بوضوح هنا عشان محدش يفتكر إن الحالة دي شغالة فعليًا دلوقتي.
- **رسائل Django messages في `group_detail.html`**: لاحظت أثناء المراجعة
  (اللي هي جزء من هدف Part 21 "الاتساق الشامل" بس اكتشفتها هنا) إن
  `group_detail.html` كانت الصفحة الوحيدة من بين كل صفحات `groups`
  اللي بتستخدم نمط تسمية مختلف تمامًا لرسائل النجاح/الخطأ
  (`.alerts-wrap` / `.alert-box.success/.error/.info`، خلفية
  `var(--bg-card)` موحّدة لكل الأنواع وبس لون الحدود بيتغيّر)، بينما
  كل باقي الصفحات (`dashboard`, `create_group`, `submit_payment_proof`,
  `upgrade_group`, `join_teacher_community`, `my_learning_groups`)
  بتستخدم نمط موحّد `<ul class="messages"><li class="success/error/info">`
  بخلفية شفافة ملوّنة حسب النوع (`rgba(52,211,153,.1)` للنجاح، إلخ).
  ده تضارب بصري حقيقي (مش تخيّلي) — نفس نوع الرسالة (نجاح مثلاً) كان
  شكله مختلف في `group_detail.html` عن باقي الصفحات. وحّدت
  `group_detail.html` بالكامل (CSS + الـ HTML markup) لنفس نمط
  `.messages li` المستخدم في كل مكان تاني، من غير أي تغيير في منطق
  `messages` framework نفسه من Django (لسه Django messages framework
  عادي، بس الـ markup اتغيّر بس).
- **الشات الجماعي — استلهام من `accounts/user_chat.html`**: البرومبت
  طلب صراحة "لو فيه ستايل جاهز لشات في المشروع استخدمه، متعملش تصميم
  جديد من الصفر". راجعت `accounts/templates/accounts/user_chat.html`
  (اللي بعتهولي Ahmed) ولقيت إن شات `group_detail.html` (Part 14) كان
  أصلاً بمبني بنفس المفهوم الأساسي (فقاعات يمين/شمال حسب المرسل، وقت
  تحت كل رسالة، اسم المرسل فوق رسائل الطرف التاني، auto-scroll لآخر
  رسالة، Enter للإرسال) — يعني مفيش داعي لإعادة بناء الشات من الصفر،
  بس ضفت تحسين واحد ناقص كان موجود في `user_chat.html` ومش موجود في
  شات الجروب: **أفاتار دائري صغير** (حرف أول من اسم المستخدم) جنب كل
  رسالة من الطرف التاني (`.chat-avatar`)، بنفس مفهوم `.chat-avatar` في
  `user_chat.html` (اللي بيستخدم `{{ other_user.username|slice:":1"|upper }}`)
  لكن بحجم أصغر (28px بدل الحجم الأكبر المستخدم في هيدر الشات المباشر)
  عشان يناسب سياق فقاعة رسالة داخل شات جماعي (أكتر من شخص، مش شخصين
  بس). باقي منطق الشات (بيانات، إرسال، صلاحيات) **متلمسش خالص** — كله
  CSS/HTML بس.
- **Responsive إضافي**: راجعت الثلاث ملفات على شاشات ضيقة جدًا (أصغر من
  breakpoint الـ 900px الموجود للنافيجيشن) ولقيت إن الكروت والفورمات
  نفسها (مش بس النافيجيشن) محتاجة تكسّر بشكل أفضل عند العرض الضيق —
  ضفت breakpoint إضافي عند `560px` في الثلاث ملفات:
  - `join_teacher_community.html`: `.category-card` بيتكسّر عمودي،
    زرار الانضمام/badge المنضم بالفعل بياخدوا العرض الكامل.
  - `my_learning_groups.html`: نفس الفكرة على `.mygroup-card`.
  - `group_detail.html`: `.session-row` بيتكسّر، زرار "انضم دلوقتي"
    بياخد العرض الكامل، `.chat-form` بيتحول لعمودي (التكستاريا فوق
    وزرار الإرسال تحت بالعرض الكامل) بدل ما يتزنقوا جمب بعض، و
    `.chat-bubble` بياخد نسبة أعرض من عرض الشاشة (88% بدل 78%) عشان
    الرسائل تتقرا أوضح على الموبايل.
- **مفيش أي لمس لمنطق backend خالص**: `groups/views.py`،
  `groups/forms.py`، `groups/models.py`، `groups/urls.py` — ولا سطر
  واحد اتغيّر. كل التعديلات في الثلاث ملفات دي CSS/HTML بس (زي ما
  اتطلب بالظبط في تعليمات الجزء)، وأي `name`/`id`/`action` في أي فورم
  (زرار الانضمام، فورم الشات، فورم attach/detach session) اتحافظ عليه
  بالظبط زي ما هو عشان الـ POST يوصل صح للـ views من غير أي تغيير
  مطلوب فيها.

## سجل الأجزاء (تابع)

### Part 20 — تنقيح واجهات الطالب بصريًا
الحالة: تم
تفاصيل:
- راجعت `PROGRESS_PART16.md` (خصوصًا قسم "قرارات معمارية اتاخدت
  (Part 19)") كمرجع مباشر قبل أي تعديل، بدل ما أعيد اكتشاف نظام
  "Obsidian Academy" من الصفر.
- عدّلت `groups/templates/groups/join_teacher_community.html`:
  - توحيد `.topbar` (`z-index: 100 → 600`,
    `backdrop-filter: blur(14px) → blur(20px) saturate(180%)`).
  - ضفت `@keyframes fadeUp` وحركة دخول على `.category-card` (نفس حركة
    `.group-card` في `dashboard.html`).
  - ضفت حالة بصرية جديدة `.seats-text.none` (لون rose) لعرض "مفيش
    أماكن متاحة" بدل الرقم — طبقة دفاعية موضحة تفصيليًا فوق في "قرارات
    معمارية" (مش شغالة فعليًا دلوقتي بسبب فلترة الـ backend الموجودة).
  - ضفت breakpoint إضافي عند `560px` لتكسير `.category-card` عمودي على
    الموبايل.
  - باقي الملف (hero, teacher-card, pills, empty-state, footer, JS
    الثيم/اللغة) **متلمسش خالص**.
- عدّلت `groups/templates/groups/my_learning_groups.html`:
  - نفس توحيد `.topbar`.
  - ضفت `@keyframes fadeUp` وحركة دخول على `.mygroup-card`.
  - وحّدت أسماء كلاسات الحالة من `.status-badge.active`/`.status-badge.frozen`
    (نمط قديم) لـ `.status-active`/`.status-frozen` (نمط `dashboard.html`
    الرسمي من Part 19) — تفاصيل كاملة فوق في "قرارات معمارية". الألوان
    نفسها متغيرتش (emerald للنشط، gold للمتجمد).
  - ضفت breakpoint عند `560px` لتكسير `.mygroup-card` عمودي.
  - باقي الملف **متلمسش خالص**.
- عدّلت `groups/templates/groups/group_detail.html`:
  - نفس توحيد `.topbar`.
  - **وحّدت رسائل Django messages بالكامل** من نمط `.alerts-wrap`/
    `.alert-box` (نمط فريد لهذه الصفحة بس) لنفس نمط `<ul class="messages">
    <li class="success/error/info">` المستخدم في كل صفحات `groups`
    التانية — تفاصيل الاكتشاف والسبب فوق في "قرارات معمارية". ده أهم
    إصلاح اتساق حقيقي في الجزء ده.
  - ضفت `@keyframes fadeUp` وحركة دخول على `.session-row`.
  - **الشات الجماعي**: راجعت `accounts/templates/accounts/user_chat.html`
    (اللي بعته Ahmed) وأكدت إن شات Part 14 أصلاً بنفس المفهوم البصري
    (فقاعات يمين/شمال، وقت، اسم مرسل). ضفت تحسين واحد بس: أفاتار دائري
    صغير (`.chat-avatar`، حرف أول من اسم المستخدم) جنب رسائل الطرف
    التاني، بنفس مفهوم `user_chat.html` — التفاصيل فوق في "قرارات
    معمارية".
  - ضفت breakpoint عند `560px`: `.session-row` بيتكسّر، زرار الانضمام
    للايف بياخد العرض الكامل، `.manage-row` بيلف (`flex-wrap`)،
    `.chat-form` بيتحول لعمودي مع زرار إرسال بالعرض الكامل، و
    `.chat-bubble` بياخد عرض أوسع (88%) على الشاشات الصغيرة.
  - باقي الملف (سيشنز لايف active/upcoming، قسم إدارة الجلسات للمدرس،
    فحوصات `is_owner`/`is_member`، الـ header، الفوتر) **متلمسش خالص**.
- **مفيش أي ملف Python اتلمس في الجزء ده** — نفس التزام Part 19 بالظبط:
  `groups/views.py`، `groups/forms.py`، `groups/models.py`،
  `groups/urls.py` زي ما هما 100%.
- اختبرت (بصريًا عن طريق مراجعة الكود، مفيش سيرفر فعلي هنا، وبفحص
  توازن `{% if/for/block %}` ↔ `{% end... %}` في الثلاث ملفات) إن:
  - التوبار في الثلاث صفحات بقى بنفس القيم بالظبط زي باقي المنصة.
  - كل الفورمات (انضمام، شات، attach/detach session) لسه بتبعت نفس
    الحقول المتوقعة بالظبط للـ views (مفيش أي `name` اتغيّر).
  - كل الـ templates اتفحصت نحويًا (عدد `{% if/for %}` = عدد
    `{% endif/endfor %}`) ومفيش أي اختلال.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. حالة "مفيش أماكن متاحة" في `join_teacher_community.html` مش
     شغالة فعليًا دلوقتي (طبقة دفاعية بس) لأن الـ backend بيشيل
     الجروبات الممتلئة من القايمة تمامًا — لو عايز الطالب يشوف الجروب
     الممتلئ (بلون واضح إنه مليان) بدل ما يختفي خالص، محتاج تعديل بسيط
     في `groups/views.py::join_teacher_community` (شيل الفلترة
     `seats_available <= 0` من الاستعلام، والتمبلت جاهز يعرضها صح من
     غيرأي تعديل تاني).
  2. الشات لسه مش real-time (نفس ملاحظة Part 14 — يحتاج ريفريش يدوي).

## قرارات معمارية اتاخدت (Part 21)

- **شاشة مراجعة طلبات الدفع (Part 9)**: زي ما اتوثق في Part 9 الأصلي،
  المراجعة بتتم من Django admin actions على `PaymentProofAdmin`
  (مفيش view/صفحة مخصصة). التنقيح البصري المطلوب هنا اتقسم لجزئين:
  1. **قايمة الأدمن نفسها** (`/admin/groups/paymentproof/`): ضفت
     helper بسيط `_status_badge(status_value, label)` في `groups/admin.py`
     بيستخدم `django.utils.html.format_html` لعرض حالة الاشتراك كـ
     badge ملوّن (نفس ألوان الـ `status-*` بتاعة التمبلتس بالظبط:
     emerald للـ active، gold للـ pending_payment، rose للـ
     expired/rejected) بدل النص العادي الافتراضي. اتستخدمت في مكانين:
     - `GroupSubscriptionAdmin.status_badge` (بدل عرض `status` الخام).
     - `PaymentProofAdmin.subscription_status` (نفس الدالة، بس عن
       طريق `obj.subscription.status`).
     كل الاتنين عندهم `admin_order_field` عشان الترتيب في القايمة يفضل
     شغال (Django مش بيقدر يرتب على method عادي من غير التلميح ده).
  2. **صفحة تأكيد الرفض** (`reject_confirmation.html`): كانت صفحة
     Django admin عادية جدًا (بلا أي تنسيق تقريبًا، زرار أحمر افتراضي
     `#ba2121`). أعدت تصميمها بالكامل جوه `{% block extrastyle %}`
     (بدون أي اعتماد على CSS variables بتاعة "Obsidian Academy" — دي
     صفحة Django admin بتستخدم `admin/base_site.html`، مش صفحة
     "Obsidian Academy" standalone، فـ CSS variables دي مش متاحة هنا
     أصلاً؛ استخدمت قيم hex مباشرة مطابقة لنفس الألوان زي
     `#fb7185` = `var(--rose-400)`):
     - صندوق تحذير واضح (`.reject-warning-box`) بخلفية rose شفافة
       وحدود rose، بدل الفقرة العادية.
     - قايمة طلبات الدفع المختارة بقت كروت صغيرة (`.reject-queryset-list`)
       بدل `<ul>` عادي.
     - Label "سبب الرفض" بقى واضح إنه إجباري (نجمة حمراء صغيرة).
     - زرار "تأكيد الرفض" بقى بلون rose/danger الحقيقي بتاع المنصة
       (`#e11d48` مع hover أغمق) بدل الأحمر الافتراضي بتاع Django
       (`#ba2121`).
     - ضفت CDN بتاع Font Awesome (نفس النسخة المستخدمة في كل التمبلتس
       التانية، `6.4.2`) في `extrastyle` عشان الأيقونات تشتغل — Django
       admin مبيحملش Font Awesome بشكل افتراضي، فده كان لازم يتضاف
       صراحة عشان الأيقونات في الصندوق الجديد تظهر.
     - **مفيش أي تغيير في منطق الفورم نفسه** — نفس الحقول
       (`review_note`, `action_checkbox_name`, `action`), نفس الـ
       `{% url opts|admin_urlname:'changelist' %}` للإلغاء. التعديل
       كله CSS/markup بصري بس، `groups/admin.py::reject_payment_action`
       (Python) **متلمستش خالص**.
- **مراجعة اتساق شاملة (Part 7 → Part 20)**: راجعت الملفات السبعة كلها
  مع بعض (الأربعة من Part 19 + التلاتة من Part 20) بحثًا عن أي تضارب
  حقيقي في الألوان/الخطوط/المسافات، مش مجرد فحص سطحي:
  - **التوبار**: كل السبع ملفات دلوقتي بنفس القيم بالظبط
    (`z-index: 600`, `backdrop-filter: blur(20px) saturate(180%)`) —
    اتأكد بالـ grep على كل الملفات مع بعض.
  - **حالات الاشتراك/الجروب (`status-*`)**: بعد توحيد
    `my_learning_groups.html` في Part 20، كل الأماكن اللي بتعرض حالة
    (dashboard، my_learning_groups) بتستخدم نفس نمط التسمية
    `.status-badge.status-XXX` بنفس الألوان (emerald/gold/rose).
  - **رسائل Django messages**: بعد توحيد `group_detail.html` في
    Part 20، كل السبع صفحات دلوقتي بتستخدم نفس نمط
    `<ul class="messages"><li class="success/error/info">` بنفس قيم
    الـ `rgba()` بالظبط لكل نوع رسالة. ده كان أهم تضارب حقيقي لقيته في
    المراجعة الشاملة، واتصلح كجزء من Part 20 (موثق هناك بالتفصيل).
  - **الكروت (`.group-card`, `.category-card`, `.mygroup-card`,
    `.form-card`, `.session-row`)**: كلهم دلوقتي بنفس نمط الحركة
    (`fadeUp` أو `cardReveal` حسب نوع الكارت — كروت قايمة بتاخد
    `fadeUp`, كروت فورم مركزية بتاخد `cardReveal` الأكبر حجمًا)، ونفس
    `border-radius`/`border`/hover behavior (`border-color:
    var(--border-glow)` عند الهوفر) في كل مكان.
  - **الـ pills** (`.pill-violet`/`.pill-sky`/`.pill-gold`): نفس القيم
    بالظبط (لون، خلفية، حدود) في `dashboard.html`،
    `join_teacher_community.html`، و`my_learning_groups.html` — مفيش
    أي تضارب اتلاقى هنا من الأساس.
  - **لوحة الأدمن**: بعد إضافة الـ badges الملوّنة (فوق)، حالة
    الاشتراك في `/admin/groups/` بقت بنفس الألوان المستخدمة في
    الواجهة الطلابية/المدرسين (مش بس نص عادي زي الـ Django admin
    الافتراضي) — أقرب ما يكون لاتساق كامل بين لوحة الأدمن والواجهة،
    مع الأخذ في الاعتبار إن لوحة الأدمن نفسها (الهيكل العام، القوايم،
    الفلاتر) بتستخدم تصميم Django admin القياسي عن قصد (مفيش داعي
    نعيد بناء لوحة الأدمن كاملة بنظام "Obsidian Academy" — ده تغيير
    أكبر بكتير من نطاق "تنقيح بصري" ومحتاج قرار منفصل من Ahmed لو
    حابب فيه).
- **رسائل الأدمن (`self.message_user`)**: راجعت `groups/admin.py` —
  كل رسائل النجاح/التحذير في الـ actions (`accept_payment_action`,
  `reject_payment_action`) بتستخدم `messages.SUCCESS`/`messages.WARNING`/
  `messages.ERROR` بشكل صحيح ومتسق بالفعل (نفس نظام ألوان Django admin
  القياسي للرسائل) — مفيش أي تعديل لازم هنا.
- **مفيش أي migration جديدة أو تعديل على أي موديل** في الجزء ده — كله
  CSS/HTML/Python (عرض بس، مفيش تغيير في structure الداتا) في
  `groups/admin.py` و`reject_confirmation.html`.

## سجل الأجزاء (تابع)

### Part 21 — تنقيح شاشات الأدمن + مراجعة اتساق شاملة نهائية
الحالة: تم — **آخر جزء في الخطة كلها (Part 0 → Part 21)**
تفاصيل:
- عدّلت `groups/admin.py`:
  - ضفت `from django.utils.html import format_html`.
  - ضفت helper بسيط `_status_badge(status_value, label)` وdict ألوان
    `_STATUS_BADGE_COLORS` (emerald/gold/rose حسب الحالة) — تفاصيل
    كاملة فوق في "قرارات معمارية".
  - `GroupSubscriptionAdmin`: `list_display` بقى فيه `status_badge`
    (method جديدة) بدل `status` الخام.
  - `PaymentProofAdmin.subscription_status`: بقت بترجع badge ملوّن
    (`_status_badge(...)`) بدل `get_status_display()` نص عادي.
  - **باقي الملف متلمسش خالص** — كل الـ actions
    (`accept_payment_action`, `reject_payment_action`) بمنطقهم الكامل
    (select_for_update، transaction.atomic، منطق Part 10 لحساب
    end_date حسب upgrade_mode) زي ما هما 100%. `TeacherGroupAdmin`،
    `CurriculumCategoryAdmin`، `GroupCapacityPlanAdmin`،
    `GroupMembershipAdmin`، `GroupUpgradeAdmin`، `GroupChatMessageAdmin`
    كلهم زي ما هما بدون أي تعديل.
- أعدت تصميم `groups/templates/admin/groups/paymentproof/reject_confirmation.html`
  بالكامل بصريًا (تفاصيل كاملة فوق في "قرارات معمارية") — صندوق تحذير
  واضح، قايمة طلبات منسّقة، زرار تأكيد بلون rose الحقيقي بتاع المنصة،
  بدون أي تغيير في منطق الفورم أو أسماء الحقول.
- عملت مراجعة اتساق شاملة (pass) على كل السبع تمبلتس اللي اتعدلوا في
  Part 19 وPart 20 مع بعض — لقيت واتأكدت إن كل التضاربات الحقيقية
  (رسائل messages في group_detail.html، تسمية status classes في
  my_learning_groups.html) اتصلحوا بالفعل كجزء من شغل Part 20 (لأنهم
  ملفات طالب/مدرس مباشرة، الأنسب يتصلحوا وقت التعامل مع نفس الملف بدل
  ما يتأجلوا لجولة تانية). باقي الاتساق (توبار، pills، كروت، حركات
  الدخول) كان بالفعل سليم من Part 19.
- **مفيش أي migration جديدة، ومفيش أي تعديل على أي موديل أو view أو
  form في `groups/`** — الجزء ده بالكامل تنقيح بصري + مراجعة (زي ما
  اتطلب بالظبط في تعليمات الجزء).
- اختبرت (بصريًا عن طريق مراجعة الكود + `python -m py_compile` على
  `groups/admin.py` للتأكد من عدم وجود أخطاء syntax، مفيش سيرفر فعلي
  هنا): الملف اتفحص وعدّى من غير أخطاء.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed قبل الإطلاق (تجميع نهائي لكل
  الملاحظات المفتوحة عبر الخطة كلها، للمراجعة السريعة):
  1. **الأهم أمنيًا**: `groups/views.py` اللي اتعدّل في Part 15 اتعمل
     كـ patch على نسخة حقيقية بعتهالي Ahmed، لكن لازم Ahmed يراجعه
     بنفسه مرة أخيرة مقابل النسخة الفعلية على السيرفر قبل النشر (نفس
     الملاحظة الأصلية من Part 15، لسه سارية).
  2. `CELERY_BEAT_SCHEDULER` مش متظبط في `settings.py` لاستخدام
     `django_celery_beat.schedulers:DatabaseScheduler` (Part 15) —
     الجدولة شغالة بس عن طريق `app.conf.beat_schedule` الثابت في
     الكود، مش من لوحة الأدمن.
  3. الإيميلات (Part 16) بتتبعت plain text مش HTML — لو عايز شكل
     مطابق لهوية Eduvia البصرية، محتاج قالب HTML جديد.
  4. قيمة XP (Part 17 = 20) وحد رسائل الشات المعروضة (Part 14 = 100)
     اخترتهم بنفسي بدون تحديد صريح في الطلب الأصلي — سهل التعديل لو
     مختلف معاهم.
  5. حالة "مفيش أماكن متاحة" في `join_teacher_community.html` (Part 20)
     مش شغالة فعليًا دلوقتي لأن الـ backend (Part 11) بيشيل الجروبات
     الممتلئة من القايمة تمامًا بدل ما يعرضها بلون مختلف — التمبلت
     جاهز لو Ahmed حب يغيّر منطق الفلترة في `groups/views.py`.
  6. لوحة الأدمن (Part 9/21) اتحسّنت بصريًا (badges ملوّنة + صفحة رفض
     منسّقة) لكن لسه بتستخدم هيكل Django admin القياسي عمومًا (مش نظام
     "Obsidian Academy" الكامل) — قرار مقصود (تفاصيل السبب فوق)، لكن
     لو Ahmed حابب لوحة أدمن مخصصة بالكامل بنفس هوية المنصة، ده مشروع
     منفصل أكبر بكتير من نطاق "تنقيح بصري".
  7. الشات الجماعي (Part 14/20) لسه مش real-time — يحتاج Django
     Channels لو الأولوية تتغير مستقبلاً.
  8. **ده آخر جزء في الخطة الكاملة (Part 0 → Part 21)** — النظام دلوقتي
     وظيفيًا كامل (كل الأجزاء 0-18) وبصريًا منقّح بالكامل (19-21). أي
     تطوير إضافي من هنا يعتبر خارج نطاق الخطة الأصلية ويحتاج تخطيط جديد.