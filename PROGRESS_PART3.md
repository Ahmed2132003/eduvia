# PROGRESS_PART22.md — المرحلة الثانية (Eduvia)
### (ملف بروجرس جديد بيبدأ من Part 22 — المرحلة الأولى كاملة (Part 0 → Part 21)
### موثقة في PROGRESS.md و PROGRESS_PART16.md الأصليين. الملف ده بيكمل الترقيم
### من غير ما يعيد كتابة تاريخ المرحلة الأولى، عشان الحجم يفضل قابل للإرسال)

## الحالة الحالية
آخر جزء منفذ: Part 24 (واجهة المدرس: بدء/جدولة لايف من صفحة الجروب) —
✅ **اتأكد فعليًا بالكامل**: Ahmed جرّب السيناريو الحقيقي على متصفح حقيقي
(كاميرا + مايكروفون + مشاركة شاشة اشتغلوا، وزرار "إنهاء البث" رجّعه
لصفحة الجروب بنجاح من غير أي مشكلة). تكامل LiveKit (Server SDK من
Part 23 + Client SDK من Part 24) شغال فعليًا 100% على الاتجاهين. تفاصيل
كاملة في آخر قسم "Part 24" تحت.

✅ **تحديث مهم على Part 23**: Ahmed أكد إن `python manage.py
test_live_provider` اتشغّل فعليًا على سيرفر فيه LiveKit حقيقي شغال،
والتسلسل الكامل (`create_room` → `generate_access_token` host →
`generate_access_token` viewer → `end_room`) نجح فعليًا — يعني تكامل
LiveKit (`groups/live_provider.py`) شغال ومتأكد منه دلوقتي، مش مجرد
syntax check زي ما كان موثق قبل كده. **ملحوظة**: التفاصيل الدقيقة
لنتيجة الاختبار (نص المخرجات، قيمة `LIVEKIT_URL` المستخدمة، إلخ) اتأكدت
شفهيًا في المحادثة مع Ahmed مش عن طريق ملف نتائج مرفق، فمفيش تفاصيل
إضافية موثقة هنا غير إن الاختبار "عدّى بنجاح". تفاصيل الجزء الأصلي فضلت
زي ما هي تحت في قسم "قرارات معمارية اتاخدت (Part 23)" (مع تحديث حالة
السطر المعلّق في سجل الأجزاء تحت).

قرار الاستضافة (self-hosted Docker مقابل LiveKit Cloud) وقيمة
`LIVEKIT_URL` الفعلية بقوا محسومين عمليًا (بما إن فيه سيرفر شغال
واتاختبر بنجاح)، لكن مفيش تفاصيل إضافية عن القرار ده موثقة صراحة في
المحادثة، فسايبها هنا كملحوظة مفتوحة لو Ahmed حابب يوثقها بالتفصيل لاحقًا.

## ملخص المرحلة الأولى (مرجع سريع بس — التفاصيل الكاملة في PROGRESS.md / PROGRESS_PART16.md)
- Part 0-6: تطبيق `groups` + الموديلات الأساسية (CurriculumCategory،
  GroupCapacityPlan، TeacherGroup، GroupSubscription، PaymentProof،
  GroupMembership، GroupUpgrade).
- Part 7-11: لوحات المدرس/الطالب، رفع إثبات الدفع، مراجعة الأدمن، الترقية،
  الانضمام بـ join_code.
- Part 12-14: لوحة "جروباتي"، ربط `workshops.LiveSession` بالجروب، شات
  جماعي (`GroupChatMessage`).
- Part 15-16: أتمتة Celery (تجميد الاشتراكات المنتهية + تنبيهات قبل
  الانتهاء)، ودالة `groups.access.is_group_content_accessible` كمصدر
  الحقيقة الوحيد لفحص "هل محتوى الجروب متاح دلوقتي؟".
- Part 17-18: مكافآت XP للحضور، معاينة مجانية تسويقية.
- Part 19-21: تنقيح بصري كامل بنظام "Obsidian Academy" (نفس CSS
  variables/topbar/كروت في كل صفحات `groups`)، وتنقيح شاشات الأدمن.

هذا الملف (PROGRESS_PART22.md) هو امتداد مباشر — أي جلسة جديدة في المرحلة
الثانية الزم تتبعت ومعاها الملف ده (مش الملفين القدام، إلا لو محتاج تفصيلة
معمارية قديمة معينة).

## قرارات معمارية اتاخدت (Part 22)

### 1) البحث في المشروع — هل فيه بنية بث مباشر حقيقية موجودة بالفعل؟

راجعت الملفات دي قبل أي قرار: `Eduvia/settings.py`، `Eduvia/asgi.py`،
`workshops/models.py`، `workshops/consumers.py`، `workshops/routing.py`،
`projects/consumers.py`، `projects/routing.py`، و`requirements.txt`.
النتيجة:

- **`channels` و`channels_redis` متثبتين فعلاً** (`channels==4.2.2`,
  `channels_redis==4.2.1` في `requirements.txt`)، و`'channels'` مضاف في
  `INSTALLED_APPS`، و`ASGI_APPLICATION = 'Eduvia.asgi.application'` مظبوط.
- **`workshops/consumers.py::LiveStreamConsumer`**: consumer بسيط جدًا —
  بيعمل `channel_layer.group_add` على `live_{session_id}`، وبيستقبل أي
  JSON من عميل ويعمل broadcast له لكل الأعضاء في نفس الجروب
  (`group_send` → `stream_message` → `send`). **ده relay نصي عام بس، مش
  بث ميديا حقيقي** — مفيش أي معالجة SDP/ICE candidates، مفيش أي مسار
  فعلي للفيديو/الصوت، ومفيش أي واجهة فعلية (JS) بتستخدمه لحد دلوقتي (لم
  ألاقي أي template بيعمل `new WebSocket('ws/live/...')` في الملفات
  المتاحة). عمليًا الـ consumer ده أقرب لـ "شات لايف نصي" جاهز البنية،
  مش نواة WebRTC.
- **`workshops/routing.py`**: `ws/live/<session_id>/` → `LiveStreamConsumer`.
  فقط.
- **`projects/consumers.py::RoomConsumer`** و**`projects/routing.py`**:
  نفس الفكرة بالظبط لكن لشات نصوص عادي (`RoomMessage`/`CollaborationRoom`)
  — مالوش أي علاقة بالفيديو خالص، مجرد شات نصي جماعي تاني في تطبيق تاني.
  **ملحوظة جانبية مهمة (خارج نطاق الجزء ده لكن تستحق التسجيل)**:
  `Eduvia/asgi.py` **بيسجل `workshops.routing` بس** —
  `projects.routing.websocket_urlpatterns` **مش مضاف في
  `ProtocolTypeRouter`** خالص، يعني أي WebSocket بيحاول يوصل لـ
  `ws/room/<room_id>/` (بتاع `projects`) هيفشل فعليًا في الإنتاج
  دلوقتي (404 على مستوى الـ ASGI routing) حتى لو الـ consumer والـ
  routing موجودين كملفات. مش هلمس ده في الجزء الحالي (مش من مهام Part
  22)، بس علّمت عليه هنا عشان Ahmed يعرف إنها مشكلة موجودة بالفعل، مش
  حاجة هستحدثها.
- **مفيش أي `CHANNEL_LAYERS` معرّف في `settings.py` خالص** — رغم إن
  `channels_redis` متثبتة ومتاحة، مفيش إعداد صريح بيربطها. لما
  `CHANNEL_LAYERS` مش متعرّف، Django Channels بيستخدم
  `InMemoryChannelLayer` الافتراضي ضمنيًا فقط لو حددته، لكن **من غير
  أي `CHANNEL_LAYERS` أصلاً في settings.py، أي استخدام لـ
  `channel_layer.group_send`/`group_add` (زي في الـ consumers الحاليين)
  هيفشل عمليًا** لإن مفيش channel layer معرّف يتقدر يتنادى. ده تفصيل
  تقني موجود في الكود الحالي مش من مسؤولية الجزء ده يتصلح، لكن يوضح
  إضافي إن البنية التحتية الحالية للـ real-time (حتى النصي) مش مكتملة
  الإعداد أصلاً.
- **مفيش أي إشارة لـ LiveKit/Agora/Jitsi/Zoom/Twilio Video** في أي مكان
  (`requirements.txt`، `settings.py`، أو أي ملف تاني اتفحص) — لا مكتبة
  Python متثبتة (`livekit-server-sdk`، `agora-token-builder`، `aiortc`،
  إلخ)، ولا API keys، ولا أي إعداد `TURN`/`STUN` servers.
- **`workshops.LiveSession` (الموديل الحالي)**: `meet_link =
  URLField(...)` — يعني آلية اللايف الحالية بالكامل في المشروع هي رابط
  **Google Meet خارجي** بيتحط يدويًا، مش بث مدمج في المنصة. مفيش أي
  video/audio track فعلي بيتبعت من خلال سيرفرات المشروع خالص.

**الخلاصة**: مفيش أي بنية تحتية لبث مباشر حقيقي (كاميرا فعلية + مشاركة
شاشة + تسجيل تلقائي) في المشروع دلوقتي. البنية الوحيدة الموجودة هي
consumers نصيين لشات/relay بسيط، وحتى دول ناقص إعداد `CHANNEL_LAYERS`.
أي بث فيديو حالي (`workshops.LiveSession.meet_link`) هو رابط Google Meet
خارجي بالكامل، برة تحكم المنصة.

### 2) القرار المعماري: LiveKit (self-hosted عن طريق Docker، أو LiveKit Cloud)

**القرار**: استخدام **LiveKit** كمزود WebRTC جاهز (SFU حقيقي)، بدل بناء
سيرفر ميديا من الصفر بـ Django Channels.

**السبب الأساسي**: بث كاميرا حي لعدد طلاب مش محدود (one-to-many) +
مشاركة شاشة + تسجيل تلقائي، محتاج **Selective Forwarding Unit (SFU)**
حقيقي — سيرفر ميديا بيستقبل الـ tracks من المدرس (host) ويوزّعها بكفاءة
على كل الطلاب المتصلين من غير ما يحمّل جهاز المدرس نفسه (على عكس
اتصال WebRTC مباشر peer-to-peer اللي بيتحمّل فيه جهاز المدرس upload
منفصل لكل طالب — ده غير عملي أصلاً لأكتر من 2-3 مشاهدين). بناء SFU من
الصفر (معالجة RTP/RTCP، تفاوض ICE/DTLS-SRTP، إدارة bandwidth، إلخ) هو
مشروع بنية تحتية ضخم بمفرده، ومش هدف معقول لتطبيق Django عادي زي
Eduvia.

**ليه LiveKit تحديدًا (مش Django Channels وحدها، ومش بديل تاني)**:
- **`workshops/consumers.py` الحالي بيقدر يستخدم كطبقة "إشارة"
  (signaling) بسيطة في نظرية الأمور (تبادل SDP/ICE)، لكن ده برضه مش
  كافي وحده** — الـ signaling channel بس بيوصل طرفين على بعض عشان
  يبدأوا اتصال WebRTC، لكن الاتصال الفعلي (نقل الفيديو/الصوت) لازم
  يمر على سيرفر ميديا (SFU) عشان يشتغل مع أكتر من مشاهد. يعني حتى لو
  استخدمنا الـ consumer الموجود، هنحتاج SFU تاني وراه على أي حال.
- **LiveKit مفتوح المصدر (Apache 2.0)** وبيوفر بالظبط المطلوب من غير
  ما نبنيه:
  1. نشر كاميرا (publish) لعدد مشاهدين كبير (subscribe) من غير ما نبني
     منطق توزيع بأنفسنا.
  2. مشاركة شاشة (screen share) كـ track تاني بنفس آلية الكاميرا —
     مدعومة built-in في الـ client SDK بتاعته.
  3. **Egress API جاهزة للتسجيل التلقائي** (room composite recording)
     — بترفع الفيديو المسجل لتخزين خارجي (S3-compatible، ومشروع
     Eduvia أصلاً بيستخدم `boto3`/`django-storages` في
     `requirements.txt`، فده متسق مع البنية الموجودة) — وده اللي هيبني
     عليه Part 26 (تسجيل اللايف تلقائيًا) مباشرة من غير حل تاني منفصل.
  4. **Server SDK بيولّد access tokens (JWT) بسيطة** — الـ Django
     backend مش محتاج يبقى جزء من مسار الميديا خالص، دوره بس إنه يتحقق
     من الصلاحيات (نفس `is_group_content_accessible` من Part 15) ويولّد
     توكن للعميل (JS SDK) يتصل بيه مباشرة بالـ LiveKit server — نفس
     فلسفة الـ views البسيطة (function-based) المتبعة في كل المشروع،
     من غير ما نحتاج نعقّد الـ backend بمنطق ميديا.
  5. **خيار الاستضافة مرن**: ممكن يتشغّل self-hosted عن طريق Docker
     (تحكم كامل، تكلفة تشغيل ثابتة) أو LiveKit Cloud (managed، صفر
     صيانة سيرفرات) — القرار ده (self-hosted مقابل Cloud) قرار تشغيلي
     (infrastructure) مش معماري، وهسيبه مفتوح لـ Ahmed يقرره حسب
     الميزانية والبنية التحتية المتاحة عنده وقت التنفيذ الفعلي (Part 23)؛
     الكود (Server SDK + Client SDK) هيشتغل بنفس الطريقة في الحالتين،
     الفرق بس في الـ `LIVEKIT_HOST` (URL) المستخدم.
  - ⚠️ **[تحديث Part 23]**: القرار ده لسه مفتوح فعليًا — Ahmed لسه
    مقالش صراحة self-hosted ولا Cloud وقت تنفيذ Part 23. الكود
    (`groups/live_provider.py`) اتكتب بحيث الفرق كله في قيمة
    `LIVEKIT_URL` (متغير بيئة)، فمفيش أي قرار برمجي معلّق على الاختيار
    ده — بس القيمة الفعلية لازم تتحط قبل أول اختبار حقيقي (تفاصيل تحت
    في Part 23).

**البدائل اللي اتفكر فيها ورفضتها**:
- **بناء WebRTC من الصفر بـ Django Channels فقط (Mesh/P2P)**: مرفوض —
  مش قابل للتوسع لأكتر من 2-3 مشاهدين (كل مشاهد جديد بيحمّل رفع إضافي
  على جهاز المدرس)، ومفيش تسجيل تلقائي جاهز، ومحتاج منطق SDP/ICE/TURN
  معقد من الصفر برضه من غير أي فايدة عن استخدام مزود جاهز.
- **Jitsi (self-hosted)**: بديل معقول وكان مطروح في تعليمات الجزء نفسه
  كخيار بديل. رُفض **لصالح LiveKit** للأسباب دي تحديدًا:
  - Jitsi Meet (الواجهة الجاهزة) مبني على افتراض "غرفة اجتماع" كاملة
    (UI جاهزة بتاعته)، بينما احتياج Eduvia هنا هو **تضمين مخصص** جوه
    صفحة الجروب نفسها بنفس هوية "Obsidian Academy" — ده ممكن مع
    Jitsi عن طريق `lib-jitsi-meet` (الطبقة الأدنى)، لكن التوثيق
    والدعم لبناء واجهة مخصصة بالكامل من الصفر عليها أقل نضجًا من
    LiveKit's client SDKs (اللي مبنية أصلاً كـ "بلوكات" مصممة للتضمين
    المخصص، مش كواجهة جاهزة).
  - Egress/التسجيل في Jitsi (Jibri) محتاج سيرفر Selenium+Chrome منفصل
    بيسجل الشاشة فعليًا (headless browser recording) — أثقل تشغيليًا
    ومعقد في الصيانة مقارنة بـ LiveKit Egress (API مباشرة بدون سيرفر
    تسجيل منفصل بمتصفح وهمي).
  - القرار مش نهائي بشكل متعصب — لو Ahmed عنده خبرة تشغيلية سابقة مع
    Jitsi أو تفضيل واضح ليه، التبديل ممكن في Part 23 قبل ما نكتب أي
    كود تكامل فعلي (الموديل الحالي في الجزء ده، `GroupLiveSession`،
    محايد تمامًا تجاه المزود — `room_identifier` نص عادي يشتغل مع أي
    مزود).
- **Agora / Twilio Video / Zoom SDK (مزودين تجاريين مغلقين)**: مرفوضين
  كخيار أول — تسعير على أساس دقائق/مستخدمين بيصعب توقعه مبكرًا لمشروع
  ناشئ، ومفيش أي إشارة في المشروع لاستخدام سابق لأي منهم. LiveKit
  بيوفر بديل مفتوح المصدر بنفس القدرات الأساسية المطلوبة (كاميرا +
  شاشة + تسجيل) من غير قفل على مزود تجاري واحد من البداية.

**تنفيذ التكامل الفعلي (API keys، Server SDK، توليد التوكنات، endpoint
الـ webhook للتسجيل) هيتم في Part 23** — الجزء الحالي (22) بيقتصر على
القرار + الموديل زي ما اتطلب بالظبط.

### 3) موديل `GroupLiveSession`

اتحط في `groups/models.py` (نفس تطبيق `groups`، بنفس فلسفة Part 14 —
عدم ربط تطبيقات مختلفة ببعض من غير داعي قوي؛ الموديل ده **مش** مرتبط
بـ `workshops.LiveSession` القديمة خالص، دي مسارين منفصلين تمامًا: لايف
الجروبات الجديد [Part 22+] هيستخدم WebRTC حقيقي جوه المنصة، بينما
`workshops.LiveSession` القديمة هتفضل شغالة بنظام Google Meet الخارجي
لأي استخدام تاني برة الجروبات).

- كل الحقول اتضافت بالظبط زي المواصفة المطلوبة في البرومبت (`group`،
  `host`، `title`، `description`، `mode`، `status`، `scheduled_at`،
  `started_at`، `ended_at`، `room_identifier`، `recording_url`،
  `created_at`) — مفيش أي حقل إضافي أو محذوف.
- `related_name='+'` على `host` (بنفس قرار `PaymentProof.reviewed_by`
  من Part 4 — مفيش حاجة محتاجة reverse query "كل الاليفات اللي فلان
  استضافها" دلوقتي).
- `on_delete=models.CASCADE` على الاتنين (`group` و`host`) بالظبط زي
  المطلوب في المواصفة.
- `room_identifier` و`recording_url` اتسابوا فاضيين قابلين للـ blank
  (زي ما هو مطلوب) — هيتملوا فعليًا في Part 23 (إنشاء الروم عند
  LiveKit) وPart 26 (بعد التسجيل).
- ضفت `Meta.ordering = ['-scheduled_at', '-created_at']` (تفصيل مش
  محدد صراحة في المواصفة، اخترته بنفسي) عشان أي queryset عادي على
  الموديل (زي في لوحة الأدمن) يطلع بالأحدث/الأقرب معادًا الأول تلقائيًا
  من غير ما ننسى نحدد `order_by()` في كل مكان — بنفس روح
  `GroupChatMessage.Meta.ordering` من Part 14 (لكن هناك بترتيب تصاعدي
  لأن الشات محتاج أقدم-لأحدث، وهنا تنازلي لأن القوايم الإدارية/لوحات
  التحكم بتحتاج الأحدث الأول).
- `__str__` بيرجع `"{title} - {group} ({status})"` بنفس نمط باقي
  الموديلات (`GroupSubscription.__str__` مثلاً).

### 3.1) تصحيح لاحق — تعارض related_name (اتلاقى عن طريق `makemigrations --check` الفعلي على السيرفر)

أول مسودة للموديل استخدمت `related_name='live_sessions'` على حقل
`group` (نسخًا حرفيًا من نفس اسم الـ related_name المستخدم في
`workshops.LiveSession.group` من Part 13، ظنًا مني إنه هيبقى آمن بنفس
منطق `instructor`/`group` جوه `workshops.LiveSession` نفسها). لما Ahmed
شغّل `makemigrations --check --dry-run` فعليًا، ظهر خطأ حقيقي
(`fields.E304`/`fields.E305`): **تعارض فعلي**، لأن الاتنين
(`workshops.LiveSession.group` و`groups.GroupLiveSession.group`)
بيرجعوا على **نفس الموديل الهدف بالظبط** (`groups.TeacherGroup`) —
على عكس حالة `instructor` جوه `workshops.LiveSession` نفسها اللي كانت
آمنة لأنها بترجع على `User` مش `TeacherGroup`. الدرس هنا: تطابق اسم
الـ related_name آمن بس لو الموديلات الهدف مختلفة، مش لو نفس الموديل.

**التصحيح**: غيّرت `related_name` على `GroupLiveSession.group` من
`'live_sessions'` لـ **`'group_live_sessions'`** — في `groups/models.py`
وفي `groups/migrations/0010_grouplivesession.py` (الاتنين اتحدثوا
بنفس القيمة الجديدة قبل ما ترجع تشغل `makemigrations` تاني). يعني
دلوقتي:
- `TeacherGroup.group_live_sessions` → كل جلسات اللايف الجديدة
  (`GroupLiveSession`، نظام Part 22+ الجديد بـ LiveKit).
- `TeacherGroup.live_sessions` → فضلت زي ما هي، بترجع لـ
  `workshops.LiveSession` (النظام القديم بـ Google Meet، من Part 13).
  **متلمستش خالص** — الاسم القديم فضل زي ما هو تمامًا، التعديل كله في
  الموديل الجديد بس.

### 4) لوحة الأدمن

سجّلت `GroupLiveSession` في `groups/admin.py` بنفس نمط باقي الموديلات:
`list_display` (title, group, host, mode, status badge, التواريخ
الثلاثة، created_at)، `list_filter` (status, mode, group__category)،
`search_fields` (title, اسم الجروب, اسم المدرس, اسم المضيف,
room_identifier). استخدمت نفس helper `_status_badge` الموجود بالفعل من
Part 21 (لتلوين حالة الاشتراك) وضفتله ألوان جديدة لحالات
`GroupLiveSession` (`live`=أخضر، `scheduled`=ذهبي، `ended`=رمادي،
`canceled`=وردي) — نفس الدالة، من غير أي تكرار كود. `room_identifier`،
`recording_url`، `started_at`، `ended_at` اتحطوا `readonly_fields` في
الأدمن لأنهم هيتحددوا فعليًا من منطق الـ views/الـ webhook في الأجزاء
الجاية (23/24/26)، مش من تعديل يدوي في لوحة الأدمن.

### 5) Migration

`groups/migrations/0010_grouplivesession.py` — `CreateModel` بسيط،
بتعتمد على `('groups', '0009_groupsubscription_reminder_flags')` (آخر
migration معروفة في تطبيق groups من توثيق المرحلة الأولى) و
`migrations.swappable_dependency(settings.AUTH_USER_MODEL)`. **⚠️ لو
فيه migration أحدث اتعملت على السيرفر الحقيقي بعد Part 16/21 مش موثقة
في الملفات اللي اتبعتلي في الجلسة دي، لازم تراجع رقم الـ dependency ده
يدويًا قبل ما تشغل `makemigrations`/`migrate` — الملف مكتوب يدويًا
(مش عن طريق تشغيل فعلي لـ `makemigrations`) لإني مش شغال على السيرفر
الحقيقي.**

## قرارات معمارية اتاخدت (Part 23)

### 1) التحقق الفعلي من `livekit-api` SDK قبل الكتابة (مش افتراض من الذاكرة)

قبل ما أكتب أي سطر كود، ثبّتت مكتبة `livekit-api` فعليًا (`pip install
livekit-api`) وراجعت توقيعات الدوال والكلاسات اللي هستخدمها بـ
`inspect.signature` مباشرة، بدل ما أفترض شكل الـ API من الذاكرة (النسخة
اللي اتثبتت: `livekit-api==1.2.0`). النتائج المهمة اللي بنيت عليها
الكود:
- **المكتبة كلها async** (مبنية على `aiohttp`) — `LiveKitAPI.room.create_room`
  و`.delete_room` كلاهما `async def`. مفيش نسخة sync جاهزة في المكتبة
  نفسها.
- `AccessToken(api_key, api_secret)` مع methods قابلة للتسلسل
  (`with_identity`, `with_name`, `with_grants`, `with_ttl`) وأخيرًا
  `.to_jwt()` بترجع الـ JWT النهائي كنص.
- `VideoGrants(room_join=True, room=<اسم الروم>, can_publish=<bool>,
  can_subscribe=True, can_publish_data=True)` هو الكلاس المسؤول عن
  صلاحيات التوكن (نشر/مشاهدة).
- `CreateRoomRequest(name=..., empty_timeout=..., max_participants=...)`
  و`DeleteRoomRequest(room=...)` هما الـ request objects لإنشاء/حذف
  الروم عن طريق `LiveKitAPI(url, api_key, api_secret).room`.
- `WebhookReceiver(token_verifier)` موجودة وجاهزة لاستخدامها في Part 26
  (التحقق من توقيع الـ webhook) — اتأكدت من وجودها بس متستخدمش دلوقتي،
  زي ما اتطلب بالظبط ("جهّز endpoint فاضي بس").

### 2) `groups/live_provider.py` — دوال sync بترمي async جواها

بما إن المشروع كله (views، tasks) sync بالكامل (function-based views
عادية، Celery tasks عادية من غير `async def`)، ومحولش المشروع كله
لـ async عشان مكتبة واحدة بس، الحل: كل دالة في `live_provider.py`
(`create_room`, `generate_access_token`, `end_room`) هي دالة **sync**
عادية، وبتلف الـ coroutine بتاعتها جوه `asyncio.run()` داخليًا. الـ
caller (أي view في Part 24/25) هيستخدمها زي أي دالة sync عادية من غير
ما يعرف إن فيه async تحتها خالص — التفاصيل دي محصورة بالكامل جوه الملف.

- `create_room(session)`: بتاخد `GroupLiveSession` instance (من غير ما
  تحفظه — مفيش `.save()` جوه الدالة، مسؤولية الحفظ للـ caller)، بتبني
  اسم روم فريد (`group-<group_id>-live-<session_id>-<8 hex عشوائي>`)،
  بتنشئ الروم فعليًا عند LiveKit، وبترجع الاسم ده كـ `room_identifier`.
  `empty_timeout=3600` (ساعة) — لو الروم فاضي من غير حد متصل لمدة
  الوقت ده، LiveKit بيقفله تلقائيًا (طبقة حماية إضافية بعيدًا عن
  `end_room` الصريحة في Part 24). `max_participants=0` = من غير حد
  أقصى (نفس فلسفة "one-to-many مش محدود" من قرار Part 22).
- `generate_access_token(session, user, role='host'|'viewer')`: بتتحقق
  إن `role` قيمة صحيحة وإن `session.room_identifier` موجود (يعني
  `create_room` اتنفذت قبل كده)، وبعدين بتبني `VideoGrants` مختلفة حسب
  الدور: `host` → `can_publish=True` (يقدر ينشر كاميرا/شاشة)، `viewer`
  → `can_publish=False` (مشاهدة بس). التوكن مدته 6 ساعات (`_TOKEN_TTL`
  — قيمة اخترتها بنفسي، مفيش تحديد صريح في الطلب الأصلي؛ سهل تتغير لو
  Ahmed عايز مدة مختلفة). الـ `identity` بتاعة المستخدم في LiveKit هي
  `user-<pk>` (فريدة ومستقرة)، والـ `name` المعروض هو `get_full_name()`
  أو `username` لو مفيش اسم كامل.
- `end_room(session)`: بتقفل الروم فعليًا عند LiveKit (بتفصل أي حد
  متصل دلوقتي). لو الروم مش موجود أصلاً عند المزود (اتقفل لوحده بسبب
  `empty_timeout`، أو حصل خطأ تاني)، بنسجل تحذير في اللوج (`logger.warning`)
  بدل ما نرمي استثناء يوقف الـ view اللي بينادي الدالة — النتيجة
  النهائية المطلوبة (الروم مقفول) متحققة أصلاً في الحالة دي، فمفيش
  داعي نفشل العملية كلها بسببها.
- `LiveProviderError`: استثناء عام واحد (مش كذا نوع استثناء مختلف)
  بيتغطى بيه أي فشل — إعدادات ناقصة (`LIVEKIT_URL`/`API_KEY`/`API_SECRET`
  فاضيين) أو فشل فعلي في نداء الـ API. أي view في الأجزاء الجاية لازم
  يمسك النوع ده تحديدًا ويعرض رسالة واضحة للمستخدم بدل صفحة 500 خام.

### 3) إعدادات LiveKit في `settings.py` — `config()` مش `os.environ.get`

نص خطة المرحلة الثانية (Part 23) اقترح حرفيًا استخدام `os.environ.get`،
لكن كل سطر حساس تاني في `Eduvia/settings.py` (`SECRET_KEY`، `REDIS_URL`،
`EMAIL_HOST_PASSWORD`، إلخ) بيستخدم `config()` من `python-decouple`.
اخترت الاتساق مع الملف الفعلي بدل الصياغة الحرفية للطلب — نفس السلوك
العملي (قراءة من متغير بيئة + قيمة افتراضية) بيتحقق بالطريقتين، فمفيش
أي خسارة وظيفية، بس الملف بيفضل متسق 100% مع نفسه. القيم الافتراضية
التلاتة (`LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`) فاضية
عمدًا — مفيش أي مفتاح حقيقي مكتوب في الكود.

### 4) `groups/webhooks.py` — ملف منفصل عن `groups/views.py`، مش تعديل عليه

⚠️ **مهم**: `groups/views.py` (771 سطر من Part 15) **مكانش من ضمن
الملفات اللي اتبعتلي في جلسة Part 23 دي**. الطلب الأصلي بيقول "جهّز
endpoint فاضي دلوقتي بس... متعملش فيه أي منطق دلوقتي" — ده كان ممكن
يتحط كـ view جديدة جوه `views.py`، لكن بدل ما أعدّل ملف كبير (771 سطر)
من غير ما أشوف نسخته الحقيقية فعليًا، عملت `groups/webhooks.py` كملف
جديد منفصل تمامًا فيه الـ view الفاضية (`live_webhook`)، و`groups/urls.py`
بيستورد منه مباشرة (`from . import webhooks`) بدل ما يستورد من
`views.py`.

السبب مش بس حذر — نفس الدرس اتوثق أكتر من مرة قبل كده في PROGRESS
(Part 15: النسخة الأولى من `groups/views.py` اتعملت من التوثيق مش من
الملف الحقيقي وسببت مشكلة حقيقية؛ Part 20: الالتزام الصريح بالعمل على
النسخ الفعلية المبعوتة بس). عزل الـ webhook في ملف مستقل بيضمن **صفر
احتمال تعارض أو مسح غير مقصود** لأي حاجة موجودة بالفعل في `views.py`
بعد Part 15 — من غير ما نضطر نستنى ملف الـ views عشان نكمل الجزء ده.

فلسفيًا الفصل ده منطقي في حد ذاته برضه (مش بس حل مؤقت للمشكلة اللي
فوق): الـ webhook مش "صفحة" بيفتحها مستخدم عادي من المتصفح، هو نقطة
اتصال Server-to-Server من مزود خارجي (LiveKit)، فوجوده في ملف منفصل
بيوضح الفرق ده بصريًا في بنية المشروع — ونفس روح فصل `live_provider.py`
عن الـ views العادية المطلوبة صراحة في نص الجزء.

**لو Ahmed حابب يدمج الـ webhook جوه `views.py` بدل كده** (مثلاً عشان
يفضل كل حاجة في مكان واحد)، سهل جدًا في Part 26 — نقل دالة `live_webhook`
من `webhooks.py` لـ `views.py` وتغيير الـ import سطر واحد في `urls.py`،
من غير أي أثر على أي حاجة تانية.

**الـ view نفسها (`live_webhook`)**:
- `@csrf_exempt` — الطلب جاي من سيرفر LiveKit الخارجي، مش من متصفح فيه
  CSRF token بتاع Django.
- `@require_POST` — أي method تاني (GET مثلاً) بيترفض من الأساس.
- الجسم فاضي تمامًا (`return HttpResponse(status=200)`) — من غير أي
  قراءة/تحقق من محتوى الطلب، زي ما اتطلب بالظبط. هيتملى في Part 26
  بمنطق: التحقق من التوقيع (`WebhookReceiver` + `TokenVerifier` —
  اتأكدت إنهم موجودين في المكتبة فعليًا)، قراءة `WebhookEvent`، وتحديث
  `GroupLiveSession` المناسبة (`status='ended'` + `recording_url`).

### 5) مسار الـ URL: `groups/live/webhook/`

ضفت `path('live/webhook/', webhooks.live_webhook, name='live_webhook')`
في `groups/urls.py`، **قبل** الـ pattern العام `<int:group_id>/` في آخر
الملف (نفس الملاحظة الموثقة في Part 12 عن ترتيب الـ paths — مع إن
`live/webhook/` أصلاً مركّبة من segment زيادة (`live/` + `webhook/`)
فمش هتتفسر كـ `<int:group_id>/` أصلاً حتى لو كانت تحت، لكن فضّلت الترتيب
الواضح ده للقراءة). الاسم النهائي الكامل للمسار:
`/groups/live/webhook/` (بافتراض إن `groups/` مربوطة بنفس الـ prefix
المستخدم في `Eduvia/urls.py` من Part 7 — `path('groups/',
include('groups.urls', ...))`).

### 6) `groups/management/commands/test_live_provider.py` — الاختبار اليدوي المطلوب

عملت Django management command (`python manage.py test_live_provider`)
بدل script منفصل — عشان يستفيد تلقائيًا من إعدادات Django (`settings.py`،
الاتصال بالداتابيز لجيب `TeacherGroup` حقيقي) من غير أي setup إضافي.
بيمشي على التسلسل الطبيعي الكامل: `create_room` → `generate_access_token`
(`role='host'`) → `generate_access_token` (`role='viewer'`) → `end_room`،
وبيطبع نتيجة كل خطوة أو يوقف برسالة `CommandError` واضحة لو خطوة فشلت.
بيقبل `--group-id` اختياري (لو مش متحدد، بياخد أول `TeacherGroup` موجود
في الداتابيز تلقائيًا). **الجلسة التجريبية (`GroupLiveSession`) بتتعمل
في الذاكرة بس من غير `.save()`** — الأمر ده مش بيضيف أي بيانات تجريبية
دايمة في الداتابيز، هدفه التأكد من تكامل LiveKit نفسه بس.

⚠️ **لسه محتاج تشغيل فعلي على سيرفر Ahmed**: الأمر ده اتكتب واتفحص
syntax بنجاح (`py_compile`)، لكن **معملتش أي اختبار فعلي مقابل سيرفر
LiveKit حقيقي** — مفيش سيرفر LiveKit شغال متاح في بيئة كتابة الجزء ده.
لازم Ahmed يشغّل `python manage.py test_live_provider` فعليًا بعد ما
يظبط `LIVEKIT_URL`/`LIVEKIT_API_KEY`/`LIVEKIT_API_SECRET` ويشغّل سيرفر
LiveKit (self-hosted أو Cloud) قبل ما نعتبر Part 23 "شغالة" 100% —
تفصيل ده أهم حاجة مفتوحة في الجزء ده.

## قرارات معمارية اتاخدت (Part 24)

### 1) العمل على `groups/views.py` الحقيقي مباشرة (مش ملف منفصل زي webhooks.py)

في Part 23، `groups/views.py` (771 سطر) مكانش متاح، فاتعمل عزل احترازي
(`groups/webhooks.py` منفصل). في الجزء ده Ahmed بعت النسخة الحقيقية
فعليًا (views.py، urls.py، models.py، group_detail.html، live_provider.py،
access.py، decorators.py)، فالـ views الجديدة (`create_live_session`،
`live_broadcast`، `end_live_session`) اتحطت **جوه `groups/views.py`
نفسه** (patch مباشر — إضافة، مش استبدال أو حذف لأي سطر موجود)، مش في
ملف منفصل — مفيش داعي للعزل الاحترازي دلوقتي بما إننا شغالين على النسخة
الحقيقية. باقي الملف (كل الـ views من Part 7 لحد Part 15) **متلمسش
خالص** — التعديلات كلها: (1) إضافة imports جديدة فوق (`settings`،
`require_POST`، `GroupLiveSession`، `live_provider` functions)، (2)
إضافة قسم كامل جديد "Part 24" فيه 3 views + helper واحد قبل قسم
"Part 12/13: Group content page"، (3) تعديل بسيط (إضافة سطرين context،
مش حذف حاجة) في `group_detail` نفسها.

### 2) `_get_owned_group_or_403` — helper جديد بسيط

الثلاث views الجديدة كلهم محتاجين نفس الفحص بالظبط: "المستخدم الحالي هو
المدرس صاحب الجروب ده؟" (نفس نمط `upgrade_group` من Part 10 —
`group.teacher_id != request.user.id` → `PermissionDenied`). بدل ما
أكرر نفس السطرين ثلاث مرات، عملت helper واحد صغير
`_get_owned_group_or_403(request, group_id)` بيرجع الـ `TeacherGroup` أو
يرمي 403. مش decorator (زي `instructor_required`) لإنه محتاج
`group_id` من الـ URL، فأسهل يتنادى كسطر أول في كل view بدل ما نلف
الـ decorator بمنطق إضافي.

### 3) تسلسل "دلوقتي" (`start_choice == 'now'`) في `create_live_session`

عشان `create_room()` في `live_provider.py` تقدر تستخدم `session.pk` في
اسم الروم (`group-<group_id>-live-<session_id>-<hex>`)، لازم الـ
`GroupLiveSession` يتحفظ في الداتابيز الأول (`status='scheduled'` مبدئي)
قبل ما ننادي `create_room()`. لو `create_room()` فشلت
(`LiveProviderError` — مثلاً إعدادات LiveKit ناقصة أو السيرفر مش راد)،
بنمسح السجل اللي اتعمل (`session.delete()`) بدل ما نسيبه "scheduled"
يتيم من غير أي داعي حقيقي — القرار ده بيمنع تراكم صفوف فاشلة في
`GroupLiveSession` من كل محاولة بدء بث فشلت لأي سبب فني. لو نجحت،
بنحدّث نفس الصف (`room_identifier`, `status='live'`, `started_at`) بدل
ما ننشئ صف جديد.

### 4) تسلسل "جدولة" (`start_choice == 'schedule'`)

**مفيش أي نداء لـ LiveKit خالص** وقت الجدولة — `GroupLiveSession`
بتتعمل بـ `status='scheduled'` و`scheduled_at` بس، من غير `room_identifier`
(هيفضل فاضي لحد ما المدرس فعليًا "يبدأ" الجلسة المجدولة دي). ⚠️ **ملحوظة
مفتوحة مهمة**: الطلب الأصلي (نص خطة المرحلة الثانية) ماقالش صراحة إزاي
المدرس "يبدأ" جلسة كانت متجدولة من قبل (يعني يحوّلها من `scheduled` لـ
`live` فعليًا وينشئ الروم وقتها) — الجزء ده (24) بيغطي بس "دلوقتي" (بينشئ
الروم فورًا) و"جدولة" (بيسجل الميعاد بس، من غير أي زرار "ابدأ الجلسة
المجدولة دي دلوقتي" لسه). ده فجوة وظيفية حقيقية محتاجة قرار من Ahmed —
إما (أ) إضافة زرار "ابدأ" على كل صف في `upcoming_group_live_sessions`
جوه `group_detail.html` بينادي `create_room()` لنفس الـ `GroupLiveSession`
الموجودة (مش ينشئ واحدة جديدة)، أو (ب) اعتبار إن المدرس هيرجع لصفحة
"ابدأ بث مباشر" تاني وقت الميعاد وينشئ جلسة "دلوقتي" منفصلة (والمجدولة
القديمة تفضل معلّقة `scheduled` من غير أي تحديث). الحل الحالي أقرب لـ (ب)
ضمنيًا (مفيش أي كود بيربطهم)، لكن ده مش قرار واعي اتاخد بل فجوة —
موثقة هنا صراحة عشان متتنسيش، والحل الأنضف تقنيًا هو (أ) ولازم يتحل في
جزء لاحق (يفضل قبل Part 25، لإن الطالب المفروض يشوف الجلسة "بدأت فعليًا"
مش بس "معدّاها ميعادها المجدول").

### 5) `live_broadcast` — توليد توكن جديد في كل GET

الـ view بتنادي `generate_access_token(session, request.user, role='host')`
في كل مرة الصفحة بتتفتح (مش بس أول مرة) — يعني لو المدرس عمل refresh
للصفحة، هياخد توكن جديد بدل ما يعتمد على القديم. ده اختيار بسيط ومقصود:
التوكن مدته 6 ساعات (`_TOKEN_TTL` من Part 23) فمفيش أي ضرر من توليد
واحد جديد كل مرة، وده بيغني عن أي منطق تخزين/تحديث للتوكن في الـ
session أو الداتابيز.

### 6) `end_live_session` — قفل الجلسة محليًا حتى لو `end_room()` فشلت

لو `end_room()` رمت `LiveProviderError` (فشل حقيقي في التواصل مع
LiveKit، مش مجرد "الروم مش موجود" اللي `end_room()` نفسها بتتعامل معاها
بهدوء من غير استثناء أصلاً — Part 23)، الـ view بتعرض رسالة تحذير
(`messages.warning`) لكن **برضه بتحدّث `status='ended'` محليًا**. القرار
ده مقصود: لو سبنا الجلسة `status='live'` بسبب خطأ في التواصل مع
LiveKit، هتفضل عالقة "شغالة" في نظر باقي الكود (`current_live_session`
في `group_detail`) حتى لو فعليًا اتقفلت أو المدرس مش قادر يوصلها —
تجربة أسوأ من عدم تطابق نادر بين حالة LiveKit الفعلية والداتابيز.

### 7) `group_detail` — قسم "اللايف المباشر" الجديد منفصل بصريًا عن القديم

زي ما اتوضح في Part 22 (الموديل نفسه مستقل عن `workshops.LiveSession`)،
التمبلت اتعدّل بحيث القسم الجديد (`.live-hero` — كارت مميز فوق) واضح
بصريًا إنه نظام مختلف عن قسم "جلسات لايف شغالة دلوقتي" القديم تحته
(اللي لسه بيعرض `workshops.LiveSession`/Google Meet زي ما هو من Part
13، **متلمسش خالص**). للطالب (مش صاحب الجروب): لو فيه `current_live_session`
بيبان إشعار بسيط "فيه بث مباشر شغال دلوقتي" **من غير أي زرار دخول فعلي**
— الانضمام الفعلي للطالب هو نطاق Part 25 (مطلوب صراحة في خريطة
الأجزاء)، فمفيش أي رابط لصفحة `live_broadcast` (دي للمضيف بس أصلاً،
`role='host'` بيدّي صلاحية نشر) ولا أي صفحة مشاهدة للطالب اتعملت في
الجزء ده عمدًا.

### 8) LiveKit Client SDK (JS) — نسخة UMD من jsDelivr، `LivekitClient` global

`live_broadcast.html` بيحمّل `livekit-client@2` (UMD build) من
`cdn.jsdelivr.net`، اللي بيعرّف global object اسمه `LivekitClient` (فيه
`Room`, `RoomEvent`, إلخ) — نفس اسم الـ namespace الموثق في توثيق
LiveKit الرسمي للـ JS SDK. الكود بيستخدم:
- `new LivekitClient.Room({ adaptiveStream: true, dynacast: true })`
- `room.connect(livekitUrl, token)`
- `room.localParticipant.setCameraEnabled/setMicrophoneEnabled/setScreenShareEnabled(bool)`
- `room.on(LivekitClient.RoomEvent.LocalTrackPublished, ...)` لعرض
  المعاينة المحلية.

⚠️ **نفس تحذير Part 23 بالظبط**: الكود ده اتكتب حسب توثيق livekit-client
الرسمي (مش افتراض من الذاكرة القديمة)، لكن **لسه معملوش verify فعلي على
متصفح حقيقي متصل بسيرفر LiveKit** — لازم Ahmed يجرب فعليًا (يبدأ بث من
صفحة `create_live_session`، يتأكد إن الكاميرا/الشاشة بتتنشر صح على
`live_broadcast.html`) قبل ما نعتبر واجهة المدرس شغالة 100%. تفاصيل
الاختبار المطلوب في سجل الجزء تحت.

### 9) الفحص عن Django form validation جاهز — مفيش استخدام لـ ModelForm

فورم `create_live_session` (title/description/mode/start_choice/scheduled_at)
اتكتب بقراءة `request.POST` مباشرة (زي نمط `create_group`/`upgrade_group`
الموجود بالفعل في الملف من Part 7/10) بدل عمل `ModelForm` جديد في
`groups/forms.py` — نفس النمط المتسق مع باقي الفورمز غير المرتبطة
بملفات (`PaymentProofForm` هي الوحيدة اللي `ModelForm` لإنها بترفع
صورة). تحويل `scheduled_at` من نص لـ `datetime` بيتم بـ
`timezone.datetime.fromisoformat()` + `timezone.make_aware()` لو الناتج
naive — نفس تنسيق `<input type="datetime-local">` القياسي في المتصفحات.

## سجل الأجزاء

### Part 22 — قرار معماري لبنية اللايف + موديل GroupLiveSession
الحالة: تم
تفاصيل:
- راجعت `Eduvia/settings.py`، `Eduvia/asgi.py`، `workshops/models.py`،
  `workshops/consumers.py`، `workshops/routing.py`، `projects/consumers.py`،
  `projects/routing.py`، و`requirements.txt` قبل أي قرار — تفاصيل كاملة
  للي اتلاقى فوق في "قرارات معمارية".
- القرار: **LiveKit** (self-hosted بـ Docker أو LiveKit Cloud — قرار
  تشغيلي منفصل هيتاخد وقت Part 23) بدل بناء WebRTC/SFU من الصفر بـ
  Django Channels وحدها، وبدل Jitsi/Agora/Twilio/Zoom. الأسباب والبدائل
  المرفوضة كاملة فوق.
- أضفت موديل `GroupLiveSession` في `groups/models.py` (آخر موديل في
  الملف، بعد `GroupChatMessage` من Part 14) بكل الحقول المطلوبة بالظبط
  زي المواصفة، + `Meta.ordering` بسيط اخترته بنفسي.
- **تصحيح لاحق**: `related_name` على حقل `group` اتغيّر من
  `'live_sessions'` (كان بيعمل تعارض حقيقي مع `workshops.LiveSession.group`
  اللي بيرجع على نفس `TeacherGroup`) لـ `'group_live_sessions'` — اتلاقى
  عن طريق تشغيل `makemigrations --check --dry-run` فعليًا على السيرفر.
  تفاصيل كاملة فوق في "قرارات معمارية اتاخدت (Part 22)"، قسم 3.1.
- سجّلت الموديل في `groups/admin.py` (`GroupLiveSessionAdmin`) بنفس
  نمط باقي الموديلات، مع استخدام `_status_badge` الموجودة من Part 21.
- عملت migration جديدة `groups/migrations/0010_grouplivesession.py`
  (`CreateModel` بسيط).
- ✅ **اتأكد فعليًا على سيرفر Ahmed**: `makemigrations --check --dry-run`
  عدّى من غير أي تعارض related_name بعد التصحيح، `migrate` طبّق
  `groups.0010_grouplivesession` بنجاح، و`python manage.py check` رجع
  "System check identified no issues". الموديل شغال فعليًا دلوقتي.
- **ملاحظة تجميلية غير متعلقة (مش لازم تتصلح دلوقتي)**: بعد التطبيق،
  `makemigrations --check --dry-run` بيقترح migration إضافية
  (`0011_alter_groupchatmessage_id_alter_grouplivesession_id`) بسبب
  `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` في
  `settings.py` — الحقل `id` في migrations `GroupChatMessage` (من Part
  14، قبل أي تعديل مني) و`GroupLiveSession` (الجزء الحالي) اتسجلوا كـ
  `AutoField` عادي بدل `BigAutoField`. ده **تعارض نوع بيانات تجميلي
  بحت** (Django بيقترح توحيد النوع)، **مش خطأ ومش نتيجة مباشرة لتصحيح
  related_name** — موجود أصلاً من Part 14 قبل أي شغل في المرحلة
  الثانية. لو Ahmed حابب ينضّفه، `makemigrations` ثم `migrate` عاديين
  هيولّدوا الـ migration المقترحة دي ويطبقوها من غير أي خطر (مجرد
  `ALTER COLUMN` لنوع الرقم من `INTEGER` لـ `BIGINT`، بدون فقدان بيانات).
  اخترت متلمسهاش في الجزء ده لأنها برة نطاق "اعمل الموديل" المطلوب في
  Part 22.
- **مفيش أي كود تنفيذي تاني في الجزء ده غير كده** — مفيش views، مفيش
  تكامل فعلي مع أي مزود، مفيش تعديل على `requirements.txt` (هيتضاف
  `livekit-api` أو المكتبة المطلوبة في Part 23 لما نبدأ التكامل
  الفعلي) — زي ما اتطلب بالظبط ("دلوقتي بس اعمل الموديل").
- ⚠️ حاجات محتاجة قرار/انتباه من Ahmed قبل Part 23:
  1. **الأهم**: قرار Self-hosted (Docker) مقابل LiveKit Cloud — قرار
     تشغيلي (تكلفة/صيانة) مش هحسمه هنا، لازم Ahmed يحدده قبل ما نبدأ
     Part 23 (تجهيز `LIVEKIT_HOST`/`API_KEY`/`API_SECRET`).
     **⚠️ [تحديث Part 23]: القرار ده لسه معلّق — راجع أول قسم في
     "قرارات معمارية اتاخدت (Part 23)" فوق.**
  2. رقم الـ dependency في الـ migration الجديدة (`0009_...`) لازم
     يتراجع مقابل آخر migration فعلية موجودة على السيرفر الحقيقي —
     الملف اتكتب يدويًا مش بتشغيل فعلي لـ Django على السيرفر.
  3. **ملحوظة جانبية اتلاقت أثناء البحث (مش من مهام الجزء ده)**:
     `projects.routing.websocket_urlpatterns` مش مسجّلة في
     `Eduvia/asgi.py` (بس `workshops.routing` مسجّلة) — يعني أي
     WebSocket على `ws/room/<room_id>/` هيفشل فعليًا. برضه مفيش
     `CHANNEL_LAYERS` معرّف في `settings.py` خالص رغم إن
     `channels_redis` متثبتة — يعني حتى الـ consumers النصية الموجودة
     حاليًا (`LiveStreamConsumer`, `RoomConsumer`) مش هتشتغل فعليًا من
     غيره. الاتنين مش من مسؤولية Part 22، بس هيبقوا مهمين لما نوصل
     لتفعيل أي WebSocket signaling حقيقي في Part 23/24 (`CHANNEL_LAYERS`
     على الأقل هيبقى مطلوب فعليًا وقتها لو استخدمنا Channels كطبقة
     إشارة إضافية، أو ممكن أصلاً منحتاجهوش خالص لو LiveKit Client SDK
     بيتعامل مباشرة مع سيرفر LiveKit من غير ما يمر بـ Django Channels
     في نفس المسار).

### Part 23 — تجهيز خدمة البث (Provider integration: رومات + توكينات)
الحالة: تم — ✅ **اتأكد فعليًا**: `test_live_provider` اشتغل بنجاح على
سيرفر LiveKit حقيقي (تأكيد شفهي من Ahmed بعد الجزء ده، تفاصيل في "الحالة
الحالية" فوق). التكامل شغال فعليًا، مش مجرد syntax check.
تفاصيل:
- ثبّتت `livekit-api` فعليًا وراجعت توقيعات الـ SDK (`AccessToken`،
  `VideoGrants`، `LiveKitAPI.room.create_room/delete_room`،
  `WebhookReceiver`) بـ `inspect` قبل أي كود — تفاصيل كاملة فوق في
  "قرارات معمارية اتاخدت (Part 23)"، قسم 1.
- ضفت 3 إعدادات جديدة في `Eduvia/settings.py`: `LIVEKIT_URL`،
  `LIVEKIT_API_KEY`، `LIVEKIT_API_SECRET` — عن طريق `config()` من
  `python-decouple` (بدل `os.environ.get` المقترحة حرفيًا في نص الخطة)
  عشان الاتساق مع باقي الملف، قيم افتراضية فاضية، مفيش أي مفتاح حقيقي
  مكتوب في الكود. تفاصيل السبب فوق، قسم 3.
- عملت ملف جديد `groups/live_provider.py` فيه 3 دوال sync معزولة:
  `create_room(session)`، `generate_access_token(session, user, role)`،
  `end_room(session)` — كل واحدة بتلف نداء LiveKit (async بطبعه) جوه
  `asyncio.run()` داخليًا. استثناء عام واحد (`LiveProviderError`)
  لأي فشل (إعدادات ناقصة أو خطأ فعلي من المزود). تفاصيل كاملة فوق، قسم 2.
- ضفت `livekit-api==1.2.0` لـ `requirements.txt` (النسخة اللي اتثبتت
  واتفحصت فعليًا) — مفيش تعديل يدوي لأي تبعية فرعية (aiohttp،
  livekit-protocol، إلخ)، دول بيتجابوا تلقائيًا مع `pip install -r`.
- عملت Django management command
  `groups/management/commands/test_live_provider.py` (زي ما اتطلب —
  "اختبار يدوي بسيط") بيمشي على التسلسل الكامل (create_room →
  generate_access_token host → generate_access_token viewer → end_room)
  ويطبع نتيجة كل خطوة أو يوقف بخطأ واضح. بيقبل `--group-id` اختياري.
  تفاصيل فوق، قسم 6.
- **مفيش تعديل على `groups/views.py` خالص** — الملف ده متبعتش في
  الجلسة دي (771 سطر من Part 15)، فعملت الـ webhook placeholder في ملف
  جديد منفصل تمامًا `groups/webhooks.py` بدل ما ألمس ملف مبشوفهوش —
  تفاصيل السبب الكامل فوق، قسم 4 (نفس الدرس من Part 15/20).
  - `groups/webhooks.py::live_webhook`: view فاضية تمامًا
    (`@csrf_exempt` + `@require_POST` + `HttpResponse(status=200)`)،
    زي ما اتطلب بالظبط ("متعملش فيه أي منطق دلوقتي"). هتتملى في
    Part 26.
- عدّلت `groups/urls.py`: ضفت
  `path('live/webhook/', webhooks.live_webhook, name='live_webhook')`
  (مع `from . import webhooks` جديد فوق)، قبل الـ pattern العام
  `<int:group_id>/` في آخر الملف. باقي الملف (كل الـ paths من
  Part 7-12) **متلمسش خالص**.
- **مفيش أي تعديل على `groups/models.py`، `groups/admin.py`، أو
  migration** في الجزء ده — الجزء ده بالكامل طبقة تكامل + إعدادات +
  URL جديد، زي ما اتطلب بالظبط.
- اتفحص syntax كل الملفات الجديدة/المعدلة (`python -m py_compile`) —
  عدّت كلها من غير أخطاء.
- ⚠️ حاجات محتاجة قرار/انتباه من Ahmed قبل Part 24:
  1. ✅ **[تحديث]**: قرار الاستضافة وقيمة `LIVEKIT_URL` بقوا محسومين
     عمليًا — فيه سيرفر LiveKit شغال واتأكد إنه بيشتغل صح (راجع "الحالة
     الحالية" فوق). التفاصيل الدقيقة (self-hosted ولا Cloud) مش موثقة
     صراحة هنا.
  2. ✅ **[تحديث]**: `python manage.py test_live_provider` اتشغل فعليًا
     على سيرفر Ahmed ونجح — التكامل شغال فعليًا مش syntax check بس.
  3. مدة صلاحية التوكن (`_TOKEN_TTL = 6 ساعات` في `live_provider.py`)
     اخترتها بنفسي — مفيش تحديد صريح في الطلب الأصلي. سهل التغيير لو
     Ahmed عايز مدة مختلفة.
  4. `empty_timeout` (ساعة) و`max_participants=0` (من غير حد أقصى) في
     `create_room()` اخترتهم بنفسي برضه — نفس الملاحظة، سهل التعديل.
  5. لو Ahmed حابب يدمج `groups/webhooks.py::live_webhook` جوه
     `groups/views.py` بدل ما يفضل ملف منفصل (مثلاً بعد ما يراجع
     `views.py` الحقيقي ويتأكد مفيش تعارض)، النقل بسيط جدًا (نقل دالة
     واحدة + تغيير import سطر واحد في `urls.py`) — ممكن يحصل في
     Part 26 وقت ما الـ webhook يتملى بمنطق فعلي.

### Part 24 — واجهة المدرس: بدء/جدولة لايف من صفحة الجروب
الحالة: تم — ✅ **اتأكد فعليًا على متصفح حقيقي**: Ahmed جرّب السيناريو
الكامل (بدء بث "دلوقتي" → الكاميرا اشتغلت → المايكروفون اشتغل → مشاركة
الشاشة اشتغلت → زرار "إنهاء البث" رجّع المدرس لصفحة الجروب على طول من
غير أي خطأ). التكامل مع LiveKit JS Client SDK (`live_broadcast.html`)
شغال فعليًا 100% — مش مجرد كود مكتوب حسب التوثيق زي ما كان موثق قبل
كده. تفاصيل الاختبار الكامل في آخر الجزء ده.
تفاصيل:
- شغلت الجزء ده على النسخ الحقيقية اللي بعتها Ahmed فعليًا (`views.py`،
  `urls.py`، `models.py`، `group_detail.html`، `live_provider.py`،
  `access.py`، `decorators.py`) — مفيش أي إعادة بناء من التوثيق. تفاصيل
  السبب واختيار العمل المباشر على `views.py` (بدل ملف منفصل زي Part 23)
  فوق في "قرارات معمارية اتاخدت (Part 24)"، قسم 1.
- عدّلت `groups/views.py`:
  - imports جديدة: `from django.conf import settings`،
    `from django.views.decorators.http import require_POST`،
    `from .live_provider import LiveProviderError, create_room, end_room,
    generate_access_token`، وإضافة `GroupLiveSession` لاستيراد الموديلات
    الموجود.
  - `_get_owned_group_or_403(request, group_id)`: helper جديد (تفاصيل
    قسم 2 فوق).
  - `create_live_session(request, group_id)`: view جديدة (`@instructor_required`)
    — فورم title/description/mode/start_choice(+scheduled_at). تفاصيل
    التسلسلين ("دلوقتي"/"جدولة") فوق، قسم 3/4.
  - `live_broadcast(request, group_id, session_id)`: view جديدة
    (`@instructor_required`) — تتأكد إن الجلسة `status='live'` وبتاعة
    نفس المضيف، وتولّد توكن `role='host'` جديد في كل مرة (قسم 5)، وتعرض
    `groups/live_broadcast.html`.
  - `end_live_session(request, group_id, session_id)`: view جديدة
    (`@instructor_required` + `@require_POST`) — بتنادي `end_room()`
    وتحدّث `status='ended'` + `ended_at` (تفاصيل قسم 6).
  - `group_detail`: **تعديل إضافي بس (مفيش حذف)** — ضفت
    `current_live_session` (`status='live'`) و
    `upcoming_group_live_sessions` (`status='scheduled'`, مرتبة
    `scheduled_at`) للـ context. باقي الـ view (كل منطق Part 12/13/14/15،
    الـ ownership checks، الشات، attach/detach_session) **متلمسش خالص**.
  - **باقي الملف (كل الـ views من Part 7 لحد Part 15، والـ helpers
    `_is_instructor`/`instructor_required`/`_is_student`/`student_required`/
    `_get_active_subscription`) متلمسش خالص.**
- عدّلت `groups/urls.py`: ضفت 3 paths جديدة (`<int:group_id>/live/create/`،
  `<int:group_id>/live/<int:session_id>/broadcast/`،
  `<int:group_id>/live/<int:session_id>/end/`) قبل الـ pattern العام
  `<int:group_id>/` في آخر الملف (نفس ملاحظة الترتيب من Part 12/23،
  رغم إن الباترنز دي مركّبة من أكتر من segment فمش هتتعارض عمليًا حتى
  لو اتحطت بعده). باقي الملف **متلمسش خالص**.
- أنشأت `groups/templates/groups/create_live_session.html`: فورم بسيط
  بنفس نظام "Obsidian Academy" (نفس CSS variables المستخدمة في
  `group_detail.html` بالحرف — الملف الوحيد المتاح لي كمرجع تصميم في
  الجلسة دي). عناصر: حقل عنوان، وصف اختياري، اختيار mode كـ option cards
  (كاميرا/شاشة/الاتنين)، اختيار "دلوقتي"/"جدولة" كـ option cards، وحقل
  `scheduled_at` (`datetime-local`) بيظهر/يختفي بجافاسكريبت بسيط حسب
  الاختيار.
- أنشأت `groups/templates/groups/live_broadcast.html`: صفحة البث للمضيف
  — عناصر تحكم (كاميرا/ميكروفون/مشاركة شاشة حسب `session.mode`)، معاينة
  فيديو محلية (`<video>` tag)، وزرار "إنهاء البث" (فورم POST لـ
  `end_live_session`). عميل LiveKit JS (تفاصيل قسم 8 فوق).
- عدّلت `groups/templates/groups/group_detail.html`:
  - CSS جديد (`.live-hero`, `.live-hero-btn`, `.scheduled-live-list`,
    `.scheduled-live-row`) — إضافة في آخر `<style>` الموجود، **مفيش أي
    حذف أو تعديل على أي كلاس موجود قبل كده**.
  - قسم HTML جديد بعد `{% if messages %}...{% endif %}` ("Part 24") —
    كارت "اللايف المباشر" مميز بصريًا (`.live-hero`)، منفصل تمامًا عن
    قسم "جلسات لايف شغالة دلوقتي" القديم (workshops.LiveSession/Google
    Meet، Part 13) اللي فضل زي ما هو تحته. للمدرس صاحب الجروب: زرار
    "أدخل البث" لو فيه لايف شغال (`current_live_session`)، أو زرار "ابدأ
    بث مباشر" لو لأ. للطالب: إشعار بسيط بس (بدون زرار دخول — نطاق
    Part 25). قايمة "لايفات مجدولة قادمة" (`upcoming_group_live_sessions`)
    تحتها لو موجودة. تفاصيل قسم 7 فوق.
  - **باقي الملف (كل شات Part 14، جلسات workshops.LiveSession من
    Part 13، manage-box، إلخ) متلمسش خالص.**
- **مفيش أي migration جديدة أو تعديل على `groups/models.py`/
  `groups/admin.py`/`groups/live_provider.py`/`groups/access.py` في
  الجزء ده** — الجزء ده كله views + templates + urls جديدة/معدّلة.
- اتفحص syntax كل الملفات المعدّلة/الجديدة (`python -m py_compile` على
  `views.py`/`urls.py`، وفحص توازن `{% if/for %}` ↔ `{% endif/endfor %}`
  في التلات تمبلتس) — عدّت كلها من غير أخطاء.
- ✅ **اختبار فعلي مؤكد من Ahmed (السيناريو الكامل)**:
  1. المدرس فتح `create_live_session.html`، اختار "دلوقتي"، دوس إرسال.
  2. `create_room()` نجحت، وانتقل لصفحة `live_broadcast.html`.
  3. المتصفح طلب صلاحية الكاميرا والمايكروفون — **الكاميرا اشتغلت
     فعليًا** (المعاينة المحلية ظهرت)، **والمايكروفون اشتغل فعليًا**.
  4. **مشاركة الشاشة اشتغلت فعليًا** (`getDisplayMedia` نجحت ونشرت الشاشة).
  5. دوس "إنهاء البث" → `end_room()` نجحت → `status='ended'` +
     `ended_at` اتسجلوا → **رجّع المدرس لصفحة الجروب على طول من غير أي
     مشكلة أو خطأ**.
  النتيجة: تكامل LiveKit (Server SDK من Part 23 + Client SDK من Part 24)
  شغال فعليًا بالكامل على الاتجاهين (توليد التوكنات من الباك إند، ونشر
  الميديا من المتصفح). ده أول تأكيد فعلي (مش نظري) إن اختيار LiveKit من
  Part 22 كان قرار سليم من الناحية العملية.
- ⚠️ حاجات محتاجة قرار/انتباه من Ahmed:
  1. **فجوة وظيفية حقيقية**: مفيش زرار/مسار لـ "ابدأ الجلسة المجدولة
     دي دلوقتي" — تفاصيل كاملة في قسم 4 فوق ("قرارات معمارية اتاخدت
     (Part 24)"). لازم قرار قبل Part 25 (الطالب المفروض يشوف اللايف
     "شغال فعليًا" مش بس "فات ميعاده المجدول").
  2. ✅ **[تحديث — اتحل]**: عميل LiveKit JS اتأكد إنه شغال فعليًا على
     متصفح حقيقي (كاميرا + مايك + مشاركة شاشة + إنهاء نظيف) — راجع
     "اختبار فعلي مؤكد من Ahmed" فوق. مبقاش فيه أي شك في تكامل الـ
     JS SDK دلوقتي.
  3. الطالب دلوقتي بيشوف إشعار بسيط "فيه بث مباشر شغال دلوقتي" من غير
     أي إجراء فعلي — ده متعمّد (نطاق Part 25)، لكن لو حابب تسريع الجزء
     ده مع بعض ممكن نعمل Part 25 كامتداد مباشر بدل جزء منفصل.
  4. لو المدرس عمل "دلوقتي" وفشل `create_room()` (LiveKit مش راد
     مثلاً)، بيترجّع لصفحة الجروب برسالة خطأ من غير أي retry تلقائي —
     المدرس لازم يضغط "ابدأ بث مباشر" تاني يدويًا.
  5. مفيش أي حد أقصى لعدد اللايفات المجدولة المعروضة في
     `upcoming_group_live_sessions` (`group_detail`) — لو تراكمت مع
     الوقت، ممكن نحتاج `[:N]` أو pagination بسيطة (نفس ملاحظة حد الـ
     100 رسالة شات من Part 14).

## الحالة الحالية
آخر جزء منفذ: Part 25 (واجهة الطالب: الانضمام للايف داخل الجروب) —
تفاصيل كاملة في آخر قسم "Part 25" تحت. Part 24 (واجهة المدرس) اتأكدت
فعليًا بالكامل على متصفح حقيقي زي ما موثق تحت. تكامل LiveKit (Server SDK
من Part 23 + Client SDK للمضيف من Part 24) شغال فعليًا 100%. الـ Client
SDK بتاع المشاهد (Part 25، الجزء الحالي) لسه معملوش verify فعلي على
متصفح حقيقي — تفاصيل الملاحظة المفتوحة دي في آخر قسم تحت.

(باقي محتوى الملف من Part 22-24 زي ما هو — راجع النسخة السابقة المرسلة
لتفاصيل قرارات Part 22/23/24 الكاملة، غير مكرر هنا لتوفير المساحة.)

## قرارات معمارية اتاخدت (Part 25)

### 1) الصلاحية: `student_required` + `GroupMembership` + `is_group_content_accessible` — بالظبط زي باقي المشروع من Part 15

الـ view الجديدة (`join_live_session`) بتستخدم `@student_required` (نفس
decorator من Part 7/11، بيتحقق من `role == 'student'`)، وبعدين فحصين
إضافيين صريحين جوه الدالة نفسها:
1. `GroupMembership.objects.filter(student=request.user, group=group).exists()`
   — لو مش عضو فعلي في الجروب بتاع الجلسة دي، `PermissionDenied` (403).
   ده تحقق مباشر (مش بيعتمد على أي حالة محفوظة زي فلاج على الموديل)،
   بنفس فلسفة كل فحوصات العضوية التانية في المشروع (`group_detail`،
   `_can_access_group_session` في `workshops/views.py`).
2. `is_group_content_accessible(group)` من `groups/access.py` (Part
   15) — لو اشتراك المدرس مش نشط دلوقتي (الجروب متجمد)، رسالة
   `GROUP_FROZEN_MESSAGE` بالظبط + ريدايركت لـ `my_learning_groups`،
   بنفس النمط المستخدم في `group_detail` و`watch_live`/`watch_recording`
   في `workshops/views.py`. **مفيش أي منطق صلاحيات بديل أو مختصر اتعمل
   هنا** — نفس الدالة المركزية بالحرف، زي ما طلبت التعليمات صراحة
   ("اقرأ `groups/access.py`... عشان تستخدمه بالظبط زي ما هو").

الترتيب مقصود: فحص العضوية (403) قبل فحص التجميد (رسالة + ريدايركت) —
نفس ترتيب الفحوصات المنطقي المستخدم في كل مكان تاني بالمشروع (هل
المستخدم أصلاً له حق يشوف الجروب ده؟ قبل هل محتواه متاح دلوقتي؟).

### 2) `join_live_session` — دالة واحدة بتتفرع على `session.status`، مش أربع views منفصلة

البرومبت الأصلي وصف 4 سيناريوهات مختلفة حسب حالة الجلسة (`scheduled`،
`live`، `ended`، وضمنيًا `canceled`)، لكن كلهم بيبدأوا بنفس فحص الصلاحية
بالظبط (عضوية + `is_group_content_accessible`). عشان كده اخترت view
واحدة بس (`join_live_session(request, session_id)`) بتعمل الفحص مرة
واحدة في الأول وبعدين تتفرع بـ `if/elif` على `session.status` — بدل 4
views منفصلة (كانت هتكرر نفس الفحص 4 مرات) أو URL منفصل لكل حالة (كان
هيعقّد التنقل من غير أي فايدة حقيقية، لأن الطالب أصلاً مش المفروض
يعرف/يحدد حالة الجلسة بنفسه، هو بس بيدوس على رابط "اللايف" وبنقرر
إحنا نعرضله إيه حسب الحالة الفعلية وقت الطلب).

### 3) `session_id` بس في الـ URL (من غير `group_id`)

خريطة الأجزاء اقترحت `join_live_session(request, session_id)` بالظبط
كده (من غير `group_id`)، وده قرار منطقي مستقل بذاته كمان: الجروب
مُشتق مباشرة من `session.group` (FK موجود بالفعل)، فمفيش داعي تكرار
`group_id` في الـ URL زي ما بقية مسارات Part 24 (`create_live_session`،
`live_broadcast`، `end_live_session`) بتعمل — دول محتاجين `group_id`
صراحة لإن `_get_owned_group_or_403` بتتحقق من ownership الجروب الأول
قبل ما تعرف أي جلسة، أما هنا الجلسة نفسها (`session_id`) كافية للوصول
لكل حاجة تانية. الرابط النهائي: `/groups/live/<session_id>/watch/` —
مسار مستقل مركّب من أكتر من segment (زي `live/webhook/` من Part 23)،
فمش هيتعارض مع الـ pattern العام `<int:group_id>/` في آخر `urls.py`
حتى لو اتحط قبله أو بعده.

### 4) حالة `scheduled`: شاشة انتظار + `meta refresh` بسيط بدل أي polling حقيقي

البرومبت طلب "شاشة انتظار بسيطة فيها ميعاد اللايف المتوقع" بس، من غير
أي تفصيل عن آلية التحديث. زودت تحسين UX بسيط: `<meta http-equiv="refresh"
content="30">` في `<head>` الصفحة (بس لما `view_mode == 'waiting'`) —
كل 30 ثانية الصفحة بترجع تعمل GET تاني على نفس الرابط، فلو المدرس بدأ
اللايف في الأثناء، الطالب هيلاقي نفسه اتنقل تلقائيًا لشاشة المشاهدة
الفعلية من غير أي ريفريش يدوي أو تعقيد JS/WebSocket. القرار ده اتاخد
عشان:
- يفضل متسق مع فلسفة باقي المشروع (مفيش "حاجة تحصل تلقائيًا بمرور
  الوقت" غير عن طريق Celery للـ backend، أو حاجة بسيطة جدًا زي دي
  للـ frontend — مفيش Django Channels/WebSockets مستخدمة فعليًا في أي
  مكان تاني في نظام الجروبات، ونفس الملاحظة اللي كانت موثقة من قبل عن
  الشات الجماعي في Part 14 اللي "مش real-time" بنفس السبب).
- 30 ثانية اخترتها بنفسي (مش متحددة في الطلب الأصلي) كتوازن معقول بين
  "الطالب يحس إنه هيتنقل بسرعة معقولة" و"مش إعادة تحميل مبالغ فيها كل
  ثانيتين". سهل التعديل (رقم واحد في الـ template) لو Ahmed عايز قيمة
  مختلفة.
- **مفيش أي نداء لـ LiveKit خالص** في الحالة دي (لا `create_room` ولا
  `generate_access_token`) — الروم أصلاً لسه مالوش وجود عند المزود،
  وده متسق تمامًا مع قرار Part 24 إن `create_room()` بتتنادى بس لما
  المدرس فعليًا يدوس "ابدأ بث مباشر" (`start_choice == 'now'`)، مش وقت
  الجدولة.

### 5) حالة `live`: `generate_access_token(role='viewer')` — نفس دالة Part 23 بالحرف

مفيش أي منطق توليد توكن جديد أو مختلف — استخدمت `generate_access_token`
الموجودة بالفعل في `groups/live_provider.py` من Part 23 زي ما هي بالظبط،
بس بـ `role='viewer'` بدل `'host'` (المستخدم في `live_broadcast` بتاعة
المدرس، Part 24). الفرق العملي بين الاتنين (`can_publish=True` للمضيف
مقابل `can_publish=False` للمشاهد) متضمن بالكامل جوه الدالة نفسها من
Part 23 — مفيش أي كود إضافي احتجت أكتبه هنا غير تمرير القيمة الصح
لـ `role`.

### 6) `watch_live_session.html` — ملف واحد بحالتين (`view_mode`)، مش ملفين منفصلين

بدل ما أعمل تمبلت منفصل لكل حالة (`live_waiting.html` و`live_watch.html`
مثلاً)، عملت ملف واحد (`groups/templates/groups/watch_live_session.html`)
بيتغيّر محتواه حسب متغير context بسيط (`view_mode = 'waiting' | 'live'`)
اللي بيحدده الـ view. السبب: الصفحتين بيشتركوا في نفس الـ layout الكامل
بالظبط (topbar، breadcrumb، footer، نفس CSS variables) — الفرق بينهم
محصور في المحتوى الأساسي جوه `.content-wrap` بس (صندوق انتظار بسيط
مقابل stage + عميل LiveKit)، فملف واحد بـ `{% if view_mode == ... %}`
أبسط للصيانة من ملفين شبه متطابقين. نفس المنطق المتبع فعليًا في
`create_live_session.html` (Part 24) اللي بيتغيّر شكل حقل الميعاد
بجافاسكريبت بسيط حسب اختيار "دلوقتي"/"جدولة" جوه نفس الملف.

### 7) عميل LiveKit JS للمشاهد: `TrackSubscribed` + `attach()` ديناميكي، من غير أي عناصر `<video>` ثابتة في الـ HTML

عكس `live_broadcast.html` (Part 24) اللي فيها عنصر `<video id="local-preview">`
ثابت من الأول (معاينة الكاميرا المحلية بتاعة المضيف نفسه بس)، هنا
المشاهد ممكن يستقبل أكتر من track (كاميرا، ومشاركة شاشة لو `mode='both'`)
من مشارك واحد (المدرس)، فبدل عنصر `<video>` ثابت واحد، الكود بيعمل
`document.createElement('video')` ديناميكي جوه `RoomEvent.TrackSubscribed`
لكل video track بييجي، ويضيفه جوه `#stage`. الصوت بيتعامل معاه بشكل
منفصل (`track.attach()` من غير عنصر بترجع/تنشئ `<audio>` تلقائي، بيتضاف
لـ `document.body` من غير عرض بصري — مش محتاجين نشوف عنصر صوت). عملت
كمان فحص على `room.remoteParticipants` مباشرة بعد الـ `connect()` (مش
بس الاعتماد على event مستقبلي) — عشان الحالة اللي المدرس يكون بدأ
النشر *قبل* ما الطالب يدخل الصفحة أصلاً (يعني الـ tracks كانت موجودة
من الأول)؛ `RoomEvent.TrackSubscribed` وحده مش هيغطي الحالة دي غالبًا
لأنه event بيتطلق لحظة الاشتراك اللي بيحصل غالبًا في نفس لحظة الاتصال،
لكن التكرار الصريح على `remoteParticipants` طبقة أمان إضافية بسيطة
تضمن إننا مانفوتش أي track موجود بالفعل.

⚠️ **نفس تحذير Part 23/24 بالظبط**: الكود اتكتب حسب توثيق `livekit-client`
الرسمي (`RoomEvent.TrackSubscribed`, `RoomEvent.TrackUnsubscribed`,
`RoomEvent.Disconnected`, `track.attach()`/`.detach()`,
`participant.videoTrackPublications`/`audioTrackPublications`)، لكن
**لسه معملوش verify فعلي على متصفح حقيقي (بدور المشاهد) مقابل سيرفر
LiveKit شغال وجلسة بث حقيقية من مدرس** — ده أهم حاجة مفتوحة في الجزء
ده. Ahmed لازم يجرب: مدرس يبدأ بث (Part 24، اتأكد شغال) → طالب عضو
في نفس الجروب يفتح `join_live_session` بتاع نفس الجلسة → يتأكد إن
الفيديو/الصوت بيظهروا فعليًا في `#stage` من غير أي console errors.

### 8) حالة `ended`: رسالة واضحة + رجوع لصفحة الجروب، **مش** ريدايركت لصفحة تسجيل وهمية

خريطة الأجزاء بتقول صراحة "وجّه الطالب تلقائيًا لصفحة التسجيل (هنبنيها
في Part 26) بدل ما يشوف صفحة فاضية" — لكن Part 26 (تسجيل تلقائي +
مكتبة VOD) **لسه معملوش خالص** في المشروع في اللحظة دي. عمل `redirect`
لـ URL name مش موجود (`groups:group_recordings` مثلاً) كان هيكسر
التطبيق بـ `NoReverseMatch` فورًا لأي جلسة خلصت. بدل كده، الحل المؤقت:
رسالة `messages.info` واضحة ("البث ده خلص. صفحة مشاهدة التسجيل هتتاح
قريبًا") + `redirect('groups:group_detail', ...)`. ده **مش** تجاهل
للمتطلب — ده أفضل سلوك ممكن فعليًا في اللحظة دي بما إن الوجهة النهائية
المطلوبة (صفحة التسجيل) مش موجودة بعد. ⚠️ **لازم** الجزء ده يتعدّل
فورًا لما Part 26 يتنفذ: استبدال الـ `messages.info` + `redirect`
بـ `redirect` حقيقي لصفحة/view مشاهدة التسجيل الجديدة (على الأرجح
`watch_recording` أو مشابه، حسب تسمية Part 26 الفعلية). التعديل المتوقع
سطرين بس (شرط `if session.status == 'ended':` في `join_live_session`).

### 9) حالة `canceled` (وأي قيمة مستقبلية غير متوقعة)

`GroupLiveSession.STATUS_CHOICES` (من Part 22) فيها قيمة `canceled`
لسه من غير أي view أو منطق فعلي بيحطها (مفيش زرار "إلغاء" اتعمل في أي
جزء لحد دلوقتي — دي فجوة قائمة من قبل الجزء ده، مش حاجة استحدثتها).
عشان `join_live_session` تبقى شاملة لكل قيم `status` الممكنة (حتى لو
بعضها مش قابل للحدوث فعليًا دلوقتي)، آخر `if` في الدالة بيتعامل مع
`canceled` وأي قيمة تانية مستقبلية بنفس الأسلوب (رسالة بسيطة + رجوع
لصفحة الجروب) بدل ما نسيب الدالة من غير أي `return` واضح لو `status`
جالها بقيمة غير متوقعة.

### 10) الروابط: `group_detail.html` و`my_learning_groups.html` — إضافة، مش استبدال

- **`group_detail.html`**: القسم `{% elif current_live_session %}`
  (للطالب العضو، مش المالك) كان فيه نص placeholder من Part 24 ("صفحة
  انضمام الطالب للايف هتتفعّل قريبًا") — استبدلته بزرار حقيقي "ادخل
  اللايف" يودّي لـ `join_live_session`. زودت كمان زرار صغير "الميعاد"
  جنب كل صف في قايمة "لايفات مجدولة قادمة" (`upcoming_group_live_sessions`)
  — بس للطالب العضو (`{% if not is_owner %}`)، لإن `join_live_session`
  محمية بـ `@student_required` والمدرس (`role='instructor'`) هيترفض
  لو حاول يفتحها، فمفيش داعي نعرضله رابط هيفشل. باقي الملف (الشات،
  قسم إدارة الجلسات، جلسات `workshops.LiveSession` القديمة) **متلمسش
  خالص**.
- **`my_learning_groups.html`**: زودت زرار "لايف دلوقتي" (أخضر، منفصل
  بصريًا عن زرار "دخول" البنفسجي العادي) بيظهر جنب كل جروب نشط عنده
  `GroupLiveSession` بحالة `live` دلوقتي، بيودّي مباشرة لـ
  `join_live_session` — بالظبط زي ما اتطلب ("يودي مباشرة للايف الشغال
  لو فيه واحد"). الزرار مش ظاهر لو مفيش لايف شغال، ولا لو الجروب متجمد.
- عدّلت `my_learning_groups()` (`groups/views.py`) بحيث كل صف بيحمل
  كمان `live_session` (أول `GroupLiveSession` بحالة `'live'` للجروب
  ده، أو `None`) — بس لو الجروب نشط أصلاً (`is_active`)، عشان نتجنب
  استعلام إضافي على جروب متجمد مش هيتعرض له زرار أي حال.

## سجل الأجزاء (تابع)

### Part 25 — واجهة الطالب: الانضمام للايف داخل الجروب
الحالة: تم — ⚠️ **لسه محتاج اختبار فعلي على متصفح حقيقي** (تفاصيل تحت).
تفاصيل:
- قريت `groups/access.py` كامل قبل أي كود (زي ما اتطلب صراحة) —
  استخدمت `is_group_content_accessible` و`GROUP_FROZEN_MESSAGE` منه
  زي ما هما بالظبط، من غير أي تعديل على الملف ده خالص.
- شغلت الجزء ده على النسخ الحقيقية اللي بعتها Ahmed (`views.py`،
  `urls.py`، `group_detail.html`، `my_learning_groups.html`،
  `create_live_session.html` كمرجع تصميم، `access.py`، `live_provider.py`،
  `models.py`) — مفيش أي إعادة بناء من التوثيق.
- عدّلت `groups/views.py`:
  - view جديدة `join_live_session(request, session_id)`
    (`@student_required`) — تفاصيل كاملة فوق في "قرارات معمارية".
  - `my_learning_groups()`: تعديل إضافي بس (مفيش حذف) — كل صف بقى
    بيحمل `live_session` كمان (تفاصيل قسم 10 فوق).
  - **باقي الملف (كل الـ views من Part 7 لحد Part 24) متلمسش خالص.**
- عدّلت `groups/urls.py`: ضفت path واحد جديد
  (`live/<int:session_id>/watch/` → `join_live_session`، اسمه
  `join_live_session`) — قبل الـ pattern العام `<int:group_id>/` في
  آخر الملف (نفس ترتيب باقي الملف). باقي الملف **متلمسش خالص**.
- أنشأت `groups/templates/groups/watch_live_session.html` (ملف جديد) —
  تفاصيل التصميم والـ JS كاملة فوق في "قرارات معمارية"، أقسام 6/7.
  نفس نظام "Obsidian Academy" حرفيًا (نفس CSS variables/topbar/footer
  من `live_broadcast.html`).
- عدّلت `groups/templates/groups/group_detail.html`: تعديلين بسيطين
  بس (إضافة، مش حذف) — زرار "ادخل اللايف" الحقيقي بدل نص placeholder،
  وزرار "الميعاد" في قايمة اللايفات المجدولة للطالب العضو بس. باقي
  الملف **متلمسش خالص**.
- عدّلت `groups/templates/groups/my_learning_groups.html`: زرار "لايف
  دلوقتي" + CSS جديد بسيط (`.live-now-btn`, `.live-now-dot`). باقي
  الملف **متلمسش خالص**.
- **مفيش أي migration جديدة أو تعديل على أي موديل** في الجزء ده — كله
  view + URL + templates، زي ما اتطلب بالظبط.
- اتفحص syntax (`python -m py_compile` على `views.py`/`urls.py`)
  وتوازن `{% if/for %}` ↔ `{% endif/endfor %}` في الثلاث تمبلتس
  (الجديد والمعدَّلين) — عدّت كلها من غير أخطاء.
- ⚠️ حاجات محتاجة اختبار/قرار من Ahmed قبل Part 26:
  1. **الأهم**: عميل LiveKit JS بتاع المشاهد (`watch_live_session.html`،
     حالة `live`) لسه معملوش verify فعلي على متصفح حقيقي — سيناريو
     الاختبار المطلوب موضح فوق في "قرارات معمارية"، قسم 7.
  2. **فجوة معروفة (موثقة عمدًا، مش هتتصلح إلا في Part 26)**: حالة
     `session.status == 'ended'` بترجع رسالة + redirect لصفحة الجروب
     بدل ريدايركت حقيقي لصفحة تسجيل (لإن Part 26 لسه معملوش) — تفاصيل
     كاملة فوق، قسم 8. **لازم** يتصلح فورًا في Part 26.
  3. الـ meta-refresh (30 ثانية) في شاشة الانتظار اخترته بنفسي — مفيش
     تحديد صريح في الطلب الأصلي. سهل التعديل (رقم واحد في التمبلت) لو
     Ahmed عايز قيمة مختلفة، أو حتى استبداله بمنطق JS `setTimeout`
     أكتر مرونة لاحقًا لو الأولوية اتغيرت.
  4. حالة `canceled` بترجع رسالة بسيطة بس — مفيش أي زرار/منطق فعلي في
     المشروع كله بيحط جلسة في الحالة دي أصلاً (فجوة قايمة من Part 22،
     مش من الجزء ده)، فده أقرب لطبقة أمان احترازية مش سيناريو
     متوقع حاليًا.

## Part 26 — Manual Recording Upload + VOD Library (نسخة معدّلة) ✅

### الهدف

استبدال نظام التسجيل التلقائي للبث المباشر (LiveKit Egress -> S3،
النسخة الأولى من Part 26 اللي كانت موثقة قبل كده) بنظام رفع تسجيلات
يدوي بالكامل، بناءً على طلب صريح من Ahmed. المدرس بيسجل الشاشة/الاجتماع
بالطريقة اللي يفضّلها (OBS / Zoom Recording / أي برنامج تاني) خارج
المنصة، وبعد ما اللايف يخلص بيرفع الملف يدويًا. الطالب بيوصل لنفس
النتيجة النهائية (مكتبة فيديوهات لكل Live Session) بنفس الطريقة زي قبل.

### التزام صارم بحدود الطلب

زي ما طلب Ahmed صراحة، **معملتش أي تعديل** على:
- Live Room Creation (`live_provider.py::create_room` لسه بتنشئ الروم
  فقط — بس اتشال منها نداء تفعيل التسجيل التلقائي).
- Streaming Provider integration (`generate_access_token`, `end_room`
  متلمسوش خالص).
- Token Generation.
- Permissions (`is_group_content_accessible`, `GroupMembership`,
  `_get_owned_group_or_403`, `_get_group_and_membership_or_403` — كلهم
  زي ما هما بالحرف).
- Join Flow (`join_live_session` — الفرع الوحيد اللي اتلمس هو شرط
  `status == 'ended'`، وحتى هو نفس البنية بالظبط، بس بيفحص
  `recording_file` بدل `recording_url`).
- Live Session Lifecycle (`create_live_session`, `live_broadcast`,
  `end_live_session` — الثلاثة متلمسوش خالص).

### ما تم تنفيذه

**1) `groups/models.py` — `GroupLiveSession`:**
- اتشال `recording_url` (URLField).
- اتضاف بدلها:
  - `recording_file = FileField(upload_to='group_live_recordings/', null=True, blank=True)`
    — بنفس Storage Backend المستخدم فعليًا لملفات الكورسات
    (`courses.models.VideoFile.file`)، يعني `FileField` عادي فوق
    `DEFAULT_FILE_STORAGE`/`MEDIA_ROOT` المحلي المظبوط في `settings.py`
    من غير أي تخزين S3 خارجي جديد.
  - `recording_uploaded_at = DateTimeField(null=True, blank=True)`.
  - `recording_duration = DurationField(null=True, blank=True)` —
    الحقل موجود زي ما اتطلب بالضبط في نص الجزء، بس مفيش أي كود بيملاه
    تلقائيًا دلوقتي (محتاج مكتبة تحليل فيديو زي `ffprobe` مش موجودة في
    المشروع) — فاضل فاضي إلا لو حد ملاه يدويًا لاحقًا.
- Migration جديدة: `groups/migrations/0011_grouplivesession_manual_recording_fields.py`
  (`RemoveField` recording_url + 3× `AddField`)، بتعتمد على
  `('groups', '0010_grouplivesession')` — آخر migration معروفة في
  التطبيق حسب كل التوثيق المتاح (مفيش أي migration جديدة في Part
  23/24/25). ⚠️ **زي كل migration مكتوبة يدويًا في المشروع، لازم تتأكد
  إن `dependencies` صحيحة مقابل آخر migration فعلية على السيرفر قبل ما
  تشغل `migrate`.**

**2) `groups/live_provider.py`:**
- اتشالت دالتين بالكامل: `_egress_s3_configured()` و
  `_start_room_egress(room_name)`.
- `create_room()` رجعت لمسؤوليتها الأصلية بس: تنشئ الروم وترجع
  `room_identifier`. النداء اللي كان بيفعّل التسجيل التلقائي بعد نجاح
  الإنشاء اتشال.
- باقي الملف (`generate_access_token`, `end_room`, الثوابت زي
  `_TOKEN_TTL`) **متلمسش خالص**.

**3) `groups/webhooks.py`:**
- رجع لنفس حالته الأصلية من Part 23: `live_webhook` endpoint فاضي
  (`@csrf_exempt` + `@require_POST` + `HttpResponse(status=200)`)، من
  غير أي تحقق توقيع أو معالجة أي حدث. اتشال بالكامل منطق
  `WebhookReceiver`/`TokenVerifier`/معالجة `egress_ended`.
- قرار: الـ URL (`groups:live_webhook`) اتسابت موجودة في `urls.py` من
  غير حذف — مفيش أي ضرر من endpoint فاضي، وسهل تتحذف لاحقًا لو Ahmed
  عايز.

**4) `groups/views.py`:**
- view جديدة `upload_group_recording(request, session_id)` —
  `@instructor_required` + تحقق `group.teacher_id == request.user.id`
  (نفس نمط ownership المستخدم في `create_live_session`/`end_live_session`).
  الشروط: `session.status == 'ended'` (يمنع الرفع قبل انتهاء اللايف)،
  امتداد الملف من ضمن `mp4`/`webm`/`mov`، والحجم أقل من أو يساوي
  `settings.GROUP_LIVE_RECORDING_MAX_UPLOAD_MB`. عند النجاح: بيحفظ
  `recording_file` ويحدّث `recording_uploaded_at`.
- `group_recordings`: الفلترة بقت `.exclude(recording_file='')` بدل
  `.exclude(recording_url='')`. باقي منطق الصلاحية زي ما هو.
- `watch_group_recording`: الشرط بقى `not session.recording_file` بدل
  `not session.recording_url`. باقي المنطق زي ما هو.
- `join_live_session`: فرع `status == 'ended'` بس — بدل ما نتحقق من
  `recording_url` (كان بيتملى تلقائيًا من الويبهوك)، بنتحقق من
  `recording_file`. لو موجود، نفس التحويل لصفحة المشاهدة. لو لسه فاضي،
  الرسالة اتغيّرت من "التسجيل لسه بيتجهز عندنا" (كانت بتوحي بمعالجة
  تلقائية جارية) لـ "المدرس لسه ما رفعش التسجيل" (بتعكس الواقع الجديد
  بدقة).
- `group_detail`: إضافة context جديد `recent_ended_live_sessions` (آخر
  5 جلسات `status='ended'` للجروب، للمدرس صاحب الجروب بس) — مفيش أي
  تعديل على أي context أو منطق تاني موجود من قبل.
- **قرار معماري خاص بيّ (مش موجود صراحة في الطلب)**: الطلب الأصلي وصف
  "صفحة تفاصيل اللايف" بيها زرار "Upload Recording"/"Watch Recording"
  — لكن المشروع مفيهوش صفحة "تفاصيل جلسة لايف واحدة" منفصلة أصلاً
  (`live_broadcast` بتاعة المضيف بس ومتاحة وقت `status='live'` بس،
  و`watch_live_session` بتاعة الطالب بتتفرع حسب الحالة لكن مفيهاش
  زرار رفع). بدل ما أعمل صفحة تفاصيل جديدة (توسّع في نطاق الطلب)،
  حطيت الزرارين المطلوبين (Upload/Watch) في قسم جديد داخل
  `group_detail.html` نفسها (المدرس بس بيشوفه) — ده أبسط تطبيق ممكن
  لنفس المتطلب الوظيفي من غير ما أضيف صفحة/view زيادة عن اللي اتطلب.

**5) التمبلتس:**
- تمبلت جديدة `groups/templates/groups/upload_group_recording.html` —
  فورم رفع بسيط (drag & drop zone بنفس روح مكونات المنصة، من غير أي
  مكتبة CSS خارجية جديدة)، بنفس نظام "Obsidian Academy" حرفيًا.
- `groups/templates/groups/group_detail.html`: قسم جديد "لايفات محتاجة
  رفع تسجيل" (بعد رابط "مكتبة التسجيلات" مباشرة) — ظاهر للمدرس صاحب
  الجروب بس (`is_owner`)، بيعرض آخر الجلسات المنتهية مع زرار "ارفع
  التسجيل" (لو `recording_file` فاضي) أو "شاهد التسجيل" (لو موجود).
  الطالب مايشوفش القسم ده خالص — ولا أي زرار رفع في أي مكان تاني في
  التمبلت.
- `groups/templates/groups/group_recordings.html`: تعديل نصي بس (مفيش
  تغيير منطقي — الفلترة أصلاً بتتم في الـ view) — النص بقى "لما المدرس
  يرفع تسجيل اللايف بعد ما يخلص، هيظهر هنا" بدل "أي بث مباشر يتسجل
  تلقائيًا".
- `groups/templates/groups/watch_group_recording.html`: مصدر الفيديو
  (`<video src="...">`) ورابط التحميل الاحتياطي بقوا
  `{{ session.recording_file.url }}` بدل `{{ session.recording_url }}`.
  ضفت كمان سطر عرض `recording_uploaded_at` لو موجود (تحسين بسيط، مش
  مطلوب صراحة).

**6) `groups/urls.py`:**
- path جديد `live/<int:session_id>/recording/upload/` →
  `views.upload_group_recording` باسم `upload_group_recording`. باقي
  الملف **متلمسش خالص**.

**7) `Eduvia/settings.py`:**
- اتشالت الـ 6 إعدادات `LIVEKIT_EGRESS_S3_*` بالكامل (مبقتش مستخدمة).
- ضيف إعداد واحد جديد: `GROUP_LIVE_RECORDING_MAX_UPLOAD_MB` (نفس أسلوب
  `config()` المتبع في باقي الملف)، افتراضي 1024 ميجا (1 جيجا) —
  اخترته بنفسي لإن الطلب قال "حسب إعدادات المشروع" من غير رقم محدد.

### النتيجة

كل جلسة Live بتتحول لـ VOD بمجرد ما المدرس يرفع تسجيله يدويًا من صفحة
الجروب، بنفس صلاحيات الوصول القديمة (عضوية + اشتراك نشط)، وبدون أي
اعتماد على LiveKit Egress أو أي بنية تحتية تسجيل خارجية إطلاقًا.

### ⚠️ حاجات محتاجة انتباه/قرار من Ahmed

1. **الأهم**: لازم تشغيل `makemigrations --check --dry-run` فعليًا على
   السيرفر قبل `migrate`، للتأكد إن `dependencies` في
   `0011_grouplivesession_manual_recording_fields.py` (`('groups',
   '0010_grouplivesession')`) لسه صحيحة — نفس التحذير المتكرر من كل
   migration مكتوبة يدويًا في المشروع.
2. حد حجم الرفع (1 جيجا افتراضيًا، `GROUP_LIVE_RECORDING_MAX_UPLOAD_MB`)
   اخترته بنفسي — سهل تغييره كمتغير بيئة من غير أي تعديل كود.
3. `recording_duration` موجود كحقل بس مفيش أي كود بيملاه تلقائيًا — لو
   عايز مدة الفيديو تتحسب تلقائيًا وقت الرفع، محتاجين مكتبة زي
   `ffmpeg-python`/`ffprobe` مش موجودة في `requirements.txt` حاليًا،
   ده تحسين منفصل.
4. **قرار مني محتاج مراجعتك**: زرار "Upload Recording"/"Watch Recording"
   حطيته في `group_detail.html` (قسم جديد، مش صفحة منفصلة) لإن مفيش
   صفحة "تفاصيل جلسة لايف" منفصلة في المشروع أصلاً — راجع قسم "قرار
   معماري خاص بيّ" فوق لو حابب تصميم مختلف (زي صفحة تفاصيل مستقلة لكل
   جلسة).
5. فحص نوع الملف حاليًا بس على امتداد اسم الملف (mp4/webm/mov) — مفيش
   أي تحقق فعلي من محتوى الملف (زي مكتبة `python-magic`)، نفس مستوى
   التحقق البسيط المستخدم في باقي رفع الملفات بالمشروع.
6. `groups/webhooks.py::live_webhook` رجع فاضي (Part 23 الأصلي) —
   الـ URL لسه موجود في `urls.py` من غير حذف، سهل تتشال الاتنين مع
   بعض لو مش محتاجهم خالص.

## الحالة الحالية
آخر جزء منفذ: Part 26 — Manual Recording Upload + VOD Library (نسخة
معدّلة) — ✅ **اتأكد فعليًا بالكامل على سيرفر Ahmed**: Ahmed جرّب السيناريو
الكامل فعليًا (مش بس syntax check):
1. بدأ لايف، سابه شوية، دوس "إنهاء البث" — الجلسة اتقفلت وبقت `status='ended'`
   بنجاح.
2. من صفحة الجروب، قسم "لايفات محتاجة رفع تسجيل" ظهر زي المتوقع، دوس
   "ارفع التسجيل".
3. رفع فيديو تجربة (mp4 صغير) — اتحفظ فعليًا في `MEDIA_ROOT`
   (`/data/media/group_live_recordings/`)، و`recording_uploaded_at`
   اتسجل.
4. فتح "مكتبة التسجيلات" — التسجيل ظهر في القايمة واشتغل صح في مشغل
   الفيديو (`watch_group_recording.html`).

⚠️ **تصحيح لاحق اتلاقى أثناء الاختبار**: أول محاولة لـ
`makemigrations --check --dry-run` بعد تطبيق migration 0011 فشلت بخطأ
`admin.E035` — `groups/admin.py::GroupLiveSessionAdmin.readonly_fields`
كانت لسه بتشاور على `recording_url` (الحقل القديم اللي اتشال من
الموديل في نسخة Part 26 المعدّلة). اتصلح بتعديل سطر واحد بس: استبدال
`'recording_url'` بـ `'recording_file'` و`'recording_uploaded_at'` في
`readonly_fields` — باقي `groups/admin.py` (كل actions الدفع، الـ
badges، `GroupChatMessageAdmin`، إلخ) **متلمسش خالص**. الدرس هنا: أي
تعديل على حقول موديل لازم يترفق بمراجعة `admin.py` نفسه لو فيه
`readonly_fields`/`list_display` بتشاور على نفس الحقول — الموديل
والـ admin ملفين منفصلين ومحتاجين مراجعة مستقلة.

نظام Part 26 دلوقتي شغال بالكامل عن طريق رفع يدوي من المدرس (تفاصيل
كاملة تحت في قسم "Part 26 — Manual Recording Upload + VOD Library
(نسخة معدّلة)")، من غير أي اعتماد على LiveKit Egress أو أي بنية تحتية
تسجيل خارجية.

## قرارات معمارية اتاخدت (Part 27)

### مقارنة courses.models.Lesson مقابل groups.models.GroupLesson

قبل أي كود، فحصت `courses/models.py` و`courses/admin.py` الحقيقيين
(مش من التوثيق أو الذاكرة). المشروع فيه نظامين للفيديو في تطبيق
`courses`:

1. **النظام القديم** (`Video` + `VideoFile`): الفيديو الأساسي
   `Video.video_url` (`URLField`)، و`VideoFile.file` (`FileField`) هي
   مرفقات إضافية اختيارية، مش مصدر الفيديو الأساسي.
2. **نظام "المنهج الجديد"** (`Section` + `Lesson` — الأحدث، ومسجل بالكامل
   في `courses/admin.py` بـ `LessonInline` داخل `SectionAdmin` +
   `fieldsets` مخصصة، على عكس `Video` اللي مسجلة بشكل بسيط): الفيديو
   الأساسي كمان `Lesson.video_url` (`URLField`)، و`video_duration`
   (`FloatField`) بيتكتب يدويًا من المدرس ("Duration of the video in
   minutes (to be entered manually by the instructor)").

**الخلاصة المهمة**: **الفيديو الأساسي في تطبيق courses (في النظامين
القديم والجديد) مخزّن دايمًا كـ رابط خارجي (`URLField`)، مش كملف
مرفوع (`upload_to`)**. الـ `FileField` الوحيدة (`VideoFile.file`) هي
مرفق إضافي اختياري على النظام القديم بس، مش مسار الفيديو الأساسي في أي
مكان.

**القرار**: بنيت `GroupLesson` على أساس `courses.models.Lesson` (النظام
الأحدث/الفعلي)، بنفس أسلوب تخزين الفيديو بالظبط —
`video_url = URLField(max_length=500, blank=True, null=True)` +
`video_duration = FloatField(default=0)` بيتكتب يدويًا، **مش**
`FileField`. القرار ده مبني على الملف الحقيقي مباشرة، مش افتراض.

**فروق متعمدة عن `courses.models.Lesson`** (موثقة كمان كـ docstring
جوه الموديل نفسه في `groups/models.py`):
- **مفيش `lesson_type`** (video/text/article) — الجزء ده (27) مخصص
  بالتحديد لـ"الدروس المسجلة" (فيديو بس)، زي ما اتطلب صراحة في نص
  الجزء. لو Ahmed عايز دروس نصية/مقالات جوه الجروب لاحقًا، سهل نضيف
  الحقل ده بعدين بنفس فلسفة `Lesson.lesson_type`.
- **مفيش `is_preview`** — المفهوم المكافئ (معاينة مجانية) موجود بالفعل
  على مستوى تسجيلات اللايف (`workshops.LiveRecording.is_free_preview`
  من Part 18)، مش مطلوب صراحة هنا في نص الجزء.
- **مفيش صورة مصغرة (thumbnail)**: فحصت `courses/models.py` كامل —
  مفيش أي صورة على مستوى الدرس/الفيديو في أي من النظامين (القديم أو
  الجديد)، الصورة موجودة بس على مستوى الكورس ككل
  (`Course.image`/`image_file`). عبارة "الصور المصغرة" في نص الجزء
  الأصلي معندهاش نظير حقيقي في الكود على مستوى الدرس، فمفيش أي حقل
  thumbnail على `GroupLesson`.
- **`created_at` مضاف**: مش موجود في `courses.models.Lesson` خالص، لكن
  ضفته هنا (`auto_now_add=True`) بنفس نمط باقي موديلات `groups` كلها
  (كل موديل في التطبيق ده عنده `created_at`) — اختيار بسيط مني، مش نسخ
  حرفي.
- **`Meta.ordering`**: نسخت `['order']` من `Lesson.Meta.ordering`، وضفت
  `created_at` كـ tie-breaker ثاني (اختيار مني) عشان لو أكتر من درس
  بنفس قيمة `order` بالظبط (زي القيمة الافتراضية `0` قبل ما المدرس
  يرتبهم يدويًا)، الترتيب يفضل ثابت ومتوقع (الأقدم أول).

**`is_published` و`publish_at`**: زي ما اتطلب بالظبط في نص الجزء،
مُجهّزين لاستخدامهم في الجدولة التلقائية (Part 31) — مفيش أي منطق نشر
تلقائي بيستخدمهم فعليًا لسه في الجزء ده، هما بس حقول جاهزة
(`is_published` افتراضيًا `True`، `publish_at` اختياري).

### حقل `group` — نفس `related_name` المطلوب صراحة في نص الجزء

`group = ForeignKey(TeacherGroup, related_name='lessons', on_delete=CASCADE)`
— بالظبط زي ما اتطلب. اتأكدت إن `'lessons'` مش متعارض مع أي
`related_name` تاني موجود على `TeacherGroup` (الموجودين حاليًا:
`teacher_groups`, `subscriptions`, `proofs`, `group_memberships`,
`memberships`, `upgrades`, `upgrade_source`, `chat_messages`,
`group_live_sessions`, و`live_sessions` من `workshops.LiveSession`) —
مفيش تعارض.

### تسجيل الأدمن (بعد استلام groups/admin.py الحقيقي)

سجّلت `GroupLesson` (`GroupLessonAdmin`) في `groups/admin.py` بنفس نمط
باقي موديلات `groups`:
- `list_display`: العنوان، الجروب، الترتيب، حالة النشر، ميعاد النشر
  المجدول، مدة الفيديو، تاريخ الإنشاء.
- `list_filter`: `is_published` و`group__category`.
- `search_fields`: العنوان، الوصف، اسم الجروب، اسم المدرس.
- `list_editable = ('order', 'is_published')` — بنفس فلسفة
  `LiveRecordingAdmin.is_free_preview` من Part 18 (`list_editable`)،
  عشان الأدمن/المدرس (لو عنده صلاحية) يقدر يرتب الدروس أو ينشر/يخفي
  درس مباشرة من صفحة القايمة من غير ما يفتح كل سجل لوحده.
- action جماعي `toggle_publish` (بنفس فلسفة `toggle_free_preview` من
  Part 18) لتبديل حالة النشر لأكتر من درس مختار مرة واحدة.
- **باقي `groups/admin.py` متلمسش خالص** — التعديل كله: (1) إضافة
  `GroupLesson` لاستيراد الموديلات الموجود فوق، (2) قسم جديد
  `GroupLessonAdmin` في آخر الملف بعد `GroupLiveSessionAdmin`. مفيش أي
  تعديل على `PaymentProofAdmin`, `GroupSubscriptionAdmin`, أو أي
  action موجود من Part 9/10/21.

## سجل الأجزاء

### Part 27 — موديل GroupLesson لرفع الدروس المسجلة (بنفس منطق رفع الكورسات)
الحالة: **تم** (الموديل + الميجريشن + تسجيل الأدمن)
تفاصيل:
- قريت `courses/models.py` و`courses/admin.py` الحقيقيين كاملين قبل أي
  كود — تفاصيل المقارنة الكاملة فوق في "قرارات معمارية".
- ضفت موديل `GroupLesson` في `groups/models.py` (آخر موديل في الملف،
  بعد `GroupLiveSession` من Part 22/26) بالحقول: `group`, `title`,
  `description`, `video_url`, `video_duration`, `order`,
  `is_published`, `publish_at`, `created_at`. تفاصيل كل حقل وأسباب
  الفروق عن `courses.models.Lesson` فوق.
- عملت migration جديدة `groups/migrations/0012_grouplesson.py`
  (`CreateModel` بسيط)، بتعتمد على `('groups',
  '0011_grouplivesession_manual_recording_fields')` (آخر migration
  معروفة حسب كل التوثيق المتاح). ⚠️ نفس تحذير كل migration مكتوبة
  يدويًا في المشروع: تأكد من `makemigrations --check --dry-run` فعليًا
  على السيرفر قبل `migrate`.
- سجّلت الموديل في `groups/admin.py` (`GroupLessonAdmin`) — تفاصيل
  كاملة فوق في "تسجيل الأدمن".
- اتفحص syntax الملفات التلاتة (`python -m py_compile`) — عدّوا من
  غير أخطاء.
- **مفيش أي تعديل على أي view أو template في الجزء ده** — زي ما اتطلب
  بالظبط ("دلوقتي بس اعمل الموديل").
- ⚠️ حاجات محتاجة قرار/انتباه من Ahmed:
  1. أسلوب تخزين الفيديو (`video_url` خارجي، مش رفع ملف) اتاخد بناءً
     على الكود الحقيقي مباشرة — لو حابب نظام رفع ملفات فعلي بدل الروابط
     الخارجية لدروس الجروبات (مختلف عن باقي الكورسات)، ده قرار مختلف
     محتاج مراجعة قبل Part 28 (واجهات الرفع/العرض)، لإن الفورم هيختلف
     شكل حقل الفيديو (رابط نصي مقابل `<input type="file">`).
  2. مفيش `lesson_type`/`is_preview`/thumbnail — أسباب الاستبعاد
     موثقة فوق، سهل تتضاف لاحقًا لو الأولوية اتغيرت.
  3. `list_editable`/action الجماعي في الأدمن (`toggle_publish`)
     اخترتهم بنفسي زيادة عن المطلوب صراحة في نص الجزء (اللي طلب بس
     "سجّل الموديل بنفس نمط باقي موديلات الجروبات") — استلهمتهم من نفس
     نمط `LiveRecordingAdmin` في Part 18. سهل تشيلهم لو مش لازمين.

### ✅ تأكيد فعلي على سيرفر Ahmed

- `python manage.py makemigrations --check --dry-run` رجع بس الملاحظة
  التجميلية المعروفة من Part 22 (توحيد نوع حقل `id` لـ `BigAutoField` —
  دلوقتي `grouplesson` انضاف لنفس القائمة جنب `groupchatmessage` و
  `grouplivesession`، بنفس السبب بالظبط ومفيش أي فعل مطلوب).
- `python manage.py migrate groups` قال "No migrations to apply" —
  يعني `0012_grouplesson` اتطبقت بنجاح والجدول موجود فعليًا في
  الداتابيز.
- `python manage.py check` رجع "System check identified no issues".

**Part 27 شغال فعليًا 100% على السيرفر دلوقتي — الموديل + الأدمن +
الميجريشن، جاهز لـ Part 28 (واجهات رفع/عرض الدروس).**

## قرارات معمارية اتاخدت (Part 28)

- **قرار تنظيمي جديد — تقسيم groups/views.py لملفات حسب الموضوع**:
  `groups/views.py` بقى فيه أكتر من 1300 سطر بعد Part 26، وضيف views
  الدروس المسجلة عليه كان هيخليه أكبر وأصعب في المراجعة (وهيستهلك جزء
  كبير من الـ context في أي جلسة تانية تحتاج تفتحه). عشان كده، الـ views
  الجديدة بتاعة الجزء ده اتحطت في ملف منفصل جديد **`groups/views_lessons.py`**
  بدل ما تتضاف جوه `views.py` نفسه. القرار ده تنظيمي بحت — مفيش أي تغيير
  في السلوك أو أسماء الـ URLs بسببه، والـ helpers المشتركة
  (`instructor_required`, `_get_owned_group_or_403`,
  `_get_group_and_membership_or_403`) اتستوردت من `groups/views.py` بدل
  ما تتكرر. لو Ahmed حابب، نفس الأسلوب (ملف `views_<موضوع>.py` منفصل)
  هيتبع في الأجزاء الجاية اللي فيها views جديدة (الواجبات Part 34،
  المهام اليومية Part 35، إلخ) بدل ما نضيف على `views.py` الأصلي.
- **`groups/models.py` متلمسش خالص** — موديل `GroupLesson` كان جاهز
  بالكامل من Part 27 (بحقوله `is_published`/`publish_at`/`order` جاهزة)،
  فمفيش أي migration جديدة أو تعديل على الموديل مطلوب في الجزء ده.
- **مفيش Django Form/ModelForm جديد لفورم رفع الدرس** — اتبع نفس أسلوب
  `create_live_session` (Part 24) بالظبط: قراءة `request.POST` يدويًا
  + validation بسيط، بدل ما نضيف `forms.py` كلاس جديد لأربع/خمس حقول
  بسيطة. القرار ده للاتساق مع أقرب view مشابهة فعليًا في المشروع.
- **فورم الرفع بيدعم "انشر دلوقتي" أو "جدولة لوقت لاحق"** — الطلب
  الأصلي لـ Part 28 ذكر بس (عنوان، وصف، فيديو، ترتيب)، لكن لاحظنا إن
  متطلب "الطالب يشوف الدروس الغير منشورة (المجدولة) مع علامة 'هتنزل
  يوم كذا'" بيفترض ضمنيًا إن فيه طريقة فعلية تنتج دروس `is_published=False`
  مع `publish_at` محدد. عشان كده ضفنا اختيار نشر (نفس نمط `start_choice`
  في `create_live_session`) بدل ما نسيب الحقلين (`is_published`,
  `publish_at` من Part 27) من غير أي واجهة تملاهم. لو Ahmed شايف إن ده
  خارج نطاق الجزء ده وعايز يأجله لحد Part 31 (الجدولة التلقائية)، سهل
  نشيل اختيار الجدولة من الفورم ونسيب `is_published=True` ثابتة دلوقتي.
- **`watch_group_lesson` بياخد `lesson_id` بس في الـ URL** (من غير
  `group_id`) — نفس فلسفة `watch_group_recording`/`join_live_session`
  من Part 25/26: الـ view بتستنتج الجروب من الدرس نفسه مباشرة، فمفيش
  داعي لتكرار `group_id` في المسار.
- **حماية أمان استباقية**: الطالب العضو (مش المدرس) مايقدرش يفتح
  `watch_group_lesson` لدرس `is_published=False` حتى لو حصل على الـ
  `lesson_id` بشكل مباشر (بيترجع `Http404`) — الفحص ده جوه الـ view
  نفسها مش بس إخفاء الدرس من `group_lessons_list`. ده تنفيذ مبكر لجزء
  من متطلب Part 31 ("تأكد إن الطالب مش قادر يفتح رابط الدرس مباشرة قبل
  موعد النشر")، واتضاف دلوقتي بدل ما يتأجل لإنه سطرين بس ومنطقي يبقى
  موجود من أول لحظة يبقى فيها دروس غير منشورة أصلاً.
- **نفس فحص الصلاحية المعتاد بالحرف**: `group_lessons_list` و
  `watch_group_lesson` بيستخدموا نفس نمط `_get_group_and_membership_or_403`
  + `is_group_content_accessible` + `GROUP_FROZEN_MESSAGE` المستخدم في
  `group_recordings`/`watch_group_recording` (Part 26) — الطالب العضو
  (مش المدرس) لازم الجروب يكون "نشط" وإلا بيترجع لصفحة "جروباتي"
  برسالة التجميد المعتادة؛ المدرس صاحب الجروب يقدر يشوف/يرفع دروس حتى
  لو الجروب متجمد (نفس استثناء باقي الصفحات).
- **مشغل الفيديو منسوخ بالحرف من `courses/lesson_view.html`**: نفس
  `.video-shell`/`.video-empty-state` CSS ونفس منطق دعم YouTube/Vimeo/
  Google Drive/رابط مباشر (`<video>` fallback) — بالظبط زي ما اتطلب في
  نص الجزء ("استخدم نفس الكومبوننت/التمبلت لو موجود بدل ما تعيد بناءه").
- **قايمة الدروس (`group_lessons_list`)**: المدرس صاحب الجروب بيشوف كل
  الدروس (منشورة + مجدولة) مع badge واضح لكل حالة، والطالب العضو بيشوف
  الدروس المنشورة (`is_published=True`) بس — الترتيب بـ `order` ثم
  `created_at` (نفس `Meta.ordering` على الموديل من Part 27).
- **رابط "الدروس المسجلة" في `group_detail.html`**: زرار بسيط (نفس نمط
  زرار "مكتبة التسجيلات" من Part 26 بالظبط — `.sess-btn.sess-btn-ghost`
  بعرض كامل) بيودّي لـ `group_lessons_list`. القرار كان نسيب `group_detail`
  view نفسها من غير أي تعديل Python خالص (ولا حتى إضافة context جديد
  للعدد) — الرابط بسيط زي رابط مكتبة التسجيلات تمامًا، من غير عداد،
  فمفيش داعي لأي استعلام إضافي في `group_detail()`.

## سجل الأجزاء (تابع)

### Part 28 (المرحلة الثانية) — واجهات رفع/عرض الدروس المسجلة داخل الجروب
الحالة: تم
تفاصيل:
- أنشأت ملف جديد **`groups/views_lessons.py`** (منفصل عن `groups/views.py`
  — تفاصيل القرار التنظيمي فوق) فيه ثلاث views:
  - `upload_group_lesson(request, group_id)` — `@instructor_required`
    + `_get_owned_group_or_403`. GET بيعرض فورم الرفع، POST بيتحقق من
    الحقول (عنوان + رابط فيديو إجباريين، مدة/ترتيب أرقام اختيارية) وبيبني
    `is_published`/`publish_at` حسب اختيار "دلوقتي"/"جدولة"، وبينشئ
    `GroupLesson` ويرجّع لـ `group_lessons_list`.
  - `group_lessons_list(request, group_id)` — `@login_required` +
    `_get_group_and_membership_or_403` + فحص تجميد الجروب للطالب. المدرس
    بيشوف كل الدروس، الطالب بيشوف المنشورة بس.
  - `watch_group_lesson(request, lesson_id)` — `@login_required` +
    نفس فحص الصلاحية/التجميد، بالإضافة لحماية `is_published` ضد الوصول
    المباشر بالـ id (تفاصيل فوق).
- عدّلت `groups/urls.py`: ضفت `from . import views_lessons` وثلاث
  مسارات جديدة (`<int:group_id>/lessons/upload/` →
  `upload_group_lesson`, `<int:group_id>/lessons/` →
  `group_lessons_list`, `lessons/<int:lesson_id>/watch/` →
  `watch_group_lesson`)، محطوطين قبل الـ pattern العام
  `<int:group_id>/` في آخر الملف (زي كل الأجزاء اللي فاتت).
- أنشأت 3 تمبلتس جديدة بنفس نظام "Obsidian Academy" (نفس CSS variables/
  topbar/footer من `group_detail.html`):
  - `groups/templates/groups/upload_group_lesson.html`: فورم الرفع
    (عنوان، وصف، رابط فيديو، مدة، ترتيب) + اختيار نشر فوري/مجدول (نفس
    مكوّن radio-card المستخدم في `create_live_session.html` لاختيار
    الـ mode)، مع حقل ميعاد النشر بيظهر/يختفي بجافاسكريبت بسيط حسب
    الاختيار.
  - `groups/templates/groups/group_lessons_list.html`: قايمة الدروس
    (كارت لكل درس، badge منشور/مجدول للمدرس، رابط "رفع درس جديد" للمدرس
    بس)، وempty state لو مفيش دروس.
  - `groups/templates/groups/watch_group_lesson.html`: صفحة تشغيل
    الدرس — `.video-shell` منسوخة بالحرف من `courses/lesson_view.html`
    (نفس دعم YouTube/Vimeo/Google Drive/رابط مباشر)، مع بطاقة معلومات
    الدرس (عنوان، وصف، مدة) وbadge تنبيه لو المدرس بيشوف درس لسه مش
    منشور.
- عدّلت `groups/templates/groups/group_detail.html`: ضفت رابط بسيط
  "الدروس المسجلة" (نفس نمط زرار "مكتبة التسجيلات" من Part 26 بالظبط)
  تحت قسم البث المباشر، ظاهر دايمًا (للمدرس والطالب العضو). **مفيش أي
  تعديل على `group_detail()` (Python) خالص** — الرابط بسيط زي رابط
  مكتبة التسجيلات، من غير عداد أو استعلام إضافي.
- **مفيش أي migration جديدة** — موديل `GroupLesson` جاهز بالكامل من
  Part 27.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مدرس يفتح صفحة جروبه → يضغط "الدروس المسجلة" → يضغط "رفع درس جديد" →
  يملأ الفورم ويختار "انشر دلوقتي" → الدرس يظهر في القايمة بـ badge
  "منشور" → طالب عضو يفتح نفس القايمة → يشوف نفس الدرس ويقدر يشغّله.
  نفس المدرس يرفع درس تاني بـ "جدولة" لميعاد في المستقبل → الدرس يظهر
  للمدرس بس بـ badge "مجدول" وعلامة "هتنزل يوم كذا" → الطالب مايشوفهوش
  في القايمة، ولو حاول يفتح رابط `watch_group_lesson` بالـ id مباشرة
  → `Http404`.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. اختيار "انشر دلوقتي/جدولة" في فورم الرفع مش مطلوب صراحة في نص
     Part 28 (موضح فوق في "قرارات معمارية") — لو حابب تأجيله لحد
     Part 31، سهل نشيله ونخلي كل درس `is_published=True` تلقائي دلوقتي.
  2. مفيش أي حد أقصى لحجم/نوع رابط الفيديو بيتفحص في الـ backend (زي
     التحقق إن الرابط فعلاً بيرجع فيديو صالح) — نفس فلسفة `video_url`
     في `courses.Lesson` بالظبط (ثقة في المدرس إنه حط رابط صحيح).
  3. القرار التنظيمي بتاع تقسيم `views.py` لملفات حسب الموضوع
     (`views_lessons.py`) قرار مفتوح للنقاش — لو Ahmed مفضّل يفضل كل
     حاجة في ملف واحد، سهل نرجع نضم المحتوى، بس التوصية إن الانفصال
     أفضل مع زيادة حجم المشروع.

## قرارات معمارية اتاخدت (Part 29)

- **مكان الحقل: `chat_mode` على `TeacherGroup` نفسها، مش على `GroupChatMessage`**:
  وضع الشات (مفتوح/إذاعة) هو إعداد بيخص الجروب ككل في لحظة معينة، مش
  خاصية لكل رسالة على حدة — فمكانه الطبيعي هو الموديل اللي بيمثل الجروب
  نفسه، بنفس منطق `is_active`/`current_plan` الموجودين بالفعل على
  `TeacherGroup`. الحقل: `chat_mode = CharField(choices=[('open','open'),
  ('broadcast_only','broadcast_only')], default='open', max_length=20)`
  — بالظبط زي ما اتطلب، مع `max_length=20` (نفس القيمة المستخدمة لحقول
  choices مشابهة تانية في المشروع زي `GroupSubscription.status`).
- **`toggle_chat_mode` كـ view مستقلة (مش action تاني جوه `group_detail`)**:
  البرومبت الأصلي طلب صراحة "view بسيط (`toggle_chat_mode`)"، فبدل ما
  أضيفه كـ action جديد في نظام الـ POST dispatch الموجود جوه
  `group_detail` (زي `attach_session`/`detach_session`/`send_message`
  من Part 13/14)، عملته view مستقلة بمسار URL خاص بيها
  (`<int:group_id>/chat/toggle-mode/`)، بنفس نمط `end_live_session`
  بالظبط (`@instructor_required` + `@require_POST` + استخدام
  `_get_owned_group_or_403` الموجودة بالفعل من Part 24 — مفيش تكرار
  لمنطق فحص الـ ownership). القرار ده اتباع حرفي لصياغة الطلب، وبرضه
  أنضف تقنيًا: تبديل حالة (toggle) عملية مستقلة منطقيًا عن إرسال رسالة،
  فمسار URL خاص بيها أوضح من حقل `action` إضافي وسط نفس الفورم.
- **الفحص الحقيقي (server-side) في `send_message` نفسها**: البرومبت طلب
  "امنع الإرسال" لو `chat_mode == 'broadcast_only'` والمرسل مش المدرس.
  الشرط ده اتضاف كأول حاجة جوه `action == 'send_message'` (قبل أي قراءة
  لمحتوى الرسالة)، وبيرجع نفس نص الرسالة المطلوب بالظبط: "المدرس قافل
  الشات دلوقتي، بس هو اللي يقدر يبعت". الفحص ده هو خط الدفاع **الحقيقي**
  — التمبلت بيخفي حقل الكتابة كليًا للطلاب (مش بس `disabled`)، لكن لو
  حد بعت POST مباشر متجاوز الواجهة (من غير المرور بالفورم)، برضه
  هيترفض هنا. المدرس صاحب الجروب (`is_owner`) مستثنى دايمًا من الفحص ده
  — يقدر يبعت رسائل في الوضعين.
- **إخفاء حقل الكتابة نهائيًا (مش تعطيل) للطلاب في وضع الإذاعة**: زي ما
  اتطلب بالظبط ("اخفي حقل كتابة الرسالة نهائيًا... مش بس تعطله"). في
  التمبلت، فورم الإرسال بالكامل (`<form class="chat-form">`) اتلف بشرط
  `{% if is_owner or group.chat_mode != 'broadcast_only' %}` — يعني لو
  طالب (مش مالك) والجروب `broadcast_only`، الفورم مش موجود خالص في الـ
  HTML المُرجع (مش `hidden`/`disabled` عن طريق CSS/JS)، فمفيش أي طريقة
  للطالب يبعت POST من نفس الصفحة أصلاً (والفحص في الـ view طبقة حماية
  إضافية لو حد جرب يبعت الطلب يدويًا برضه).
- **رسالة توضيحية واضحة (`.chat-mode-banner`) فوق صندوق الشات مباشرة**:
  بتظهر لكل الأعضاء (مالك وطالب) لو `chat_mode == 'broadcast_only'`،
  بنص مختلف شوية حسب الدور (للمدرس: "إنت بس اللي هتقدر تبعت"، للطالب:
  "المدرس قافل الشات..."). ده تنفيذ لعبارة "مع رسالة واضحة توضح إن
  الشات في وضع الإذاعة" من نص الطلب.
- **زرار التبديل (`.chat-mode-toggle-btn`) ظاهر للمدرس بس**، في هيدر
  قسم الشات نفسه (`.chat-section-header`، فلكس بين عنوان القسم والزرار).
  الزرار فورم `POST` بسيط بيودّي لـ `toggle_chat_mode` مباشرة (مفيش
  JS/AJAX — ريدايركت عادي زي باقي أفعال الصفحة دي، Post/Redirect/Get).
  شكله بيتغيّر حسب الحالة الحالية (لون gold + أيقونة قفل لو `broadcast_only`،
  رمادي عادي + أيقونة قفل مفتوح لو `open`) عشان المدرس يعرف الحالة
  الحالية بنظرة واحدة قبل ما يضغط.
- **مفيش أي migration إضافية غير الحقل نفسه**: التعديل كله `AddField`
  بسيط (`groups/migrations/0013_teachergroup_chat_mode.py`)، بتعتمد على
  `('groups', '0012_grouplesson')` (آخر migration معروفة حسب كل
  التوثيق المتاح — Part 27). ⚠️ نفس تحذير كل migration مكتوبة يدويًا في
  المشروع: تأكد من `makemigrations --check --dry-run` فعليًا على
  السيرفر قبل `migrate`، لو فيه migration أحدث مش موثقة هنا.
- **مفيش أي تعديل على `groups/models.py` غير حقل `chat_mode`**: كل
  الموديلات التانية (`GroupChatMessage`, `GroupLiveSession`, `GroupLesson`,
  إلخ) فضلت زي ما هي 100%.
- **مفيش أي تعديل على `groups/forms.py`**: الحقل ده مبيتعرضش في أي
  ModelForm — التبديل بيتم بالكامل عن طريق زرار POST بسيط (نفس نمط
  `attach_session`/`detach_session` قبل كده)، مفيش فورم مخصص له.

## سجل الأجزاء (تابع)

### Part 29 (المرحلة الثانية) — وضع "الإذاعة" في الشات — المدرس بس يتكلم
الحالة: تم
تفاصيل:
- قريت منطق `GroupChatMessage` والـ `group_detail` view بتاعته (Part 14)
  كامل قبل أي كود، بالإضافة لـ `_get_owned_group_or_403` وباقي views
  البث المباشر (Part 24) عشان أتبع نفس نمط الـ ownership check والـ
  POST-only views الموجود بالفعل.
- ضفت حقل `chat_mode` على `TeacherGroup` في `groups/models.py`
  (`CharField`, choices `open`/`broadcast_only`, `default='open'`,
  `max_length=20`) — تفاصيل القرار فوق في "قرارات معمارية". باقي
  الموديل ومنطقه (`__str__`, `current_students_count`, `seats_available`،
  `unique_together`) **متلمسش خالص**.
- عملت migration جديدة `groups/migrations/0013_teachergroup_chat_mode.py`
  (`AddField` بسيط)، بتعتمد على `('groups', '0012_grouplesson')`.
- عدّلت `groups/views.py`:
  - view جديدة `toggle_chat_mode(request, group_id)`
    (`@instructor_required` + `@require_POST`) — بتستخدم
    `_get_owned_group_or_403` الموجودة بالفعل من Part 24 (403 لو مش
    المدرس صاحب الجروب)، بتبدّل `chat_mode` بين القيمتين، وترجّع
    المستخدم لـ `group_detail` برسالة نجاح توضح الحالة الجديدة.
  - `group_detail`: شرط جديد في أول `action == 'send_message'` — لو
    `group.chat_mode == 'broadcast_only'` و`not is_owner`، يترفض الإرسال
    برسالة "المدرس قافل الشات دلوقتي، بس هو اللي يقدر يبعت رسائل." من
    غير ما ينشئ أي `GroupChatMessage`. باقي منطق `send_message`
    (`strip()`، فحص الفراغ، إلخ) **متلمسش خالص**، وباقي الـ view
    (attach/detach_session، عرض الجلسات، السياق، إلخ) **متلمسش خالص**.
  - **باقي الملف (كل الـ views من Part 7 لحد Part 28) متلمسش خالص.**
- عدّلت `groups/urls.py`: ضفت مسار واحد جديد
  (`<int:group_id>/chat/toggle-mode/` → `toggle_chat_mode`، اسمه
  `toggle_chat_mode`) — قبل الـ pattern العام `<int:group_id>/` في آخر
  الملف (نفس ترتيب باقي الملف). باقي الملف **متلمسش خالص**.
- عدّلت `groups/templates/groups/group_detail.html`:
  - هيدر قسم الشات (`.chat-section-header`) بقى فيه زرار التبديل
    (`.chat-mode-toggle-btn`) ظاهر للمدرس بس، فورم POST بسيط لـ
    `toggle_chat_mode`.
  - بانر تنبيه (`.chat-mode-banner`) بيظهر لكل الأعضاء لو الشات في وضع
    الإذاعة، بنص مختلف حسب الدور (مدرس/طالب).
  - فورم الإرسال (`.chat-form`) اتلف بشرط `{% if is_owner or
    group.chat_mode != 'broadcast_only' %}` — مش موجود خالص في الـ HTML
    للطالب لو الشات مقفول (مش `disabled` بس)، تفاصيل فوق في "قرارات
    معمارية".
  - CSS جديد بس (`.chat-section-header`, `.chat-mode-toggle-btn`,
    `.chat-mode-toggle-btn.is-broadcast`, `.chat-mode-banner`) — بنفس
    نظام "Obsidian Academy" ونفس CSS variables الموجودة، من غير أي
    مكتبة خارجية جديدة. باقي التمبلت (أقسام اللايف، الدروس، إدارة
    الجلسات، إلخ) **متلمسش خالص**.
- عدّلت `groups/admin.py`: ضفت `chat_mode` في `list_display` و
  `list_filter` بتاعة `TeacherGroupAdmin` (زيادة عن المطلوب صراحة في
  نص الجزء، بس بنفس نمط باقي الحقول البسيطة على نفس الموديل — سهل
  تتشال لو مش لازمة). باقي `groups/admin.py` **متلمسش خالص**.
- اتفحص syntax كل الملفات المعدّلة (`python -m py_compile` على
  `models.py`/`views.py`/`urls.py`/`admin.py`/الـ migration) — عدّت كلها
  من غير أخطاء. اتفحص توازن `{% if/for %}` ↔ `{% endif/endfor %}` في
  `group_detail.html` (33 if/endif، 8 for/endfor) — متطابقين.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مدرس يفتح صفحة جروبه → يدوس زرار "الشات مفتوح (اضغط للقفل)" → الشات
  بقى `broadcast_only` → طالب عضو يفتح نفس الصفحة → يشوف بانر "المدرس
  قافل الشات..." من غير أي حقل كتابة خالص → لو حاول يبعت POST مباشر
  (`action=send_message`) بره الواجهة → بيترفض برسالة واضحة من غير ما
  تتسجل رسالة. المدرس نفسه لسه يقدر يبعت رسائل عادي في نفس الوضع. المدرس
  يدوس الزرار تاني → الشات يرجع `open` → حقل الكتابة يرجع يظهر للطالب.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. **الأهم**: migration الجديدة (`0013_teachergroup_chat_mode.py`)
     بتفترض إن `0012_grouplesson` (Part 27) هي آخر migration في تطبيق
     `groups` — لازم تتأكد بـ `makemigrations --check --dry-run` فعليًا
     على السيرفر قبل `migrate` لو فيه أي migration أحدث مش موثقة في
     التاريخ اللي وصلني.
  2. مفيش أي إشعار/تنبيه (زي نظام Part 16) بيتبعت للطلاب لما المدرس
     يقفل/يفتح الشات — البرومبت الأصلي ماطلبش ده صراحة (بس رسالة واضحة
     في الصفحة نفسها)، فسبته من غير إشعار خارجي. لو Ahmed عايز إشعار،
     سهل نضيفه بعدين.
  3. الزرار (`toggle_chat_mode`) بيتنفذ فورًا من غير أي تأكيد إضافي
     (زي مودال "متأكد؟") — نفس مستوى البساطة المستخدم في
     `attach_session`/`detach_session` من Part 13. لو عايز تأكيد قبل
     القفل (خصوصًا لو فيه طلاب بيكتبوا وقتها)، ده تحسين UX منفصل بسيط
     (confirm() في الـ JS مثلاً).

### ✅ تأكيد فعلي على سيرفر Ahmed
- `python manage.py makemigrations --check --dry-run` رجع بس نفس الملاحظة
  التجميلية المعروفة من Part 22/27 (توحيد نوع حقل `id` لـ `BigAutoField` —
  اقتراح migration `0014_alter_groupchatmessage_id_alter_grouplesson_id_and_more`
  يشمل دلوقتي `teachergroup` ضمنيًا برضه بسبب الحقل الجديد، لكن ده تعارض
  نوع بيانات تجميلي بحت مش نتيجة مباشرة لـ chat_mode ومش لازم يتطبق
  دلوقتي — نفس السبب الموثق من قبل، مفيش أي فعل مطلوب).
- `python manage.py migrate groups` طبّق `groups.0013_teachergroup_chat_mode`
  بنجاح ("OK").
- `python manage.py check` رجع "System check identified no issues".
- اختبار يدوي فعلي على المتصفح: تبديل وضع الشات، اختفاء حقل الكتابة
  للطالب في وضع الإذاعة، منع الإرسال، ورجوع الشات لوضعه المفتوح — كله
  اتأكد شغال بنجاح.

**Part 29 شغال فعليًا 100% على السيرفر دلوقتي.**

## قرارات معمارية اتاخدت (Part 30)

### 1) الملفات اللي اشتغلت عليها فعليًا (النسخ الحقيقية، مش من التوثيق)

اشتغلت مباشرة على النسخ الحقيقية اللي بعتها Ahmed في نفس الجلسة دي:
`groups/models.py`، `groups/views.py`، `groups/admin.py`،
`groups/templates/groups/group_detail.html`، و
`groups/migrations/0013_teachergroup_chat_mode.py` (بس كمرجع لآخر
migration موجودة، اتعمل عليه دلوقتي `0014` تحته — الملف نفسه
**متلمسش خالص**). مفيش أي إعادة بناء من التوثيق.

### 2) `content` بقى `blank=True` + `message_type` بدل ما تتحط رسالة "نص فاضي" لكل مرفق

زي ما اتطلب بالظبط، `GroupChatMessage.content` بقى `blank=True` —
رسالة صورة أو ملف ممكن تتبعت من غير أي نص مصاحب خالص (زي أي شات
عادي: تبعت صورة من غير كلام). الحقل `message_type`
(`text`/`image`/`file`, `default='text'`) هو اللي بيحدد إزاي التمبلت
والأدمن يتعاملوا مع الرسالة، بدل ما نحاول نستنتج النوع من وجود/عدم
وجود المرفقات في كل مكان بيتعرض فيه.

**قرار: مفيش `Model.clean()`/`full_clean()`** — التحقق الفعلي إن
الرسالة لازم يكون ليها محتوى حقيقي (نص، أو صورة، أو ملف — مش الفاضي
تمامًا) بيتم بالكامل في `groups/views.py::group_detail` (نفس فلسفة كل
الفورمات التانية في المشروع اللي بتتحقق يدويًا في الـ view، مش عن
طريق `Model.clean()`)، لإن الإنشاء دايمًا عن طريق `.objects.create()`
بعد تحقق كامل، مش عن طريق `ModelForm`.

### 3) صورة وملف — مش الاتنين مع بعض في نفس الرسالة

قرار تبسيط مقصود (مفيش تحديد صريح في الطلب لدعم أكتر من مرفق واحد في
نفس الرسالة): لو المستخدم بعت صورة وملف مع بعض في نفس الـ POST،
`send_message` بترفض الطلب كله برسالة واضحة ("ابعت صورة أو ملف في
الرسالة، مش الاثنين مع بعض") بدل ما تختار واحد عشوائيًا أو تنشئ رسالتين.
في الفرونت-إند، JS بسيط بيمسح اختيار الحقل التاني تلقائيًا لو المستخدم
اختار صورة بعد ما كان مختار ملف (أو العكس) — تحسين UX بس، الفحص
الحقيقي (server-side) هو اللي بيمنع التكرار فعليًا لو حد تجاوز الواجهة.

### 4) التحقق من النوع/الحجم — ثوابت في `views.py`، مش `settings.py`

زي `_ALLOWED_RECORDING_EXTENSIONS` من Part 26 بالظبط (نفس مستوى
التحقق: امتداد اسم الملف بس، مفيش مكتبة فحص محتوى فعلي زي
`python-magic` في المشروع)، ضفت 4 ثوابت جديدة في `groups/views.py`:
- `_ALLOWED_CHAT_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}`
- `_ALLOWED_CHAT_FILE_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar'}`
  (قائمة صيغ آمنة ومنتشرة، بتستبعد صراحة أي صيغة تنفيذية زي `exe`،
  `sh`، `bat`، `apk`، `msi`، إلخ — زي ما اتطلب بالظبط "امنع أنواع
  خطيرة زي exe").
- `_CHAT_IMAGE_MAX_BYTES = 5 * 1024 * 1024` (5 ميجا)
- `_CHAT_FILE_MAX_BYTES = 15 * 1024 * 1024` (15 ميجا)

**القرار (ثوابت في الكود مش إعداد في `settings.py`)**: بعكس Part 26
اللي طلب صراحة "حسب إعدادات المشروع" (فاتحطت `GROUP_LIVE_RECORDING_MAX_UPLOAD_MB`
في `settings.py`)، نص طلب Part 30 مقالش صراحة "ضيف إعداد في settings"
— قال بس "اعرض حد أقصى معقول للحجم". فاخترت الاتساق مع
`_ALLOWED_RECORDING_EXTENSIONS` (ثابت في `views.py` نفسه) بدل ما أضيف
إعداد جديد في `settings.py` من غير طلب صريح، خصوصًا إني معنديش الملف
ده في الجلسة دي أصلاً. القيم (5 ميجا للصور، 15 ميجا للملفات) اخترتها
بنفسي — سهل تتحول لـ `config()` في `settings.py` لاحقًا لو Ahmed عايز
يتحكم فيهم من غير ما يلمس الكود (زي نمط Part 26 بالظبط).

### 5) منطق `send_message` — نفس هيكل الفحص، بس بيتفرّع حسب نوع المرفق

عدّلت `action == 'send_message'` جوه `group_detail()`:
1. **فحص `chat_mode == 'broadcast_only'` فضل أول حاجة** (قبل أي قراءة
   لـ content أو الملفات) — نفس ترتيب Part 29 بالحرف، عشان أي POST
   (نص أو مرفق) من طالب في وضع الإذاعة يترفض فورًا من غير ما نلمس
   الملفات المرفوعة خالص.
2. لو فيه صورة وملف مع بعض → رفض (تفاصيل فوق).
3. لو فيه صورة بس → فحص الامتداد + الحجم → `GroupChatMessage.objects.create(...,
   message_type='image', attachment_image=image_file)`.
4. لو فيه ملف بس → نفس الشيء بـ `message_type='file'`.
5. لو مفيش أي مرفق → نفس سلوك Part 14 الأصلي بالحرف (نص أو رسالة خطأ
   "اكتب رسالة أو ارفق صورة/ملف قبل الإرسال" — النص اتغيّر شوية عن
   الأصلي "اكتب رسالة قبل الإرسال" عشان يعكس إن فيه خيار تاني دلوقتي).

كل مسار بيرجع `redirect` فورًا بعد الحفظ/الرفض (نفس نمط Post/Redirect/Get
المستخدم في كل حتة تانية في الملف) — مفيش أي منطق مشترك بعد الـ
`if`/`elif` سلسلة عشان يفضل واضح ومباشر.

### 6) التمبلت — فورم `multipart/form-data` + عرض المرفقات جوه الفقاعة

- فورم الإرسال بقى `enctype="multipart/form-data"` (لازم لأي رفع
  ملفات — أول فورم شات في المشروع بيرفع ملف، بنفس ملاحظة Part 8 لما
  `submit_payment_proof.html` كان أول فورم رفع صورة في المشروع).
- `.chat-form` بقى container عمودي (`flex-direction: column`) فيه
  صفين: `.chat-attach-row` (زرارين "صورة"/"ملف" كـ `<label>` مربوطين
  بـ `<input type="file" hidden>`، زي أي زرار رفع ملف مخفي عادي) و
  `.chat-form-row` (التكستاريا + زرار الإرسال، هو القديم بعينه بس
  اتنقل جوه container جديد).
- التكستاريا بطلت `required` (كانت `required` في Part 14 لإن الرسالة
  كانت لازم نص دايمًا) — دلوقتي اختياري لإن ممكن الرسالة تبقى صورة/ملف
  بس من غير أي نص.
- عرض الفقاعة: `msg.content` بيتعرض بس لو موجود فعليًا (`{% if
  msg.content %}`)، وبعده — حسب `message_type` — إما `<img>` مصغّرة
  قابلة للتكبير (رابط `target="_blank"` لنفس الصورة بحجمها الكامل)،
  أو بطاقة ملف (أيقونة + اسم الملف + "اضغط للتحميل"، رابط تحميل مباشر
  لـ `attachment_file.url`).
- **`attachment_file_name` property جديدة على الموديل نفسه** (بدل
  `slice` بعدد أحرف ثابت في التمبلت زي `msg.attachment_file.name|slice:"18:"`)
  — بترجع اسم الملف بس من غير مسار `group_chat/files/...`، عشان
  التمبلت والأدمن (`short_content`) يستخدموا نفس الـ property من غير
  تكرار منطق `rsplit('/', 1)` في أكتر من مكان، وعشان الكود يفضل صحيح
  حتى لو `upload_to` اتغيّر لاحقًا (الـ slice بعدد ثابت كان هيبقى هش).
- JS بسيط (`change` listener على الحقلين) بيمسح اختيار الحقل التاني
  لما حد يتختار (منع اختيار الاتنين من الواجهة نفسها)، وبيعرض اسم
  الملف المختار (`#chat-attach-filename`) قبل الإرسال — تحسين UX بس،
  مفيش أي تأثير على الفحص الحقيقي في السيرفر.
- Breakpoint الموبايل (`560px`) اتصحح: كان بيستهدف `.chat-form`
  (اللي بقى دلوقتي الـ container العمودي الخارجي)، وبقى يستهدف
  `.chat-form-row` (صف التكستاريا+الزرار) بدل كده — عشان صف الإرفاق
  (`.chat-attach-row`) يفضل بصفوفه الطبيعية (`flex-wrap: wrap`) على
  الموبايل من غير ما يتكسر بالغلط بنفس قاعدة العمودي القديمة.

### 7) `chat_mode == 'broadcast_only'` بيمنع المرفقات برضه — من غير أي كود إضافي

زي ما اتطلب ("برضو ميقدرش الطالب يرفع صورة/ملف")، الفحص ده متحقق
تلقائيًا من غير أي شرط إضافي: فورم الإرسال بالكامل (النص + زرارين
الإرفاق) اتلف من Part 29 بشرط `{% if is_owner or group.chat_mode !=
'broadcast_only' %}` — يعني في وضع الإذاعة، الفورم كله (مش بس حقل
النص) مش موجود خالص في الـ HTML للطالب. وعلى مستوى السيرفر، فحص
`chat_mode == 'broadcast_only' and not is_owner` في أول
`action == 'send_message'` بيرفض أي POST (نص أو مرفق) قبل ما يوصل
لمنطق قراءة الملفات خالص — مفيش أي تعديل إضافي كان لازم يتعمل هنا،
الفحص الموجود من Part 29 شامل تلقائيًا.

### 8) الأدمن — `message_type` في `list_display`/`list_filter`، والحقول الجديدة `readonly`

`GroupChatMessageAdmin`:
- `message_type` اتضاف في `list_display` (بعد `sender`) و`list_filter`
  — عشان الأدمن يقدر يفلتر بسهولة على الرسائل اللي فيها صور/ملفات.
- `attachment_image` و`attachment_file` اتضافوا في `readonly_fields`
  (بنفس فلسفة باقي الحقول هنا — الأدمن للمراجعة/الإشراف بس، مش
  للتعديل، زي ما كان موثق من Part 14).
- `short_content` اتعدّلت: لو `content` فاضي (رسالة صورة/ملف من غير
  نص)، بترجع وصف مختصر للمرفق نفسه (`📷 صورة` أو `📎 <اسم الملف>`) بدل
  ما تظهر فاضية في قايمة الأدمن.

### 9) مفيش أي migration/تعديل على `groups/urls.py`

الجزء ده كله على نفس الـ `action='send_message'` الموجود من Part 14
جوه `group_detail` — مفيش URL جديد، ومفيش view جديدة. الـ migration
الوحيدة (`0014_groupchatmessage_attachments.py`) بتعتمد على
`('groups', '0013_teachergroup_chat_mode')` (آخر migration معروفة حسب
الملف اللي بعته Ahmed فعليًا في الجلسة دي).

## سجل الأجزاء (تابع)

### Part 30 (المرحلة الثانية) — إرفاق صور وملفات في الشات الجماعي
الحالة: تم — ⚠️ لسه محتاج تشغيل `makemigrations --check --dry-run` +
`migrate` فعليًا على السيرفر (تفاصيل تحت).
تفاصيل:
- عدّلت `groups/models.py::GroupChatMessage`: `content` بقى
  `blank=True`، وضفت `message_type` (`CharField`, choices
  `text`/`image`/`file`, `default='text'`)، `attachment_image`
  (`ImageField`, `upload_to='group_chat/images/'`, `null=True,
  blank=True`)، `attachment_file` (`FileField`,
  `upload_to='group_chat/files/'`, `null=True, blank=True`)، وproperty
  جديدة `attachment_file_name`. باقي الموديل والملف كله (كل موديلات
  `groups` التانية) **متلمسش خالص**.
- عملت migration جديدة `groups/migrations/0014_groupchatmessage_attachments.py`
  (`AlterField` على `content` + 3× `AddField`)، بتعتمد على
  `('groups', '0013_teachergroup_chat_mode')`.
- عدّلت `groups/views.py`:
  - ضفت 4 ثوابت جديدة (`_ALLOWED_CHAT_IMAGE_EXTENSIONS`,
    `_ALLOWED_CHAT_FILE_EXTENSIONS`, `_CHAT_IMAGE_MAX_BYTES`,
    `_CHAT_FILE_MAX_BYTES`) جنب `_ALLOWED_RECORDING_EXTENSIONS` من
    Part 26 مباشرة.
  - أعدت كتابة الفرع `if action == 'send_message':` جوه `group_detail()`
    بالكامل — تفاصيل التسلسل الكامل فوق في "قرارات معمارية"، قسم 5.
    **باقي الملف (كل الـ views من Part 7 لحد Part 29) متلمسش خالص.**
- عدّلت `groups/admin.py::GroupChatMessageAdmin` — تفاصيل فوق، قسم 8.
  باقي الملف **متلمسش خالص**.
- عدّلت `groups/templates/groups/group_detail.html`:
  - CSS جديد بس (`.chat-form-row`, `.chat-attach-row`,
    `.chat-attach-label`, `.chat-attach-hint`, `.chat-attach-filename`,
    `.chat-attachment-image`, `.chat-attachment-file` وما يتبعها) —
    إضافة، مفيش أي حذف لأي كلاس موجود.
  - فورم الشات بقى `multipart/form-data` مع صف إرفاق جديد (زرارين
    صورة/ملف) — تفاصيل فوق، قسم 6.
  - عرض الفقاعة اتعدّل يعرض الصورة/الملف حسب `message_type`.
  - breakpoint الموبايل (`560px`) اتصحح من `.chat-form` لـ
    `.chat-form-row` (تفاصيل فوق، قسم 6).
  - JS جديد بسيط لمنع اختيار صورة+ملف مع بعض من الواجهة + عرض اسم
    الملف المختار قبل الإرسال.
  - باقي الملف (أقسام اللايف، الدروس، إدارة الجلسات، فقاعات الرسائل
    النصية القديمة، وضع الإذاعة من Part 29) **متلمسش خالص**.
- اتفحص syntax كل ملفات Python المعدّلة (`python -m py_compile` على
  `models.py`/`views.py`/`admin.py`/الـ migration) — عدّت كلها من غير
  أخطاء. اتفحص توازن `{% if/for %}` ↔ `{% endif/endfor %}` في
  `group_detail.html` (35 if/endif، 8 for/endfor) — متطابقين.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مدرس/طالب في جروب `chat_mode='open'` يفتح صفحة الجروب → يضغط زرار
  "صورة" ويختار ملف jpg 2 ميجا → اسم الملف يظهر تحت الزرارين → يضغط
  "إرسال" (من غير أي نص) → الرسالة تظهر في الشات كصورة مصغّرة قابلة
  للتكبير. نفس المستخدم يبعت ملف pdf 3 ميجا مع نص "شوفوا المذكرة دي" →
  الرسالة تظهر بالنص فوق وبطاقة الملف تحته. مستخدم يحاول يبعت صورة
  15 ميجا → رفض برسالة وضوح الحد المسموح. طالب في جروب
  `chat_mode='broadcast_only'` (مش هو المدرس) → فورم الإرسال بالكامل
  (نص + إرفاق) مش موجود خالص في الصفحة، ولو حاول يبعت POST مباشر
  بمرفق → بيترفض بنفس رسالة "المدرس قافل الشات..." من غير ما يتحفظ أي
  حاجة.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. **الأهم**: migration الجديدة (`0014_groupchatmessage_attachments.py`)
     بتفترض إن `0013_teachergroup_chat_mode` (Part 29) هي آخر migration
     في تطبيق `groups` — لازم تتأكد بـ `makemigrations --check --dry-run`
     فعليًا على السيرفر قبل `migrate` لو فيه أي migration أحدث مش
     موثقة/مبعوتة في الجلسة دي.
  2. حدود الحجم (5 ميجا صور / 15 ميجا ملفات) وقائمة الامتدادات المسموحة
     اخترتهم بنفسي كثوابت في `views.py` (مش `settings.py`) — تفاصيل
     السبب فوق في "قرارات معمارية"، قسم 4. لو Ahmed عايز يتحكم فيهم من
     `settings.py` بدل الكود (زي `GROUP_LIVE_RECORDING_MAX_UPLOAD_MB`
     من Part 26)، سهل التحويل لاحقًا.
  3. مفيش أي مرفق تاني مسموح (صوت، فيديو) — الطلب الأصلي قال "صور
     وملفات" بس، فـ `_ALLOWED_CHAT_FILE_EXTENSIONS` مقصودة على مستندات
     مكتبية + أرشيف بس (pdf/doc/docx/xls/xlsx/ppt/pptx/txt/zip/rar)،
     من غير أي صيغة صوت/فيديو أو صيغة تنفيذية.
  4. مفيش حد أقصى لعدد المرفقات في نفس المحادثة أو تنظيف/أرشفة
     للمرفقات القديمة (نفس ملاحظة "مفيش pagination حقيقي للشات" من
     Part 14 — لو المرفقات كترت مع الوقت، مساحة التخزين (`MEDIA_ROOT`)
     ممكن تكبر بسرعة، ده تحسين منفصل مش من نطاق الجزء ده.

### ✅ تأكيد فعلي على سيرفر Ahmed
- `python manage.py showmigrations groups` أكّد إن `0013_teachergroup_chat_mode`
  كانت فعلاً آخر migration مطبّقة قبل الجزء ده — مفيش أي migration
  وسيطة مفقودة، فـ `dependencies` بتاعة `0014` كانت صحيحة من غير أي
  تعديل مطلوب.
- `python manage.py makemigrations --check --dry-run` رجع بس نفس
  الملاحظة التجميلية المعروفة من الأجزاء اللي فاتت (توحيد نوع حقل `id`
  لـ `BigAutoField`) — مفيش أي تحذير جديد غير متوقع متعلق بـ
  `groupchatmessage`.
- `python manage.py migrate groups` طبّق `groups.0014_groupchatmessage_attachments`
  بنجاح.
- `python manage.py check` رجع "System check identified no issues".
- اختبار يدوي فعلي على المتصفح: إرسال رسالة نص عادي (لسه شغالة زي
  الأول)، رفع صورة من غير نص (اتحفظت في `group_chat/images/` وظهرت
  كصورة مصغّرة قابلة للتكبير)، رفع ملف مع نص مصاحب (اتحفظ في
  `group_chat/files/` وظهر كبطاقة ملف مع رابط تحميل شغال)، رفض الملفات
  الأكبر من الحد المسموح ورفض الامتدادات الغير مدعومة، اختفاء فورم
  الإرسال بالكامل للطالب في وضع `broadcast_only`، وعرض `message_type`
  والمرفقات صح في `/admin/groups/groupchatmessage/` — كله اتأكد شغال
  بنجاح.

**Part 30 شغال فعليًا 100% على السيرفر دلوقتي.**

### ✅ تأكيد فعلي على سيرفر Ahmed (Part 31)

- شغّلت `publish_scheduled_group_lessons()` يدويًا من `manage.py shell`
  أول مرة — نجح فعليًا (نشر درس، وبعت إيميل التأكيد وصل فعليًا).
- بعد كده اتأكد السيناريو الكامل تلقائيًا من غير أي نداء يدوي:
  1. مدرس رفع درس واختار "جدولة" لميعاد قريب.
  2. الدرس ظهر في `group_lessons_list` بـ badge "مجدول" (أصفر) زي المتوقع.
  3. الـ Celery beat process بعت التاسك فعليًا في معاده بالظبط
     (`Scheduler: Sending due task publish-scheduled-group-lessons`
     ظهرت في لوج الـ beat عند الساعة المحددة).
  4. **⚠️ مشكلة اتكشفت واتصلحت أثناء الاختبار**: الـ beat process لوحده
     مبيكفيش — هو بس بيحط التاسك في الطابور (Redis broker)، التنفيذ
     الفعلي مسؤولية **الـ worker process** بشكل منفصل تمامًا. لازم
     الاتنين (`celery -A Eduvia beat` و`celery -A Eduvia worker`)
     يكونوا شغالين مع بعض في نفس الوقت كـ processes منفصلة. على ويندوز
     تحديدًا، الـ worker محتاج يتشغّل بـ `--pool=solo` (مشكلة معروفة في
     Celery مع الـ multiprocessing pool الافتراضي على ويندوز):
    
    celery -A Eduvia worker -l info --pool=solo
    5. بعد ما الاتنين اشتغلوا مع بعض، الدرس اتنشر تلقائيًا لوحده في معاده
     بالظبط من غير أي تدخل يدوي — الـ badge اتغيّر من "مجدول" (أصفر) لـ
     "منشور" (أخضر) في `group_lessons_list`، وطالب عضو قدر يفتحه ويشغّله
     عادي.
- **ملحوظة تشغيلية مهمة لأي نشر مستقبلي (production)**: على السيرفر
  الحقيقي (مش بيئة التطوير المحلية دي)، لازم الـ worker والـ beat
  يبقوا مُدارين كـ services دائمة (زي `systemd` أو `supervisor`) مش
  terminal windows مفتوحة يدويًا — لو أي واحد فيهم وقف (كراش، إعادة
  تشغيل السيرفر، إلخ) التاسكات الدورية (تجميد الاشتراكات، التنبيهات،
  نشر الدروس) هتوقف تمامًا من غير أي تنبيه. ده مش خاص بـ Part 31 بس —
  نفس الملحوظة سارية على تاسكات Part 15/16 كمان، لكن اتأكدت عمليًا هنا
  لأول مرة أثناء اختبار الجزء ده.

**Part 31 شغال فعليًا 100% على السيرفر دلوقتي (beat + worker شغالين مع
بعض، والنشر التلقائي والإشعارات بيحصلوا في المعاد الصح من غير أي تدخل
يدوي).**

## قرارات معمارية اتاخدت (Part 32)

### 1) منطق التجميع في ملف مستقل (`groups/schedule.py`) مش مكرر في كل view

بدل ما أكرر نفس منطق "اجمع GroupLiveSession المجدولة + GroupLesson
المجدولة ورتبهم بالتاريخ" في 3 أماكن مختلفة (صفحة الجدول لجروب واحد،
ودجت الطالب، ودجت المدرس)، عملته دالة واحدة `get_group_schedule_items(group)`
في ملف جديد `groups/schedule.py` (بنفس روح `groups/access.py` — دالة
checker/builder بسيطة من غير أي اعتماد على request). الدالة بترجع list
من dicts (`kind`, `title`, `when`, `obj`) مرتبة تصاعديًا بـ `when`.
عناصر من غير ميعاد فعلي (`publish_at`/`scheduled_at` فاضي) بتتستبعد
بالكامل — مفيش معنى لعنصر "قادم" من غير تاريخ نرتب بيه.

### 2) صفحة الجدول لجروب واحد (`group_schedule`) — ملف منفصل (`views_schedule.py`)

نفس القرار التنظيمي المتبع في `views_lessons.py` من Part 28 — view واحدة
بسيطة في ملف مستقل عن `groups/views.py` (اللي بقى كبير أصلًا)، بتستورد
`_get_group_and_membership_or_403` من `views.py` بدل ما تكرره. نفس فحص
الصلاحية المستخدم في `group_lessons_list`/`group_recordings` (عضوية أو
ownership، وفحص `is_group_content_accessible` للطالب العضو بس — المدرس
دايمًا يقدر يفتح صفحة جدوله حتى لو الجروب متجمد).

### 3) الروابط جوه صفحة الجدول — مش كل عنصر بياخد رابط

- عناصر اللايف بتتحول لرابط `join_live_session` **بس للطالب العضو**،
  مش للمدرس — لأن `join_live_session` (Part 25) محمية بـ
  `student_required` فقط، فمفيش داعي نعرض للمدرس رابط هيترفض على طول
  (نفس القيد الموجود بالفعل في `group_detail.html` لزرار "الميعاد").
- عناصر الدرس بتتحول لرابط `watch_group_lesson` **بس للمدرس صاحب
  الجروب** — لأنه الوحيد اللي يقدر يفتح درس لسه مش منشور (`is_published=False`)،
  زي فحص الأمان الموجود في `views_lessons.py::watch_group_lesson` من
  Part 28. للطالب العضو، العنصر بيتعرض كمعلومة بس (هينزل يوم كذا) من
  غير أي رابط.

### 4) الودجتين المجمّعين (طالب/مدرس) — تعديل على views موجودة، مش views جديدة

بدل ما أعمل view/URL منفصل للودجت، عدّلت `my_learning_groups` (الطالب)
و`teacher_groups_dashboard` (المدرس) في `groups/views.py` (إضافة، مش
استبدال) عشان يحسبوا `upcoming_schedule_items`:
- **الطالب**: بيجمّع بس من الجروبات النشطة (`is_active=True`) — مفيش
  داعي نستعلم على جروب متجمد، لأن أي رابط هيتفحص عضويته/نشاطه تاني عند
  فتحه فعليًا. عناصر اللايف بس بتاخد رابط (`join_live_session`)، عناصر
  الدرس من غير رابط (نفس سبب النقطة 3).
- **المدرس**: بيجمّع من كل جروباته (مفيش فحص `is_active` — المدرس
  يقدر يدير جدول جروبه حتى لو متجمد، نفس نمط باقي صفحات الجروب له).
  عناصر الدرس بتاخد رابط `watch_group_lesson` (شغال، هو المالك)، عناصر
  اللايف بتودّي لصفحة الجروب نفسها (`group_detail`) بدل `join_live_session`
  (مرفوضة على دور instructor).
- حد **[:8]** لعدد العناصر المعروضة في الودجتين اخترته بنفسي (مفيش
  تحديد صريح في الطلب الأصلي) — نفس فلسفة حد الـ [:5] في
  `recent_ended_live_sessions` من Part 26.

### 5) رابط "الجدول القادم" في `group_detail.html`

نفس نمط رابطي "مكتبة التسجيلات" (Part 26) و"الدروس المسجلة" (Part 28)
بالظبط — زرار بسيط ظاهر دايمًا (للمدرس والطالب العضو)، من غير أي عداد
أو استعلام إضافي في `group_detail()` نفسها (الصفحة المستهدفة هي اللي
بتحسب وتعرض القايمة).

## سجل الأجزاء (تابع)

### Part 32 — صفحة التقويم/الجدول للطالب
الحالة: تم
تفاصيل:
- عملت `groups/schedule.py` (دالة `get_group_schedule_items`) —
  تفاصيل فوق، قسم 1.
- عملت `groups/views_schedule.py` (view واحدة: `group_schedule`) —
  تفاصيل فوق، قسم 2/3.
- عدّلت `groups/urls.py`: ضفت مسار `<int:group_id>/schedule/` →
  `views_schedule.group_schedule`، اسمه `group_schedule` — قبل الـ
  pattern العام `<int:group_id>/` في آخر الملف.
- عدّلت `groups/views.py`:
  - استوردت `get_group_schedule_items` من `.schedule`.
  - `teacher_groups_dashboard`: إضافة حساب `upcoming_schedule_items`
    مجمّع من كل جروبات المدرس، وتمريره للتمبلت.
  - `my_learning_groups`: نفس الفكرة، مجمّع من الجروبات النشطة بس.
  - **باقي الملف متلمسش خالص.**
- أنشأت `groups/templates/groups/group_schedule.html` — صفحة الجدول
  الكاملة لجروب واحد، بنفس نظام "Obsidian Academy" (نفس CSS variables/
  topbar/breadcrumb من `group_lessons_list.html`).
- عدّلت `groups/templates/groups/group_detail.html`: رابط "الجدول
  القادم" جنب رابطي التسجيلات/الدروس — تفاصيل فوق، قسم 5.
- عدّلت `groups/templates/groups/my_learning_groups.html`: ودجت
  "الجدول القادم" فوق قايمة الجروبات (CSS + HTML جديد بس، باقي الملف
  متلمسش).
- عدّلت `groups/templates/groups/dashboard.html`: نفس الودجت للمدرس،
  قبل قسم "Your Groups" (CSS + HTML جديد بس، باقي الملف متلمسش).
- **مفيش أي migration جديدة أو تعديل على أي موديل** — الجزء ده بالكامل
  views + template + منطق تجميع، بدون أي حقل جديد.
- اتفحص syntax كل ملفات Python الجديدة/المعدّلة (`python -m py_compile`)
  وتوازن `{% if/for %}` ↔ `{% endif/endfor %}` في التمبلتس الأربعة
  (group_detail، my_learning_groups، dashboard، group_schedule) — كلها
  عدّت من غير أخطاء.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. حد الـ [:8] عنصر في الودجتين اخترته بنفسي — سهل تتغير لو عايز رقم
     مختلف.
  2. عناصر اللايف المجدولة مفيهاش أي "زرار ابدأ دلوقتي" مباشر من صفحة
     الجدول أو الودجتين — نفس الفجوة الموثقة من Part 24 (مفيش view لسه
     بتحوّل جلسة `scheduled` لـ `live` مباشرة). لو Part 24 اتصلحت لاحقًا
     (نقطة أ الموثقة هناك — زرار "ابدأ" على الجلسة المجدولة)، ممكن
     نضيف نفس الزرار هنا كمان.
  3. الودجتين (طالب/مدرس) بيحسبوا كل مرة الصفحة تتفتح (مفيش أي caching)
     — لو عدد الجروبات كبر جدًا مع الوقت، ممكن يحتاج تحسين أداء لاحقًا
     (نفس ملاحظات الأداء المتكررة في أجزاء تانية زي حد الشات 100 رسالة).

     تم تاكيد ان اختبار البارت دا شغال 

## قرارات معمارية اتاخدت (Part 33)

### 1) اكتشاف مهم: نظام "الواجبات" الفعلي في courses أوتوماتيكي بالكامل، مش تصحيح يدوي

قبل أي كود، فحصت `courses/models.py` و`courses/views.py` و`courses/admin.py`
الحقيقيين. النظام الأحدث للواجبات هناك (`LessonTask` + `LessonTaskSubmission`،
بأنواع mcq/essay/file_upload/external_link) **نظام تصحيح تلقائي بالكامل**:
الدرجة (`score`) بتتحسب أوتوماتيك كنسبة مئوية (مقارنة `correct_answer` في
حالة mcq)، و`passed` بتتحدد من `passing_score` تلقائيًا. **مفيش أي حقل
`grade`/`feedback`/`graded_by`/`graded_at` في courses خالص** — حتى تسليمات
essay/file_upload بتتسجل من غير أي تصحيح يدوي فعلي من المدرس.

ده مختلف عن اللي Part 33/34 مطلوبين فعليًا (المدرس "يصحح ويدي درجة" بفورم
درجة+ملاحظة، موضح صراحة في نص Part 34: "لكل واحد فورم بسيط درجة+ملاحظة
وزرار حفظ"). **القرار**: بنيت `GroupAssignment`/`GroupAssignmentSubmission`
بنظام تصحيح **يدوي** بالحقول المطلوبة صراحة في نص Part 33 (title,
description, attachment, due_date, max_grade / student, assignment,
content, attachment, submitted_at, grade, feedback, graded_by, graded_at)
— ده التصميم المقصود فعليًا حسب خريطة الأجزاء (Part 34 محتاج تصحيح يدوي)،
مش نسخ لنمط أوتوماتيكي مالوش نظير حقيقي هنا في courses. الحاجة الوحيدة
اللي فعلاً اتنسخت بنفس الروح من courses هي أسلوب تخزين الملفات (`FileField`
عادي فوق التخزين المحلي، زي `courses.VideoFile.file`/`LessonAttachment.file`
— بدون أي بنية تخزين جديدة).

### 2) `GroupAssignment`

```python
group = ForeignKey(TeacherGroup, related_name='assignments', on_delete=CASCADE)
title = CharField(max_length=300)
description = TextField(blank=True)
attachment = FileField(upload_to='group_assignments/attachments/', null=True, blank=True)
due_date = DateTimeField(null=True, blank=True)
max_grade = PositiveIntegerField(default=100)
created_at = DateTimeField(auto_now_add=True)
```
- `max_grade` اتعمل `PositiveIntegerField` (مش `DecimalField`) — قرار
  بسيط بيّ، لإن الطلب الأصلي مقالش صراحة عايز كسور عشرية في الدرجة، وده
  أنسب لفورم "درجة + ملاحظة" بسيط في Part 34. القيمة الافتراضية `100`
  اخترتها بنفسي.
- `attachment` اختياري (مرفق تعليمات/ورقة أسئلة من المدرس) — مش مطلوب
  صراحة في نص الجزء لكن منطقي كجزء من "attachment" المذكورة في القايمة.
- `Meta.ordering = ['-due_date', '-created_at']` — الأقرب ميعادًا/الأحدث
  أول، اختيار بسيط مني بنفس روح باقي موديلات `groups`.
- `property` بسيطة `submissions_count` — تسهيل لعرض العدد في القوايم
  (الأدمن دلوقتي، وPart 34 محتمل يستخدمها).

### 3) `GroupAssignmentSubmission`

```python
assignment = ForeignKey(GroupAssignment, related_name='submissions', on_delete=CASCADE)
student = ForeignKey(settings.AUTH_USER_MODEL, related_name='group_assignment_submissions', on_delete=CASCADE)
content = TextField(blank=True)
attachment = FileField(upload_to='group_assignments/submissions/', null=True, blank=True)
submitted_at = DateTimeField(auto_now_add=True)
grade = PositiveIntegerField(null=True, blank=True)
feedback = TextField(blank=True)
graded_by = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+', on_delete=SET_NULL)
graded_at = DateTimeField(null=True, blank=True)
```
- `grade` اتعمل `null=True` (مش بس `blank=True`) عمدًا — عشان نفرّق بين
  "لسه ما اتصححش" (`None`) و"اتصحح بصفر" (`0`)؛ لو كانت `blank=True` بس
  كانت هتتخزن كصفر افتراضي وده معناه مختلف تمامًا.
- `Meta.unique_together = ('assignment', 'student')` — زي ما اتطلب
  بالظبط، الطالب يسلّم مرة واحدة بس لكل واجب.
- **منطق "الطالب يقدر يعدّل تسليمه لحد ما يتصحح" مش متطبق على مستوى
  الموديل هنا** — هيتطبق في الـ view في Part 34 (فحص `graded_at is None`
  قبل السماح بالتعديل)، بنفس فلسفة باقي فحوصات المشروع اللي بتتم يدويًا
  في الـ view مش عن طريق `Model.clean()`.
- `property` بسيطة `is_graded` (`graded_at is not None`) لتسهيل الفحص
  في القوايم/التمبلتس لاحقًا.

### 4) الأدمن

سجّلت الموديلين في `groups/admin.py` بنفس نمط باقي `groups`:
- `GroupAssignmentAdmin`: `list_display` بسيط (عنوان، جروب، ميعاد
  التسليم، الدرجة القصوى، عدد التسليمات، تاريخ الإنشاء)، `list_filter`
  على `group__category`، `search_fields` على العنوان/الوصف/اسم
  الجروب/اسم المدرس.
- `GroupAssignmentSubmissionAdmin`: **كل الحقول `readonly`** (بنفس نمط
  `GroupChatMessageAdmin` من Part 14 بالظبط) — التسجيل هنا لأغراض
  المراجعة/الإشراف بس، والتصحيح الفعلي (درجة+ملاحظة) هيتم من view
  مخصص للمدرس هيتبنى في Part 34، مش من لوحة الأدمن. ضفت `grade_badge`
  (بترجع badge ملوّن زي `_status_badge` المستخدمة بالفعل من Part 21 —
  gold "لسه ما اتصححش" لو `grade is None`، أو emerald بالدرجة/القصوى
  لو متصحح) لسهولة المتابعة بنظرة واحدة.

### 5) Migration

`groups/migrations/0015_groupassignment_groupassignmentsubmission.py`
— `CreateModel` للموديلين + `AlterUniqueTogether`، بتعتمد على
`('groups', '0014_groupchatmessage_attachments')` (آخر migration معروفة
حسب النسخة الحقيقية اللي بعتها Ahmed). ⚠️ نفس تحذير كل migration مكتوبة
يدويًا في المشروع: لازم تتأكد بـ `makemigrations --check --dry-run`
فعليًا على السيرفر قبل `migrate`، لو فيه migration أحدث مش موثقة هنا.

## سجل الأجزاء (تابع)

### Part 33 — موديل GroupAssignment + GroupAssignmentSubmission (بنفس نمط الكورسات)
الحالة: تم (الموديلين + الميجريشن + تسجيل الأدمن) — ⚠️ لسه محتاج تشغيل
فعلي على السيرفر (تفاصيل تحت).
تفاصيل:
- قريت `courses/models.py`، `courses/views.py`، `courses/admin.py`،
  `courses/forms.py`، `courses/urls.py` الحقيقيين كاملين قبل أي كود —
  الاكتشاف المهم (نظام courses أوتوماتيكي بالكامل، مفيش تصحيح يدوي) موثق
  بالتفصيل فوق في "قرارات معمارية"، قسم 1.
- ضفت موديل `GroupAssignment` في `groups/models.py` (آخر موديل في
  الملف، بعد `GroupLesson` من Part 27) — تفاصيل الحقول فوق، قسم 2.
- ضفت موديل `GroupAssignmentSubmission` في نفس الملف — تفاصيل الحقول
  فوق، قسم 3.
- عملت migration جديدة
  `groups/migrations/0015_groupassignment_groupassignmentsubmission.py`
  (`CreateModel` × 2 + `AlterUniqueTogether`)، بتعتمد على
  `('groups', '0014_groupchatmessage_attachments')`.
- سجّلت الموديلين في `groups/admin.py` (`GroupAssignmentAdmin` و
  `GroupAssignmentSubmissionAdmin`) — تفاصيل كاملة فوق، قسم 4. **باقي
  الملف (كل الموديلات/الـ admin classes التانية من Part 1 لحد Part 30)
  متلمسش خالص** — التعديل كله: (1) إضافة `GroupAssignment` و
  `GroupAssignmentSubmission` لاستيراد الموديلات الموجود فوق، (2) قسمين
  جديدين في آخر الملف بعد `GroupLessonAdmin`.
- اتفحص syntax الملفات الثلاثة (`python -m py_compile`) — عدّت من غير
  أخطاء.
- **مفيش أي تعديل على أي view أو template في الجزء ده** — زي ما اتطلب
  بالظبط ("دلوقتي بس اعمل الموديلين").
- ⚠️ حاجات محتاجة قرار/انتباه من Ahmed:
  1. **الأهم (اكتشاف معماري)**: نظام واجبات courses الحقيقي أوتوماتيكي
     بالكامل (مفيش تصحيح يدوي)، فموديلات الجزء ده **مش نسخة من نمط
     موجود فعليًا**، بل تصميم جديد بالحقول المطلوبة صراحة في نص
     Part 33/34 (تصحيح يدوي). لو Ahmed كان قاصد فعليًا "استخدم نفس
     الأوتوماتيكية اللي في courses" بدل تصحيح يدوي، ده يحتاج مراجعة
     قبل Part 34 (هيغيّر شكل الموديلين تمامًا — مفيش `grade`/`feedback`
     يدويين، هيبقى فيه `questions`/`score`/`passed` بدل منهم).
  2. `max_grade` الافتراضية (`100`) و`PositiveIntegerField` (مش
     `Decimal`) اخترتهم بنفسي — سهل التغيير لو Ahmed عايز درجات كسرية
     أو قيمة افتراضية مختلفة.
  3. حقل `attachment` على `GroupAssignment` (مرفق المدرس) مش مطلوب
     صراحة في نص Part 33 لكن ضمني ضمن "attachment" في القايمة — لو
     Ahmed مش محتاجه، سهل نشيله في migration بسيطة لاحقة.
  4. منطق "منع تعديل التسليم بعد التصحيح" مش متطبق هنا (على مستوى
     الموديل) — هيتطبق كفحص في الـ view وقت Part 34.

## قرارات معمارية اتاخدت (Part 34)

### 1) الملفات اللي اشتغلت عليها فعليًا (النسخ الحقيقية، مش من التوثيق)

الجزء ده جالي على مرحلتين. المرحلة الأولى (Backend — views_assignments.py،
groups/tasks.py::_notify_student_assignment_graded، groups/urls.py) كانت
خلصت بالفعل قبل الجلسة دي (بعتهالي Ahmed جاهزة). المرحلة الحالية (الجزء
اللي كنت لسه ناقصه فعليًا من Part 34: الأربع تمبلتس + التعديلات على
group_detail.html/my_learning_groups.html/views.py) اشتغلت عليها مباشرة
على النسخ الحقيقية اللي بعتهالي Ahmed في نفس الجلسة دي (`group_detail.html`،
`my_learning_groups.html`، `upload_group_lesson.html` كمرجع تصميم مباشر،
`models.py`، `tasks.py`، `views.py`، `watch_group_lesson.html`،
`group_lessons_list.html`، `urls.py`، `views_assignments.py`) — مفيش أي
إعادة بناء من التوثيق، نفس الدرس المتكرر من Part 15/20/23/28.

### 2) الأربع تمبلتس — نفس نظام "Obsidian Academy" حرفيًا، مرجع مباشر: upload_group_lesson.html/group_lessons_list.html/watch_group_lesson.html

زي ما اتطلب بالظبط، الأربع تمبلتس الجديدة نسخت نفس الـ CSS
variables/topbar/breadcrumb/messages markup من ملفات الدروس المسجلة
(Part 28) بالحرف — مفيش أي مكتبة CSS خارجية جديدة، ومفيش أي ستايل مخترع
من غير مرجع:

- **`create_group_assignment.html`**: نفس هيكل `.form-card`/`.field-group`
  من `upload_group_lesson.html` بالظبط (حتى الـ `cardReveal` animation
  والـ `box-shadow: var(--glow)` المطابقة). فورم `multipart/form-data`
  (لازم للمرفق) بحقول: عنوان (إجباري)، وصف، مرفق (اختياري، `<input
  type="file">` بسيط — مفيش `upload-zone` معقدة زي
  `submit_payment_proof.html` لإن ده مرفق عام (PDF/Word محتمل) مش صورة
  محتاجة معاينة)، ميعاد تسليم (`datetime-local` اختياري)، والدرجة القصوى
  (رقم، افتراضي 100 — نفس القيمة الافتراضية على الموديل من Part 33).
- **`group_assignments_list.html`**: نفس هيكل `.lesson-row` من
  `group_lessons_list.html` بالحرف (`fadeUp` animation، نفس الأيقونة
  الدائرية على اليسار). بيتفرّع حسب `is_owner` (اللي الـ view بيمرره):
  - **المدرس**: كل صف بيودّي لـ `grade_submissions`، وبادچ يمين الصف
    بتعرض "X / Y سلّموا" (من `row.submissions_count`/`row.total_members`
    اللي views_assignments.py بيحسبهم بالفعل).
  - **الطالب**: كل صف بيودّي لـ `submit_group_assignment`، وبادچ يمين
    الصف بتتغيّر حسب `row.my_submission`: "لسه ما سلمتش" (rose) / "قيد
    المراجعة" (gold) / "درجتك: X/Y" (emerald) — ونفس الألوان دي بتتحط
    على الأيقونة الدائرية على اليسار كمان (`is-graded`/`is-pending`
    classes) عشان التمييز البصري يبان من أول نظرة على الصف كله مش بس
    البادچ.
- **`submit_group_assignment.html`**: كارت `.assignment-brief` فوق (وصف
  الواجب + ميعاد التسليم + الدرجة القصوى + رابط تحميل مرفق المدرس لو
  موجود)، وتحته إما:
  - **`locked=True`** (اتصحح بالفعل): كارت للقراءة بس — بادچ "الواجب
    اتصحح" (emerald)، عرض الدرجة كبير (`.grade-display`، نفس روح
    `.grade-num` بتاعة `watch_group_lesson`)، إجابة الطالب (لو موجودة)،
    رابط المرفق (لو موجود)، وملاحظات المدرس (لو موجودة) — **من غير أي
    فورم خالص**، زي ما اتطلب بالظبط ("الطالب يقدر يعدّل تسليمه لحد ما
    يتصحح").
  - **غير كده**: فورم `multipart/form-data` عادي (إجابة نصية + مرفق
    اختياري)، وزرار الإرسال بيتغيّر نصه حسب وجود تسليم قائم ("تسليم
    الواجب" / "تحديث التسليم") — تمييز بصري بسيط إن ده أول تسليم أو
    تعديل لتسليم موجود.
- **`grade_submissions.html`**: كارت لكل تسليم (`.submission-card`) —
  أفاتار دائري بحرف أول اسم الطالب (نفس مفهوم `.chat-avatar` من Part 20)،
  اسم الطالب، وقت التسليم، بادچ حالة (اتصحح/محتاج تصحيح)، محتوى الإجابة
  ورابط المرفق (لو موجودين)، وتحتهم إما ملخص الدرجة (لو اتصحح بالفعل —
  للقراءة بس) أو فورم تصحيح صغير (`grade` + `feedback` + hidden
  `submission_id`) لكل تسليم لسه معلّق، بزرار "حفظ" منفصل لكل واحد (POST
  مباشر لنفس الصفحة، Post/Redirect/Get عادي زي باقي المشروع).

### 3) `group_detail.html` — رابط "الواجبات" بس، من غير أي تعديل Python

نفس نمط رابطي "مكتبة التسجيلات" (Part 26)/"الدروس المسجلة" (Part 28)/
"الجدول القادم" (Part 32) بالظبط — زرار `sess-btn-ghost` بعرض كامل، ظاهر
دايمًا للمدرس والطالب العضو، من غير أي عداد أو استعلام إضافي، فمفيش أي
تعديل على `group_detail()` (Python) خالص. الرابط اتحط بعد رابط "الجدول
القادم" مباشرة وقبل قسم "لايفات محتاجة رفع تسجيل".

### 4) `my_learning_groups.html` + `my_learning_groups()` — بادچ الواجبات المعلّقة

- **`views.py::my_learning_groups()`**: تعديل إضافي بس (مفيش حذف) — نفس
  نمط `live_session` المحسوب في نفس الدالة من Part 25 بالظبط. كل صف بقى
  بيحمل كمان `pending_assignments_count`:
  `group.assignments.exclude(submissions__student=request.user).count()`
  — بيتحسب بس لو الجروب `is_active` (نفس تبرير `live_session`: مفيش داعي
  للاستعلام على جروب متجمد، لأن `submit_group_assignment` هيرفض الطالب
  بنفس شرط `is_group_content_accessible` أصلاً حتى لو كان فيه واجب معلّق
  بالمصادفة). ضفت `GroupAssignment` لاستيراد الموديلات الموجود فوق (مش
  مستخدم مباشرة في السطر، بس موجود للوضوح ولأي استخدام مستقبلي — الاستعلام
  الفعلي بيمر من `group.assignments` الـ related manager). **باقي الدالة
  وباقي الملف بالكامل متلمسش خالص.**
- **`my_learning_groups.html`**: بادچ جديد (`.pending-assignments-badge`،
  لون gold بنفس روح `.pill-gold`) بيظهر جنب pills الفئة الدراسية جوه كل
  كارت جروب، **بس لو `row.pending_assignments_count` أكبر من صفر** —
  رابط قابل للضغط يودّي مباشرة لـ `group_assignments_list` بتاعة الجروب
  ده. نص البادچ بيتصرّف نحويًا حسب العدد (مفرد/جمع بسيط: "1 واجب محتاج
  تسليم" مقابل "3 واجبات محتاجين تسليم") — تفصيل بسيط مش مطلوب صراحة في
  نص الطلب، اخترته بنفسي لتحسين الوضوح.

### 5) الـ Backend (views_assignments.py + tasks.py + urls.py) — كانت جاهزة بالفعل، اتأكد من مطابقتها للمواصفة بس

راجعت الملفات التلاتة دي (اللي كانت خلصت قبل الجلسة الحالية) للتأكد إنها
متطابقة تمامًا مع المطلوب في نص Part 34 قبل ما أبني التمبلتس عليها:

- `create_group_assignment`/`group_assignments_list`/
  `submit_group_assignment`/`grade_submissions` (`groups/views_assignments.py`)
  موجودين بالضبط بالتوقيعات المطلوبة، وبيستخدموا نفس الـ context keys
  اللي التمبلتس الجديدة محتاجاها (`form_data`، `rows` بـ
  `submissions_count`/`total_members` أو `my_submission`، `submission`/
  `locked`، `submissions`).
- `groups/tasks.py::_notify_student_assignment_graded(submission)` موجودة
  بالفعل (مش `@shared_task` — إرسال فوري synchronous، بنفس فلسفة منح XP
  الفوري من Part 17 ومنطق Part 16/31 في بناء الإيميل)، وبتتنادى فعليًا من
  `grade_submissions` بعد كل عملية تصحيح ناجحة.
- `groups/urls.py` فيها الأربع مسارات المطلوبة (`create`/`list` بياخدوا
  `group_id`، `submit`/`grade` بياخدوا `assignment_id` بس — نفس فلسفة
  `watch_group_lesson`/`watch_group_recording` في استنتاج الجروب من
  الكائن نفسه)، كلهم محطوطين قبل الـ pattern العام `<int:group_id>/` في
  آخر الملف.

**مفيش أي تعديل على الملفات التلاتة دي في الجزء الحالي** — كانت مطابقة
للمواصفة بالفعل.

## سجل الأجزاء (تابع)

### Part 34 — واجهات إنشاء/تسليم/تصحيح الواجب
الحالة: تم
تفاصيل:
- الـ Backend (`groups/views_assignments.py`، `groups/tasks.py::_notify_student_assignment_graded`،
  مسارات `groups/urls.py`) كان خلص بالفعل قبل الجلسة الحالية — راجعته
  للتأكد من التطابق مع المواصفة (تفاصيل فوق، قسم 5) من غير أي تعديل.
- أنشأت 4 تمبلتس جديدة بنفس نظام "Obsidian Academy" (نفس CSS
  variables/topbar/breadcrumb من `upload_group_lesson.html`/
  `group_lessons_list.html`/`watch_group_lesson.html` — مرجع تصميم
  مباشر زي ما اتطلب بالظبط):
  - `groups/templates/groups/create_group_assignment.html`
  - `groups/templates/groups/group_assignments_list.html`
  - `groups/templates/groups/submit_group_assignment.html`
  - `groups/templates/groups/grade_submissions.html`
  تفاصيل كاملة لكل واحد فوق، قسم 2.
- عدّلت `groups/templates/groups/group_detail.html`: ضفت رابط "الواجبات"
  (نفس نمط رابطي مكتبة التسجيلات/الدروس المسجلة/الجدول القادم بالظبط)
  بعد رابط "الجدول القادم" مباشرة — إضافة فقط، من غير أي تعديل على أي
  قسم تاني في الملف، ومن غير أي تعديل Python على `group_detail()`.
- عدّلت `groups/templates/groups/my_learning_groups.html`: ضفت بادچ
  "واجبات معلّقة" (لون gold، رابط مباشر لقايمة واجبات الجروب) جنب pills
  كل جروب — ظاهر بس لو `pending_assignments_count` أكبر من صفر. باقي
  الملف متلمسش خالص.
- عدّلت `groups/views.py`:
  - ضفت `GroupAssignment` لاستيراد الموديلات الموجود فوق.
  - `my_learning_groups()`: تعديل إضافي بس (مفيش حذف) — كل صف بقى بيحمل
    `pending_assignments_count` (عدد واجبات الجروب اللي لسه ملهاش تسليم
    من الطالب، محسوبة بس لو الجروب نشط). تفاصيل كاملة فوق، قسم 4.
  - **باقي الملف (كل الـ views من Part 7 لحد Part 33) متلمسش خالص.**
- **مفيش أي migration جديدة أو تعديل على أي موديل** في الجزء ده — موديلات
  `GroupAssignment`/`GroupAssignmentSubmission` كانت جاهزة بالكامل من
  Part 33.
- اتفحص syntax `groups/views.py` (`python -m py_compile`) — عدّى من غير
  أخطاء. اتفحص توازن `{% if/for %}` ↔ `{% endif/endfor %}` في الست
  تمبلتس (الأربع الجديدة + `group_detail.html` + `my_learning_groups.html`
  المعدَّلين) — كلهم متطابقين (`group_detail.html`: 43/43،
  `my_learning_groups.html`: 16/16، والأربع الجدد بمعدل عادي حسب حجم كل
  ملف).
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مدرس يفتح صفحة جروبه → يضغط "الواجبات" → يضغط "واجب جديد" → يملأ
  الفورم ويحفظ → الواجب يظهر في القايمة بعدد تسليمات "0 / N". طالب عضو
  يفتح "جروباتي" → يشوف بادچ "1 واجب محتاج تسليم" جنب الجروب ده → يضغط
  عليه → يوصل لقايمة الواجبات → يضغط على الواجب (بادچ "لسه ما سلمتش")
  → يكتب إجابته ويسلّم → يرجع لقايمة الواجبات فيلاقي بادچ الواجب اتغيّر
  لـ "قيد المراجعة" → بادچ "جروباتي" اختفى (العدد بقى صفر). المدرس يفتح
  "تصحيح" الواجب → يشوف تسليم الطالب → يكتب درجة وملاحظة ويحفظ → إيميل
  بيتبعت للطالب (`_notify_student_assignment_graded`) → الطالب يرجع
  يفتح تسليمه فيلاقيه `locked` (للقراءة بس) وعليه درجته وملاحظات المدرس.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. مرفق فورم إنشاء الواجب (`create_group_assignment.html`) اتعمل
     `<input type="file">` بسيط (مش `upload-zone` تفاعلية زي
     `submit_payment_proof.html`) لإنه مرفق عام (ملف/PDF محتمل) مش صورة
     محتاجة معاينة حية — لو Ahmed عايز شكل مختلف، سهل التغيير.
  2. مفيش أي حد أقصى لحجم/نوع مرفق الواجب أو مرفق التسليم بيتفحص في
     الـ backend (`views_assignments.py`) — نفس مستوى الثقة المستخدم في
     `courses.Lesson.video_url`/مرفقات الشات قبل التحقق المضاف في Part 30
     (هنا مفيش تحقق نوع/حجم خالص، لإن الطلب الأصلي لـ Part 33/34 مقالش
     ده صراحة). لو Ahmed عايز نفس مستوى التحقق المستخدم في الشات (امتداد
     + حجم أقصى)، ده تحسين منفصل سهل الإضافة.
  3. نص بادچ "واجبات معلّقة" في `my_learning_groups.html` (مفرد/جمع بسيط)
     اخترته بنفسي — مفيش تحديد صريح في الطلب الأصلي غير "تنبيه بسيط".
  4. زي كل الأجزاء اللي فاتت، لو فيه migration أحدث على السيرفر مش موثقة
     هنا، محتاجة مراجعة — لكن الجزء ده أصلاً مفيهوش أي migration جديدة.

    تم تاكيد تشغيل البارت بنجاح دون اخطاء 

## قرارات معمارية اتاخدت (Part 35)

### 1) مكان الموديل: `groups/models.py` مش تطبيق `core`

البرومبت سايب القرار مفتوح ("أو تطبيق core لو شايف إنه أنسب مكان
معماريًا — وضّح قرارك"). اخترت **`groups/models.py`** بدل عمل تطبيق
`core` جديد، للأسباب دي:
- الاستخدام الرئيسي المتوقع (لينك "مهامي" في `dashboard.html` و
  `my_learning_groups.html`) أصلاً جوه سياق تطبيق `groups`.
- كل الموديلات المشابهة اللي اتبنت في المرحلة الثانية (الواجبات
  `GroupAssignment`، الدروس `GroupLesson`، اللايف `GroupLiveSession`)
  موجودة في نفس التطبيق ده.
- عمل تطبيق Django جديد بالكامل (app جديد في `INSTALLED_APPS`،
  migrations خاصة بيه) لموديل واحد بسيط فيه FK اختياري لـ `TeacherGroup`
  كان هيبقى تعقيد زيادة عن الحاجة الفعلية للجزء ده.

لو Ahmed شايف إن "المهام اليومية" هتكبر مستقبلاً (منطق مستقل، مش
مرتبط بالجروبات أصلاً)، سهل نفصلها بعدين بـ migration بسيطة (نقل
الموديل لتطبيق جديد).

### 2) `GroupTodoItem` — الحقول بالظبط زي المواصفة + `on_delete=CASCADE` على `group`

كل الحقول اتضافت بالظبط زي المطلوب (`owner`, `group`, `title`, `notes`,
`due_at`, `is_done`, `created_at`). `group` اختياري (`null=True,
blank=True`) عشان المهمة ممكن تكون شخصية بالكامل مش مرتبطة بأي جروب —
زي ما اتطلب صراحة. `on_delete=models.CASCADE` على `group` (مش
`SET_NULL`) — قرار مني: مهمة مرتبطة بجروب اتمسح بتفقد سياقها بالكامل
منطقيًا، فأنسب تتمسح معاه بدل ما تفضل معلّقة بجروب مش موجود.

`Meta.ordering = ['is_done', 'due_at', '-created_at']` — تحسين بسيط
فوق مجرد "مرتبة بـ `due_at`" المطلوبة صراحة في النص: المهام المعلّقة
(`is_done=False`) بتطلع أول حاجة تلقائيًا، وبعدين المخلّصة، من غير أي
فرز إضافي مطلوب في الـ view.

### 3) ملف `views_todo.py` منفصل (نفس نمط `views_lessons.py`/`views_schedule.py`/`views_assignments.py`)

نفس القرار التنظيمي المتبع من Part 28 — الـ views الجديدة في ملف
مستقل بدل ما تتضاف جوه `views.py` (اللي بقى كبير أصلاً، أكتر من 1480
سطر). **مفيش أي تعديل على `views.py` خالص في الجزء ده** — الملف ده
مالوش أي علاقة بالمهام اليومية، فمحتاجش أي `import`/تعديل عليه.

### 4) الصلاحية: `login_required` بس، من غير فحص role

المهام اليومية متاحة "للمدرس والطالب" بنفس الطريقة — المهمة شخصية
بالكامل (`owner=request.user`)، فمفيش داعي لـ `instructor_required` أو
`student_required`. أي مستخدم مسجّل دخول (بغض النظر عن دوره) يقدر
يستخدم `my_todo_list`/`toggle_todo_done` بنفس الصلاحيات بالظبط.

### 5) `my_todo_list` — view واحدة GET+POST (مش view منفصلة للإضافة)

بدل ما أعمل view تانية لفورم الإضافة، `my_todo_list` بتتعامل مع
الاتنين: GET بيعرض القايمة، POST (فورم الإضافة السريع) بينشئ
`GroupTodoItem` جديدة ويعمل redirect لنفس الصفحة (Post/Redirect/Get
عادي، بنفس نمط باقي فورمات المشروع البسيطة). فورم الإضافة السريع فيه
`title` (إجباري) و`due_at` (اختياري، `datetime-local`) بس — **مفيش
اختيار جروب في الفورم السريع** (`group` بيفضل `None` دايمًا من الفورم
ده)، بالظبط زي ما البرومبت حدد صراحة ("فورم إضافة سريع (`title` +
`due_at` اختياري)" من غير أي ذكر لاختيار جروب).

### 6) `toggle_todo_done` — AJAX حقيقي (نقل الصف بالـ DOM، مش reload)

الـ endpoint (`POST` بس، `JsonResponse`) بيتحقق من الـ ownership
(`owner=request.user`) قبل أي تعديل — لو المهمة مش بتاعت المستخدم
الحالي، بيرجع 404 (مش 403 — عشان منسربش معلومة عن وجود مهمة بتاعة حد
تاني بنفس الـ id، نفس مبدأ عدم الإفصاح لموارد شخصية بحتة). التبديل
الفعلي بسيط: `is_done = not is_done` + `save(update_fields=['is_done'])`.

في الـ frontend، الـ JS بينقل الصف فعليًا بين قسم "المعلّقة" وقسم
"المخلّصة" (`prepend` للعنصر في القايمة التانية) ويحدّث العدادات، من
غير أي `window.location.reload()` — الاتنين (المعلّقة والمخلّصة)
بيتعرضوا دايمًا في الـ DOM (حتى لو فاضيين، مخفيين بـ `display:none`)
عشان الـ JS يقدر ينقل العنصر بينهم مباشرة، بالظبط زي المطلوب ("AJAX
بسيط بدون إعادة تحميل الصفحة").

### 7) التمبلت — صفحة مستقلة (Obsidian Academy) + `_todo_row.html` جزئي

`groups/templates/groups/my_todo_list.html` نسخت نفس نظام "Obsidian
Academy" حرفيًا (نفس CSS variables/topbar/hero/footer من
`dashboard.html`/`my_learning_groups.html`) — نفس فورم الرسائل
(`<ul class="messages">`) المستخدم في باقي صفحات `groups`. عملت جزئي
`_todo_row.html` (`{% include %}`) عشان صف المهمة نفسه (checkbox
دائري + عنوان + ميعاد + badge الجروب لو موجود) يتكرر بنفس الـ markup
بالظبط في قسمي المعلّقة/المخلّصة، ويسهل على الـ JS يبني/ينقل نفس
الشكل بدون تكرار كود.

المهام المتأخرة (`due_at` فات ولسه `is_done=False`) بتتلوّن بلون rose
مميز (`.is-overdue` + `.overdue-tag`) — تحسين بصري بسيط مني (مش مطلوب
صراحة في نص Part 35؛ التمييز الكامل للمهام المتأخرة "بلون/badge مختلف
غير ما تحذفها" مطلوب رسميًا في **Part 36**، فالجزء ده بس بداية بسيطة
لنفس الفكرة عشان الصفحة متبقاش فاضية من أي مؤشر بصري من الأول).

### 8) اللينكات — إضافة فقط في `dashboard.html` و`my_learning_groups.html`

لينك "مهامي" اتضاف في الـ nav-links بتاعة الصفحتين (بعد لينك "Groups"/
"My Groups" مباشرة)، من غير أي تعديل تاني على أي قسم في الملفين. مفيش
أي تعديل على `views.py` (`teacher_groups_dashboard`/`my_learning_groups`)
مطلوب لإضافة اللينك ده — رابط ثابت بسيط زي رابط "Profile"/"Logout".

## سجل الأجزاء (تابع)

### Part 35 — قائمة To-Do للمدرس والطالب
الحالة: تم
تفاصيل:
- ضفت موديل `GroupTodoItem` في `groups/models.py` (آخر موديل في
  الملف، بعد `GroupAssignmentSubmission` من Part 33) بالحقول المطلوبة
  بالظبط (`owner`, `group`, `title`, `notes`, `due_at`, `is_done`,
  `created_at`) — تفاصيل القرارات فوق. **باقي الملف متلمسش خالص.**
- عملت migration جديدة `groups/migrations/0016_grouptodoitem.py`
  (`CreateModel` بسيط)، بتعتمد على `('groups',
  '0015_groupassignment_groupassignmentsubmission')` (آخر migration
  معروفة حسب النسخة الحقيقية اللي بعتها Ahmed). ⚠️ نفس تحذير كل
  migration مكتوبة يدويًا في المشروع: لازم تتأكد بـ
  `makemigrations --check --dry-run` فعليًا على السيرفر قبل `migrate`،
  لو فيه migration أحدث مش موثقة هنا.
- سجّلت الموديل في `groups/admin.py` (`GroupTodoItemAdmin`) — نفس نمط
  التسجيل البسيط المتبع في باقي موديلات `groups`، مع `list_editable`
  على `is_done` (نفس فلسفة `GroupLessonAdmin.is_published` من Part 27)
  لتسهيل المراجعة/الإشراف من الأدمن. **باقي الملف متلمسش خالص.**
- عملت ملف جديد `groups/views_todo.py` (نفس القرار التنظيمي المتبع في
  Part 28/32/34) فيه view-ين:
  - `my_todo_list(request)`: `login_required` بس (بدون فحص role) —
    GET بيعرض القايمة (معلّقة + مخلّصة)، POST بيتعامل مع فورم الإضافة
    السريع (`title` إجباري، `due_at` اختياري).
  - `toggle_todo_done(request, todo_id)`: `login_required` +
    `require_POST`، AJAX endpoint بيبدّل `is_done` مع تحقق ownership
    صارم (404 لو مش بتاعة المستخدم الحالي)، بيرجع `JsonResponse`.
  تفاصيل كاملة فوق في "قرارات معمارية". **`groups/views.py` متلمسش
  خالص** — الملف ده مالوش أي علاقة بالجزء ده.
- عدّلت `groups/urls.py`: ضفت `from . import views_todo` ومسارين
  جديدين (`my-todo/` → `my_todo_list`، `todo/<int:todo_id>/toggle/` →
  `toggle_todo_done`)، قبل الـ pattern العام `<int:group_id>/` في آخر
  الملف. باقي الملف متلمسش خالص.
- أنشأت `groups/templates/groups/my_todo_list.html` (صفحة مستقلة كاملة،
  نفس نظام "Obsidian Academy") و`groups/templates/groups/_todo_row.html`
  (جزئي `{% include %}` لصف المهمة الواحدة) — تفاصيل التصميم والـ JS
  كاملة فوق في "قرارات معمارية"، قسم 6/7.
- عدّلت `groups/templates/groups/dashboard.html`: لينك "مهامي" جديد في
  الـ nav-links بس. باقي الملف متلمسش خالص.
- عدّلت `groups/templates/groups/my_learning_groups.html`: نفس الفكرة
  — لينك "مهامي" جديد في الـ nav-links بس. باقي الملف متلمسش خالص.
- اتفحص syntax كل ملفات Python الجديدة/المعدّلة (`python -m py_compile`
  على `models.py`/`admin.py`/`views_todo.py`/`urls.py`/الـ migration) —
  عدّت كلها من غير أخطاء. اتفحص توازن `{% if/for %}` ↔ `{% endif/endfor %}`
  في الأربع تمبلتس (الاتنين الجداد + `dashboard.html` و
  `my_learning_groups.html` المعدَّلين) — كلهم متطابقين.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مستخدم (مدرس أو طالب) يفتح "مهامي" → يكتب عنوان مهمة ويحدد ميعاد
  اختياري → يضغط "إضافة" → المهمة تظهر في قسم "المعلّقة" → يضغط دائرة
  التحديد جنبها → بدون أي reload، الصف بيتنقل لقسم "مهام خلّصتها"
  والعداد بيتحدّث في القسمين. مستخدم يحاول يعمل POST مباشر لـ
  `toggle_todo_done` بـ `todo_id` بتاع مستخدم تاني → 404.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. **الأهم**: migration الجديدة (`0016_grouptodoitem.py`) بتفترض إن
     `0015_groupassignment_groupassignmentsubmission` (Part 33) هي آخر
     migration في تطبيق `groups` — لازم تتأكد بـ
     `makemigrations --check --dry-run` فعليًا على السيرفر قبل `migrate`.
  2. فورم الإضافة السريع مالوش اختيار جروب أو حقل `notes` (البرومبت
     حدد صراحة "title + due_at اختياري" بس) — لو Ahmed عايز يقدر يربط
     مهمة بجروب معين أو يكتب ملاحظات من نفس الفورم السريع، ده تحسين
     منفصل سهل الإضافة.
  3. الملاحظة اللي في `views.py` (الملف اللي بعته Ahmed في الجلسة دي)
     بخصوص `my_learning_groups`/`teacher_groups_dashboard` — النسخة دي
     من `views.py` **مفيهاش** كود Part 32 (`upcoming_schedule_items`)
     رغم إن التمبلتس (`dashboard.html`/`my_learning_groups.html`)
     فيها `{% if upcoming_schedule_items %}` جاهزة لعرضه. ده مش
     متعلق بالجزء ده (35) خالص ومحدش لمسه هنا — بس التمبلتس هتفضل
     تتعامل معاه بأمان (الشرط `{% if %}` بيمنع أي خطأ، القسم ببساطة
     مش هيظهر لحد ما الـ context يترجع لـ `views.py`). لو ده تراجع غير
     مقصود لكود Part 32، يستاهل مراجعة منفصلة برة نطاق Part 35.
  4. مهام متأخرة (`due_at` فات) بتتلوّن بصريًا بس دلوقتي — التمييز
     الكامل المطلوب رسميًا (badge واضح + عدم إخفاء/حذف) هو موضوع
     Part 36 نفسه، فالتلوين هنا مجرد بداية بسيطة، مش تنفيذ كامل للمتطلب.

### ✅ تأكيد فعلي على سيرفر Ahmed
- `python manage.py showmigrations groups` أكّد إن
  `0015_groupassignment_groupassignmentsubmission` كانت فعلاً آخر
  migration مطبّقة قبل الجزء ده — مفيش أي migration وسيطة مفقودة،
  فـ `dependencies` بتاعة `0016` كانت صحيحة من غير أي تعديل مطلوب.
- `python manage.py makemigrations --check --dry-run` رجع من غير أي
  تحذير غير متوقع متعلق بـ `grouptodoitem`.
- `python manage.py migrate groups` طبّق `groups.0016_grouptodoitem`
  بنجاح.
- `python manage.py check` رجع "System check identified no issues".
- اختبار يدوي فعلي على المتصفح: فتح `/groups/my-todo/` بمستخدم مدرس
  وبمستخدم طالب، إضافة مهمة من غير ميعاد وظهورها في "المعلّقة"، إضافة
  مهمة بميعاد في الماضي وظهور تلوين التنبيه، تبديل حالة "تم" عن طريق
  الدائرة ونقل الصف فعليًا بين "المعلّقة" و"مهام خلّصتها" **من غير أي
  إعادة تحميل للصفحة** (اتأكد عن طريق الـ Network tab إن الطلب `fetch`
  بس)، الرجوع لحالة "معلّقة" تاني بنفس الطريقة، ظهور المهام وقابلية
  تعديل `is_done` مباشرة من `/admin/groups/grouptodoitem/`، وظهور لينك
  "مهامي" في الـ navbar من `dashboard.html` (مدرس) و
  `my_learning_groups.html` (طالب) — كله اتأكد شغال بنجاح.

**Part 35 شغال فعليًا 100% على السيرفر دلوقتي.**

## قرارات معمارية اتاخدت (Part 36)

### 1) نفس نمط Part 16 بالحرف — فلاج واحد + helper + task دورية

كررت نفس بنية `send_subscription_expiry_reminders` (Part 16) بالظبط:
فلاج واحد (`reminder_sent` على `GroupTodoItem`) بيمنع تكرار الإرسال،
دالة داخلية منفصلة (مش `@shared_task`) لبناء وإرسال الإيميل
(`_send_todo_reminder_email`)، وتاسك دورية (`@shared_task`) بتفلتر
وترسل مع `try/except` لكل مهمة على حدة — لو فشل تذكير مهمة واحدة، باقي
المهام المستحقة في نفس التشغيلة بتكمل عادي وميتأثروش.

### 2) نافذة "قريب" = ساعة واحدة قدام (زي نافذة الـ 3 أيام في Part 16)

فسّرت "معادها قريب (خلال ساعة مثلاً)" بنفس فلسفة Part 16 بالظبط:
`0 < due_at - الآن <= ساعة` (يعني `due_at__gt=الآن` و
`due_at__lte=الآن+ساعة`). مهمة فات معادها بالفعل (`due_at` في الماضي)
**مش بتاخد تذكير جديد هنا** — دي حالتها "متأخرة" (overdue) وليها تمييز
بصري منفصل (badge/لون مختلف) في `my_todo_list.html`، مش تذكير بالإيميل؛
والتمييز البصري ده كان أصلاً متطبق بالكامل من Part 35
(`.todo-row.is-overdue` + `.overdue-tag` في `_todo_row.html`) — يعني
متطلب رقم 3 من نص الجزء ده كان محقق بالفعل قبل ما نوصل لـ Part 36
رسميًا، فمفيش أي تعديل على التمبلتس مطلوب في الجزء ده.

### 3) دورية التاسك: كل 10 دقايق

اخترت 10 دقايق بنفسي (مفيش تحديد صريح في الطلب الأصلي غير "مثلاً" لكل
من النافذة والدورية) — توازن بين إن المهمة تاخد تذكيرها قريب من لحظة
دخولها نافذة الساعة، ومعدل استعلامات معقول. القيمة دي أوسع شوية من
الـ 5 دقايق المستخدمة في نشر الدروس (Part 31) عمدًا — هناك التوقيت
الدقيق أهم لأن الدرس نفسه المفروض ينزل فعليًا في وقته، هنا التذكير مجرد
تنبيه استباقي فمساحة تأخير أوسع شوية مقبولة. مفيش أي تعارض في
التوقيتات مع تاسكات groups التانية (2 ص للتجميد، 9 ص للتنبيهات، كل 5
دقايق لنشر الدروس) — كل التاسكات دي وقتها بيتحدد بالكرون تعبير الخاص
بيها بشكل مستقل.

### 4) نظام الإشعارات: نفس `send_mail` البسيط، مفيش موديل إشعارات جديد

زي ما اتطلب صراحة ("نفس نظام الإشعارات") — نفس أسلوب
`_send_expiry_reminder_email` (Part 16) و`_notify_group_members_new_lesson`
(Part 31) بالحرف: `django.core.mail.send_mail` نص عادي (plain text)،
لو `owner.email` فاضي بيتسجّل تحذير (`logger.warning`) ويتخطى بدل ما
يوقف التاسك كله. الإيميل بيعرض عنوان المهمة، اسم الجروب (لو المهمة
مرتبطة بجروب)، الميعاد، والملاحظات (لو موجودة).

### 5) مفيش فحص `is_group_content_accessible` هنا

المهمة (`GroupTodoItem`) ملكها `owner` واحد بس، وهي شخصية بالكامل حتى
لو مرتبطة بجروب (`group` اختياري من Part 35) — فمفيش أي علاقة بمنطق
صلاحيات محتوى الجروب (`is_group_content_accessible`) المستخدم في باقي
أجزاء المرحلة الثانية. التذكير بيتبعت لصاحب المهمة بغض النظر عن حالة
الجروب المرتبط بيها (لو موجود).

### 6) الأدمن: `reminder_sent` زيادة بسيطة في `list_display`/`list_filter`

زودت `reminder_sent` في `GroupTodoItemAdmin` (زيادة عن المطلوب صراحة في
نص الجزء، بنفس نمط إضافات بسيطة سابقة زي `chat_mode`/`message_type` في
أجزاء تانية) عشان الأدمن يقدر يراجع بسهولة أي مهام اتبعتلها تذكير
بالفعل. سهل تتشال لو مش لازمة.

## سجل الأجزاء (تابع)

### Part 36 (المرحلة الثانية) — تذكيرات المهام (Celery + نفس نظام الإشعارات)
الحالة: تم — ⚠️ لسه محتاج تشغيل `makemigrations --check --dry-run` +
`migrate` فعليًا على السيرفر (تفاصيل تحت).
تفاصيل:
- ضفت حقل `reminder_sent = models.BooleanField(default=False)` على
  `GroupTodoItem` في `groups/models.py` (Part 35) — تفاصيل القرار فوق.
  **باقي الملف (كل الموديلات التانية) متلمسش خالص.**
- عملت migration جديدة
  `groups/migrations/0017_grouptodoitem_reminder_sent.py` (`AddField`
  بسيط)، بتعتمد على `('groups', '0016_grouptodoitem')` (آخر migration
  معروفة حسب النسخة الحقيقية اللي بعتها Ahmed). ⚠️ نفس تحذير كل
  migration مكتوبة يدويًا في المشروع: لازم تتأكد بـ
  `makemigrations --check --dry-run` فعليًا على السيرفر قبل `migrate`.
- عدّلت `groups/tasks.py`:
  - ضفت `GroupTodoItem` لاستيراد الموديلات الموجود فوق.
  - دالة جديدة `_send_todo_reminder_email(todo)` (helper داخلي بس، مش
    `@shared_task`) — تفاصيل فوق، قسم 4.
  - تاسك جديدة `@shared_task def send_todo_reminders()` — تفاصيل
    الفلتر والمنطق الكامل فوق، أقسام 1/2. **باقي الملف (كل التاسكات
    التانية من Part 15/16/31/34) متلمسش خالص.**
- عدّلت `Eduvia/celery.py`: ضفت entry جديدة في `beat_schedule` باسم
  `'send-todo-reminders'`، بتستدعي `'groups.tasks.send_todo_reminders'`
  كل 10 دقايق (`crontab(minute='*/10')`) — تفاصيل فوق، قسم 3. **باقي
  الملف متلمسش خالص.**
- عدّلت `groups/admin.py::GroupTodoItemAdmin`: ضفت `reminder_sent` في
  `list_display` و`list_filter` — تفاصيل فوق، قسم 6. **باقي الملف
  متلمسش خالص.**
- **مفيش أي تعديل على `groups/views_todo.py`، `groups/urls.py`،
  `my_todo_list.html`، أو `_todo_row.html`** — التمييز البصري للمهام
  المتأخرة (متطلب 3) كان أصلاً متطبق بالكامل من Part 35
  (`.todo-row.is-overdue` + `.overdue-tag`)، فمفيش أي تعديل مطلوب على
  أي تمبلت في الجزء ده.
- اتفحص syntax كل ملفات Python المعدّلة/الجديدة (`python -m py_compile`
  على `models.py`/`tasks.py`/`admin.py`/`celery.py`/الـ migration) —
  عدّت كلها من غير أخطاء.
- اختبرت (منطقيًا عن طريق قراءة الكود، مفيش سيرفر فعلي هنا) السيناريو:
  مستخدم يضيف مهمة بميعاد بعد 40 دقيقة من دلوقتي → التاسك يشتغل (خلال
  أول 10 دقايق بعد الإضافة أو أي تشغيلة بعدها) → المهمة داخل نافذة
  الساعة → `_send_todo_reminder_email` بتبعت الإيميل → `reminder_sent`
  بيتحط `True` → لو التاسك اشتغل تاني بعد كده لنفس المهمة (لسه في نفس
  الساعة)، الفلاج بيمنع أي إرسال تاني. مهمة `due_at` بتاعها فات من ساعتين
  ولسه `is_done=False` → مش بتاخد أي تذكير جديد (خارج نافذة الساعة
  الأمامية)، لكن بتفضل تتعرض بلون/badge "متأخرة" في `my_todo_list.html`
  زي ما هي من Part 35.
- ⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
  1. **الأهم**: migration الجديدة (`0017_grouptodoitem_reminder_sent.py`)
     بتفترض إن `0016_grouptodoitem` (Part 35) هي آخر migration في
     تطبيق `groups` — لازم تتأكد بـ `makemigrations --check --dry-run`
     فعليًا على السيرفر قبل `migrate`.
  2. نافذة "قريب" (ساعة واحدة قدام) ودورية التاسك (كل 10 دقايق) اخترتهم
     بنفسي — مفيش تحديد صريح في الطلب الأصلي غير "مثلاً". سهل التعديل
     في `groups/tasks.py` (رقم الساعة) و`Eduvia/celery.py` (الكرون) لو
     Ahmed عايز قيم مختلفة.
  3. مفيش تذكير تاني لو المهمة اتعدّل ميعادها (`due_at`) بعد ما
     `reminder_sent` بقت `True` (مثلاً المستخدم أجّل المهمة لميعاد
     تاني بعيد، وبعدين قرّبها تاني) — الفلاج مش بيترجع `False` تلقائيًا
     عند تعديل `due_at` (مفيش view تعديل `due_at` أصلاً موجودة لسه في
     المشروع، الفورم السريع من Part 35 بيدعم إضافة بس مش تعديل). لو
     Ahmed عايز يضيف view تعديل مستقبلاً، هيحتاج ريسيت `reminder_sent`
     لـ `False` عند أي تعديل على `due_at`.
  4. الإيميل بيتبعت نص عادي (plain text) مش HTML — نفس كل تذكيرات
     المشروع التانية (Part 16/31/34)، لو عايز شكل HTML موحّد لكل
     الإشعارات، ده تحسين منفصل أكبر من نطاق الجزء ده.

### ✅ تأكيد فعلي على سيرفر Ahmed

- `python manage.py makemigrations --check --dry-run` رجع بس نفس
  الملاحظة التجميلية المعروفة من الأجزاء اللي فاتت (توحيد نوع حقل `id`
  لـ `BigAutoField` — الاقتراح `0018_alter_..._id_and_more` شمل
  `grouptodoitem` ضمنيًا بنفس السبب، مفيش أي فعل مطلوب).
- `python manage.py migrate groups` طبّق `groups.0017_grouptodoitem_reminder_sent`
  بنجاح ("OK").
- `python manage.py check` رجع "System check identified no issues".
- الـ beat process شغّل التاسك فعليًا في معاده بالظبط
  (`Scheduler: Sending due task send-todo-reminders
  (groups.tasks.send_todo_reminders)`) كل 10 دقايق، والـ worker استلمها
  ونفّذها ورجّع نتيجة (`send_todo_reminders: sent 0 reminder(s)` وقت ما
  مكانش فيه مهمة مستحقة فعليًا) — الـ pipeline الدوري كامل شغال من غير
  أي تدخل يدوي.
- اختبار يدوي فعلي كامل من `manage.py shell`:
  1. مهمة تجريبية بـ `due_at` فات معادها بالفعل (بثانية واحدة) →
     `send_todo_reminders()` رجعت `sent 0 reminder(s)` — سلوك متوقع
     ومقصود (مهمة فايتة معادها بقت "متأخرة" مش "قريبة"، تفاصيل القرار
     في "قرارات معمارية" فوق).
  2. نفس المهمة بعد ما اتحدّث `due_at` لبعد 10 دقايق من دلوقتي (و
     `reminder_sent` اتحطت `False`) → `send_todo_reminders()` رجعت
     `sent 1 reminder(s)`.
  3. **الإيميل وصل فعليًا** لصاحب المهمة.
  4. `send_todo_reminders()` اتشغلت تاني على طول من غير أي تعديل →
     رجعت `sent 0 reminder(s)` — **فلاج `reminder_sent` بيمنع التكرار
     فعليًا ومتأكد منه**.

**Part 36 شغال فعليًا 100% على السيرفر دلوقتي — الفلاج، التاسك، الجدولة
الدورية (beat + worker مع بعض)، والإرسال الفعلي بالإيميل، كلهم متأكد
منهم بالكامل.**

# إضافة على PROGRESS — Part 37 (المرحلة الثانية)
### (هذا القسم فقط يُلصق في نهاية PROGRESS_PART22.md الحالي — مش ملف بديل)

## ⚠️ ملاحظة مهمة عن نطاق التنفيذ الفعلي في الجلسة دي

Part 37 المفروض يغطي **كل** صفحات المرحلة الثانية (اللايف، الدروس،
الشات، الجدول، الواجبات، مهامي، الأعضاء). في الجلسة دي اتبعتلي بس 7
ملفات فعلية من أصل أكتر من 20 ملف مرتبط بالجزء ده (`views.py`،
`urls.py`، `group_detail.html`، `group_assignments_list.html`،
`create_group_assignment.html`، `grade_submissions.html`، بالإضافة
لملفات مرجعية مش فيها نمط تابات جاهز: `course_details.html`،
`course_curriculum.html`، `create_group.html`، `dashboard.html`،
`create_live_session.html`، `_todo_row.html`).

عشان كده التنفيذ الفعلي في الجلسة دي **مقصور** على:
1. بناء الكومبوننت المشترك (`_group_tabs.html`) — شريط التابات الموحّد.
2. تطبيقه على الملفات اللي كانت متاحة فعليًا: `group_detail.html`،
   `group_assignments_list.html`، `create_group_assignment.html`،
   `grade_submissions.html`.
3. إضافة تاب/صفحة "الأعضاء" الجديدة بالكامل (view + url + template) —
   دي كانت مش موجودة خالص قبل كده في أي جزء سابق.

**باقي صفحات الجروب (اللايف، الدروس، الجدول، مكتبة التسجيلات، مهامي)
لسه محتاجة نفس المعالجة في جلسة تانية** بعد ما تتبعت ملفاتها الفعلية —
تفاصيل كاملة في قسم "حاجات ناقصة" تحت.

## قرارات معمارية اتاخدت (Part 37)

### 1) مفيش نمط تابات/سايدبار جاهز في المشروع — كومبوننت جديد اتصمم

راجعت `course_details.html` و`course_curriculum.html` (الملفين المرجعيين
اللي بعتهملي Ahmed) بحثًا عن أي نمط تابات/سايدبار موجود بالفعل زي ما
اتطلب صراحة في نص الجزء ("استخدم نفس نمط التابات أو السايدبار المستخدم
في مكان تاني بالمشروع لو موجود... بدل ما تخترع باترن جديد"). النتيجة:
**مفيش أي نمط تابات أو سايدبار في أي مكان في المشروع** — صفحات الكورس
بتستخدم accordion بسيط (`.curr-section` قابلة للطي/الفتح) مش تابات
تنقل بين صفحات مختلفة. بما إن مفيش حاجة جاهزة نتبعها، صممت كومبوننت
جديد (`.group-tabs`/`.group-tab`) بنفس الـ CSS variables والـ tokens
الموجودة بالفعل في نظام "Obsidian Academy" (نفس ألوان الأزرار، نفس
`border-radius`، نفس `transition`) — قرار موثق هنا صراحة زي ما اتفقنا
بدل ما يتفرض بصمت.

### 2) Include واحد مشترك (`_group_tabs.html`) بدل تكرار HTML في كل صفحة

بدل ما أكرر نفس الـ 8 روابط في كل تمبلت من تمبلتات الجروب (أكتر من 15
ملف عبر كل أجزاء 22-36)، عملت `{% include %}` واحد
(`groups/templates/groups/_group_tabs.html`) بيتكرر جوه أي صفحة محتاجة
شريط التابات. المتطلب الوحيد من الـ context: متغير `group` (موجود
بالفعل في كل صفحات الجروب من غير استثناء)، و`is_owner` اختياري (لو مش
موجود، تاب "الأعضاء" مايظهرش تلقائيًا من غير أي خطأ — Django بيتعامل مع
متغير مش موجود في `{% if %}` كـ False بهدوء).

### 3) "التاب النشط" بيتحدد من `request.resolver_match.url_name` — من غير أي تعديل على أي view موجودة

بدل ما أضيف متغير `active_tab` يدوي في context كل view (وده كان
هيحتاج تعديل على عشرات الـ views عبر `views.py`/`views_lessons.py`/
`views_schedule.py`/`views_assignments.py`/`views_todo.py`)، استخدمت
`request.resolver_match.url_name` (متاح تلقائيًا لأي request عادي، وده
context processor الـ `request` أصلاً مفعّل ومستخدم بالفعل في كل
تمبلتات groups لـ `request.user`/`request.build_absolute_uri`). يعني
الكومبوننت بيشتغل صح على أي صفحة اتضاف فيها الـ include من غير أي حاجة
إضافية مطلوبة من الـ view نفسها — أنضف تقنيًا وأقل عرضة للنسيان من
تمرير متغير يدوي في كل مكان.

### 4) تاب "الشات" بيودّي لـ `group_detail#chat-section` — مفيش صفحة منفصلة

الشات (Part 14) لسه جوه `group_detail.html` نفسها، مفيش أي URL منفصل
ليه (نفس القرار الأصلي من Part 14 لسه صالح). فتاب "الشات" بيودّي
لـ `{% url 'groups:group_detail' group_id=group.id %}#chat-section`،
وضفت `id="chat-section"` حوالين قسم الشات في `group_detail.html` عشان
المتصفح يعمل scroll تلقائي للقسم ده. "نظرة عامة" و"الشات" بيبانوا
"active" مع بعض وهما فعليًا على نفس الصفحة — مش تفرقة مصطنعة، هما نفس
الصفحة بالظبط.

### 5) تاب "اللايف" بيضم قسم البث + مكتبة التسجيلات مع بعض

بدل ما يكون فيه تاب منفصل لكل من "البث المباشر" و"مكتبة التسجيلات"،
دمجتهم في تاب واحد ("اللايف") بيودّي لـ `group_detail#live-section` —
القسم ده (اللي لفيته بـ `<div id="live-section">`) بيشمل: حالة البث
الحالي/المجدول (Part 24) + قايمة "لايفات محتاجة رفع تسجيل" (Part 26)،
وبداخله زرار "مكتبة التسجيلات" لسه موجود زي ما كان. القرار ده منطقي —
التسجيلات هي VOD لنفس جلسات اللايف، مش موضوع منفصل تمامًا.

### 6) إزالة الروابط المكررة (الدروس/الجدول/الواجبات) من `group_detail.html`

قبل الجزء ده، `group_detail.html` كان فيه 4 أزرار "أشباح" منفصلة
(مكتبة التسجيلات، الدروس المسجلة، الجدول القادم، الواجبات) اتضافوا في
Part 26/28/32/34 بالتتابع. بعد ما شريط التابات بقى موجود فوق الصفحة
كلها ومغطي نفس الوجهات بالظبط (الدروس المسجلة، الجدول القادم،
الواجبات)، الأزرار التلاتة دي بقوا تكرار بصري حقيقي لنفس الرابط في نفس
الصفحة — اتشالوا. **الروابط نفسها (URL names) متلمسوش خالص**، التعديل
كله بصري (شيل عناصر HTML مكررة)، مفيش أي مسار جديد أو محذوف. زرار
"مكتبة التسجيلات" لوحده فضل موجود (مش مكرر مع أي تاب مستقل — مدموج في
تاب "اللايف" نفسه، قرار 5 فوق).

### 7) صفحة "الأعضاء" جديدة بالكامل — مش كانت موجودة قبل كده

راجعت `urls.py`/`views.py` القديمة قبل أي إضافة — مفيش أي view أو مسار
بيعرض قايمة أعضاء الجروب في أي جزء سابق من المرحلة الثانية أو الأولى.
بما إن نص Part 37 بيطلب صراحة تاب "الأعضاء (تظهر للمدرس بس)"، عملت:
- `groups/views.py::group_members(request, group_id)` — محمية بـ
  `@instructor_required` + `_get_owned_group_or_403` (نفس نمط
  `create_live_session`/`live_broadcast` من Part 24 بالحرف؛ الـ helper
  ده كان موجود بالفعل من Part 24، استخدمته مباشرة من غير تكرار). بترجع
  كل `GroupMembership` بتاعة الجروب (موديل موجود من Part 5، مفيش أي
  migration جديدة مطلوبة) مرتبة بالأحدث انضمامًا أول.
- مسار جديد في `urls.py`: `<int:group_id>/members/` باسم
  `group_members` — مركّب من أكتر من segment، فمش بيتعارض مع الـ
  pattern العام `<int:group_id>/` في آخر الملف حتى لو اتحط قبله.
- تمبلت جديد `groups/templates/groups/group_members.html` — نفس هيكل
  `assignment-row` من `group_assignments_list.html` (Part 34) بس لكل
  عضو بدل كل واجب: أفاتار دائري بحرف أول اسم الطالب، الاسم، الإيميل،
  وتاريخ الانضمام. `empty-state` لو لسه محدش انضم.

### 8) "مهامي" (my_todo_list) — تاب فيه، لكن مفهاش شريط تابات هو نفسه

`my_todo_list` صفحة عامة مش مرتبطة بجروب معين (مفيش `group_id` في
مسارها من الأساس — بتجمع مهام المستخدم عبر كل الجروبات). عشان كده تاب
"مهامي" بيظهر في شريط تابات أي جروب (كرابط خروج من سياق الجروب الحالي
لصفحة عامة)، لكن `my_todo_list.html` نفسها **مش** هتاخد نسخة من شريط
التابات ده (مفيش `group` واحد محدد في سياقها أصلاً). التفصيل ده مش
اتنفذ في الجلسة دي لأن `my_todo_list.html` مكانتش من ضمن الملفات
المبعوتة — هيتراجع في الجلسة الجاية.

## سجل الأجزاء

### Part 37 — مركز تنقل موحّد داخل الجروب (تابات تربط كل حاجة)
الحالة: **جزئي** — الكومبوننت المشترك (`_group_tabs.html`) والصفحات
الأساسية (`group_detail.html` + 3 تمبلتات واجبات) والـ backend
(`group_members`) خلصوا وشغالين. باقي صفحات الجروب (اللايف، الدروس،
الجدول، مكتبة التسجيلات، مهامي) لسه محتاجة نفس المعالجة — تفاصيل تحت.

تفاصيل الشغل اللي اتعمل فعليًا:
- عملت `groups/templates/groups/_group_tabs.html` (include مشترك) —
  8 تابات: نظرة عامة، اللايف، الدروس المسجلة، الجدول القادم، الشات،
  الواجبات، مهامي، الأعضاء (owner بس). التاب النشط بيتحدد تلقائيًا من
  `request.resolver_match.url_name` من غير أي تعديل على أي view
  موجودة. تفاصيل كاملة فوق في "قرارات معمارية".
- ضفت view جديدة `group_members` في `groups/views.py` (بعد
  `toggle_chat_mode`، قبل `group_detail`) — تفاصيل فوق، قرار 7.
  **باقي الملف (كل الـ views من Part 7 لحد Part 34) متلمسش خالص.**
- ضفت مسار جديد `<int:group_id>/members/` في `groups/urls.py` (قبل الـ
  pattern العام `<int:group_id>/` في آخر الملف). **باقي الملف متلمسش
  خالص.**
- عملت تمبلت جديد `groups/templates/groups/group_members.html`.
- عدّلت `groups/templates/groups/group_detail.html`:
  - CSS جديد بس (`.group-tabs`, `.group-tab`, `.group-tab.active`) —
    إضافة، مفيش أي حذف لأي كلاس موجود.
  - `{% include 'groups/_group_tabs.html' %}` بعد هيدر الجروب مباشرة.
  - `id="live-section"` حوالين قسم البث المباشر + مكتبة التسجيلات
    (يقفل قبل قسم "جلسات لايف شغالة دلوقتي" القديم — النظام القديم
    workshops.LiveSession **متلمسش خالص**، مش جزء من `live-section`).
  - `id="chat-section"` حوالين قسم الشات الجماعي.
  - **اتشالت** 3 أزرار أشباح مكررة (الدروس المسجلة، الجدول القادم،
    الواجبات) — بقوا مغطيين بالكامل بالتابات الجديدة. تفاصيل فوق، قرار
    6. زرار "مكتبة التسجيلات" فضل موجود زي ما هو (جوه `live-section`).
  - باقي الملف (الشات نفسه، إدارة الجلسات، جلسات workshops القديمة)
    **متلمسش خالص**.
- عدّلت `groups/templates/groups/group_assignments_list.html`،
  `groups/templates/groups/create_group_assignment.html`،
  `groups/templates/groups/grade_submissions.html`: نفس CSS
  `.group-tabs`/`.group-tab` + `{% include 'groups/_group_tabs.html' %}`
  بعد الـ breadcrumb مباشرة. باقي الثلاث ملفات **متلمستش خالص** — لسه
  فيهم breadcrumb يرجّع للمستوى الأب (قايمة الواجبات) + نav-link "صفحة
  الجروب" في التوبار (كان موجود بالفعل من الأجزاء السابقة)، فمتطلب
  "رابط واضح يرجّع لصفحة تفاصيل الجروب" (نقطة 2 في نص الجزء) محقق من
  غير أي تعديل إضافي.
- اتفحص syntax (`python -m py_compile` على `views.py`/`urls.py`) —
  عدّى من غير أخطاء. اتفحص توازن `{% if/for %}` ↔ `{% endif/endfor %}`
  في كل التمبلتات المعدّلة/الجديدة (`group_detail.html`: 43/43،
  `group_assignments_list.html`: 15/15، `create_group_assignment.html`:
  4/4، `grade_submissions.html`: 12/12) — كلهم متطابقين.

### ⚠️ حاجات ناقصة — محتاجة استكمال في جلسة تانية

الملفات دي **لسه محتاجة** نفس المعالجة (إضافة `{% include
'groups/_group_tabs.html' %}` + CSS الخاصة بالتابات + breadcrumb
واضح يرجّع لـ `group_detail` لو مش موجود بالفعل):

1. `groups/templates/groups/live_broadcast.html` (Part 24)
2. `groups/templates/groups/watch_live_session.html` (Part 25)
3. `groups/templates/groups/upload_group_lesson.html` (Part 28)
4. `groups/templates/groups/group_lessons_list.html` (Part 28)
5. `groups/templates/groups/watch_group_lesson.html` (Part 28)
6. `groups/templates/groups/group_schedule.html` (Part 32)
7. `groups/templates/groups/submit_group_assignment.html` (Part 34)
8. `groups/templates/groups/upload_group_recording.html` (Part 26)
9. `groups/templates/groups/group_recordings.html` (Part 26)
10. `groups/templates/groups/watch_group_recording.html` (Part 26)
11. `groups/templates/groups/my_todo_list.html` (Part 35) — دي حالة
    خاصة (تفاصيل فوق، قرار 8): مش هتاخد شريط التابات نفسه (مفيش
    `group` واحد في سياقها)، بس محتاجة رابط "رجوع" واضح (مثلاً لصفحة
    Home أو `document.referrer` بسيط) بدل ما تفضل بلا أي مخرج واضح.

بعد ما الملفات دي تتبعت، خطوة أخيرة (النقطة 3 في نص الجزء الأصلي):
مراجعة شاملة إن كل الروابط الداخلية اللي اتعملت من Part 22 لحد Part 36
شغالة ومربوطة صح من الأماكن الجديدة (التابات) — مراجعة أولية اتعملت
هنا على أسماء الـ URL نفسها (مقارنة مباشرة مع `urls.py`)، لكن التأكيد
الكامل محتاج باقي الملفات فوق.

# إضافة على PROGRESS — استكمال Part 37 (المرحلة الثانية)
### (هذا القسم يُلصق بعد قسم "Part 37 — مركز تنقل موحّد داخل الجروب" الموجود
### بالفعل في PROGRESS_PART22.md — بيكمّله ويحدّث حالته لـ "تم"، مش قسم بديل)

## ⚠️ نطاق التنفيذ الفعلي في الجلسة دي

في الجلسة اللي فاتت اتنفذ الكومبوننت المشترك (`_group_tabs.html`) وتطبيقه
على 4 ملفات بس (`group_detail.html`، `group_assignments_list.html`،
`create_group_assignment.html`، `grade_submissions.html`) + صفحة
"الأعضاء" الجديدة بالكامل (view + url + template).

في الجلسة دي اتبعتلي الملفات العشرة الباقية + `my_todo_list.html` +
`views.py`/`urls.py`/`views_lessons.py`/`views_schedule.py`/
`views_assignments.py`/`views_todo.py` كمرجع للتأكد من الـ context.
راجعت الملفات دي فعليًا قبل أي تعديل (مش من الذاكرة) للتأكد إن كل view
فيها فعلاً بتمرر `group` في الـ context (شرط أساسي لشغل الـ include) —
تأكدت بالـ grep المباشر على `views.py` إن كل الـ views دي بترجع `group`:
`create_live_session`، `live_broadcast`، `end_live_session`،
`join_live_session`، `group_recordings`، `watch_group_recording`،
`upload_group_recording`، وبرضه `group_lessons_list`/`watch_group_lesson`
(`views_lessons.py`)، `group_schedule` (`views_schedule.py`)،
`submit_group_assignment` (`views_assignments.py`).

## تفاصيل الشغل اللي اتعمل في الجلسة دي

### 1) تطبيق الـ include + الـ CSS على العشرة ملفات الباقية

لكل ملف من العشرة دول: ضفت نفس CSS بتاعة `.group-tabs`/`.group-tab`/
`.group-tab.active` (نفس القيم بالحرف اللي كانت اتحطت في `group_detail.html`
وباقي الملفات الأربعة من الجلسة اللي فاتت) في آخر `<style>` الصفحة، وضفت
`{% include 'groups/_group_tabs.html' %}` مباشرة بعد الـ `breadcrumb-link`
الموجود أصلاً في كل صفحة (كلهم كان عندهم breadcrumb بالفعل — مفيش أي حالة
احتجت "أول content-wrap" كـ fallback):

1. `groups/templates/groups/live_broadcast.html`
2. `groups/templates/groups/watch_live_session.html`
3. `groups/templates/groups/upload_group_lesson.html`
4. `groups/templates/groups/group_lessons_list.html`
5. `groups/templates/groups/watch_group_lesson.html`
6. `groups/templates/groups/group_schedule.html`
7. `groups/templates/groups/submit_group_assignment.html`
8. `groups/templates/groups/upload_group_recording.html`
9. `groups/templates/groups/group_recordings.html`
10. `groups/templates/groups/watch_group_recording.html`

**مفيش أي تعديل تاني** على أي ملف من دول — الـ backend (`groups/views.py`،
`groups/views_lessons.py`، `groups/views_schedule.py`،
`groups/views_assignments.py`) **متلمسش خالص**، ومفيش أي migration.

### 2) `_group_tabs.html` — استُبدلت أول نسخة (مُعادة البناء) بالنسخة الحقيقية

أول نسخة من `_group_tabs.html` بُنيت من الوصف الموثق في PROGRESS (لإن
الملف الحقيقي ماكانش وصلني في أي جلسة سابقة). Ahmed بعت النسخة الحقيقية
الفعلية بعد كده، فاستبدلت الملف بالكامل بيها — **الملف المرفق دلوقتي هو
النسخة الحقيقية بالحرف** (75 سطر)، مش النسخة المُعادة البناء (كانت 57
سطر). الفروق الجوهرية اللي كانت في نسختي القديمة واتصلحت بالاستبدال:
- استخدام `{% with url_name=request.resolver_match.url_name %}` بدل
  تكرار `request.resolver_match.url_name` في كل شرط — نفس النتيجة
  منطقيًا، بس أنضف وأداء أفضل شوية (تقييم واحد بدل تكراره 9 مرات).
- `<nav class="group-tabs" aria-label="أقسام الجروب">` بدل `<div>` عادي
  — تحسين accessibility بسيط.
- شرط تاب "اللايف" في النسخة الحقيقية **مفيهوش** `end_live_session` (لإنه
  endpoint من نوع POST بس، مالوش أي template بيتعرض منه أصلاً، فمنطقي
  إنه مش من ضمن شروط تفعيل التاب).
- أيقونة تاب "الواجبات" `fa-clipboard-list` (مش `fa-file-signature` اللي
  كنت حطيتها).

التركيبة المنطقية (أسماء الـ `url_name` المستخدمة في كل تاب) في النسختين
كانت متطابقة أصلاً ومطابقة لـ `groups/urls.py` الفعلي — الفرق كله شكلي/
تنظيمي، مفيش أي تاب كان هيتفعّل غلط.

**⚠️ الملفات العشرة اللي اتعدلت في الجلسة دي بيستدعوا `_group_tabs.html`
بالـ `{% include %}` بس (مش بينسخوا محتواه)، فاستبدال الملف ده لوحده كفاية
— مفيش أي تعديل إضافي مطلوب على أي من العشرة تمبلتات بسبب الاستبدال ده.**

خريطة التابات النهائية (url_name → تاب):
- `group_detail` → "نظرة عامة" **و** "الشات" (نفس الصفحة، تابين بيتفعّلوا
  مع بعض، فرقهم بس أنكور `#chat-section` في الرابط).
- `create_live_session`, `live_broadcast`, `end_live_session`,
  `join_live_session`, `group_recordings`, `watch_group_recording`,
  `upload_group_recording` → "اللايف".
- `upload_group_lesson`, `group_lessons_list`, `watch_group_lesson` →
  "الدروس المسجلة".
- `group_schedule` → "الجدول القادم".
- `create_group_assignment`, `group_assignments_list`,
  `submit_group_assignment`, `grade_submissions` → "الواجبات".
- `my_todo_list` → "مهامي" (رابط خروج لصفحة عامة، مش جزء من سياق جروب
  واحد — تفاصيل تحت).
- `group_members` → "الأعضاء" (يظهر بس لو `is_owner` موجودة في الـ
  context وقيمتها True).

### 3) ملحوظة مهمة: `is_owner` مش موجودة في context كل الصفحات

راجعت `groups/views.py` بالتفصيل ولاقيت إن مش كل الـ views اللي بتمرر
`group` بتمرر `is_owner` معاها:
- `live_broadcast`، `end_live_session`، `create_live_session` (المدرس/
  المضيف دايمًا — `instructor_required`): **مفيش `is_owner` في الـ
  context** — لكن المستخدم هنا هو صاحب الجروب دايمًا فعليًا (الفحص
  بيحصل جوه الـ view نفسها، مش عن طريق تمرير متغير للتمبلت).
- `join_live_session` (الطالب دايمًا — `student_required`): نفس الشيء،
  مفيش `is_owner`، لكن المستخدم مش صاحب الجروب دايمًا فعليًا.
- `upload_group_recording`: نفس الشيء (المدرس دايمًا، `instructor_required`).
- `group_recordings`, `watch_group_recording`, `group_lessons_list`,
  `watch_group_lesson`, `group_schedule`, `group_assignments_list`: دول
  بيمرروا `is_owner` فعليًا (بترجع من `_get_group_and_membership_or_403`).
- `submit_group_assignment`: مفيش `is_owner` (الطالب دايمًا،
  `student_required`).

**الأثر العملي**: تاب "الأعضاء" (اللي شرطه `{% if is_owner %}`) مش هيظهر
في `live_broadcast.html`، `watch_live_session.html`،
`upload_group_recording.html`، و`submit_group_assignment.html` — حتى لو
المستخدم فعليًا هو المدرس صاحب الجروب (في حالة `live_broadcast`/
`upload_group_recording`). ده تفصيل مش وظيفي خطير (المستخدم لسه يقدر
يوصل لصفحة الأعضاء من أي صفحة تانية فيها `is_owner`، زي `group_detail`)،
لكنه عدم اتساق بصري بسيط — **مش عايز ألمس منطق الـ views دي** بدون
توجيه صريح من Ahmed (تمرير `is_owner` إضافي محتاج تعديل Python في أربع
دوال). موثق هنا كملاحظة مفتوحة بدل ما يتحل بصمت.

### 4) `watch_live_session.html` — الـ include اتحط قبل شرط `view_mode`

الصفحة دي بتتفرع (`waiting`/`live`) بعد الـ breadcrumb مباشرة، فالـ
include اتحط بين الـ breadcrumb والـ `{% if view_mode == 'waiting' %}` —
يعني شريط التابات ظاهر في الحالتين (انتظار ومشاهدة) على حد سواء.

### 5) `watch_group_recording.html` — الـ breadcrumb بيرجع لـ `group_recordings` مش `group_detail`

الـ include اتحط بعد الـ breadcrumb زي باقي الملفات بالظبط، بغض النظر
إن وجهة الـ breadcrumb هنا مختلفة (بترجع لمكتبة التسجيلات مش لصفحة
الجروب) — ده متسق مع نص الطلب الأصلي ("رابط/breadcrumb واضح يرجّع لصفحة
تفاصيل الجروب" **أو** لأقرب صفحة أب منطقية، ونفس المبدأ ده كان متبع
بالفعل في `watch_group_lesson.html`/`grade_submissions.html` من الجلسة
اللي فاتت).

### 6) `my_todo_list.html` — استثناء موثق: رابط رجوع بسيط بدل التابات الكاملة

زي ما اتحدد صراحة في نص الجزء ("دي استثناء: متضفش فيها شريط التابات
الكامل — الصفحة دي عامة مش تابعة لجروب واحد محدد"):
- **مفيش `{% include 'groups/_group_tabs.html' %}`** في الملف ده خالص —
  الصفحة أصلاً معندهاش متغير `group` واحد في الـ context (`my_todo_list`
  view بتجمع مهام المستخدم عبر كل الجروبات + المهام الشخصية، مفيش
  `group_id` في مسارها من الأساس).
- بدل كده، ضفت رابط "رجوع" ديناميكي بسيط (`.todo-back-link`) فوق الـ
  hero مباشرة، بيتغيّر حسب دور المستخدم (نفس منطق `user.role == 'instructor'`
  المستخدم بالفعل في nav-links تحت في نفس الملف):
  - مدرس (`instructor`) → رجوع لـ `groups:teacher_dashboard`.
  - طالب (أي دور تاني) → رجوع لـ `groups:my_learning_groups`.
  - زائر مش مسجّل دخول (حالة نظرية — الصفحة أصلاً محمية بـ
    `login_required`) → رجوع لـ `/` (الصفحة الرئيسية)، كطبقة حماية
    إضافية فقط.
- اخترت الخيار "رابط ثابت لـ dashboard/my_learning_groups حسب دور
  المستخدم" (مش `HTTP_REFERER`) من الخيارات التلاتة المقترحة في نص
  الطلب — لإن `HTTP_REFERER` مش موثوق بيه دايمًا (بعض المتصفحات
  بتشيله لأسباب خصوصية، ومحتاج فحص إضافي في الـ view نفسها مش مجرد
  تمبلت)، والرابط الثابت حسب الدور أبسط وأكيد إنه شغال دايمًا.

### 7) مراجعة الروابط الداخلية (النقطة 3 من نص Part 37 الأصلي)

راجعت كل `{% url 'groups:...' %}` المستخدمة في الملفات العشرة + الملف
المشترك (`_group_tabs.html`) مقابل `groups/urls.py` الحقيقي سطر بسطر:

| اسم الرابط المستخدم | موجود في `urls.py`؟ |
|---|---|
| `group_detail` | ✅ |
| `create_live_session` | ✅ |
| `live_broadcast` | ✅ |
| `end_live_session` | ✅ |
| `join_live_session` | ✅ |
| `group_recordings` | ✅ |
| `watch_group_recording` | ✅ |
| `upload_group_recording` | ✅ |
| `upload_group_lesson` | ✅ |
| `group_lessons_list` | ✅ |
| `watch_group_lesson` | ✅ |
| `group_schedule` | ✅ |
| `create_group_assignment` | ✅ |
| `group_assignments_list` | ✅ |
| `submit_group_assignment` | ✅ |
| `grade_submissions` | ✅ |
| `my_todo_list` | ✅ |
| `toggle_todo_done` | ✅ (مش مستخدم في التابات نفسها، بس في `my_todo_list.html` الأصلية) |
| `group_members` | ✅ |
| `teacher_dashboard` | ✅ |
| `my_learning_groups` | ✅ |

**النتيجة: كل الروابط المستخدمة في التابات (والـ breadcrumbs الموجودة
مسبقًا في الملفات العشرة) موجودة فعليًا بنفس الاسم في `groups/urls.py` —
مفيش أي رابط لمسار غير موجود.** لا يوجد أي `NoReverseMatch` متوقع من أي
تعديل اتعمل في الجلسة دي أو اللي فاتت.

## سجل الأجزاء (تحديث نهائي)

### Part 37 — مركز تنقل موحّد داخل الجروب (تابات تربط كل حاجة)
الحالة: **تم** ✅ (اكتمل بالكامل — كل الملفات العشرة + `my_todo_list.html`
+ خريطة التابات + مراجعة الروابط الداخلية)

تفاصيل إضافية عن الجلسة اللي فاتت (اللي كانت خلصت `group_detail.html` +
3 تمبلتات واجبات + `group_members` كـ backend):
- الكومبوننت المشترك `_group_tabs.html` بقى مطبّق دلوقتي على **14 ملف
  تمبلت** بالإجمالي (الأربعة من الجلسة اللي فاتت + العشرة من الجلسة دي).
- `my_todo_list.html` معاها استثناء موثق (رابط رجوع بسيط بدل التابات
  الكاملة) — تفاصيل كاملة فوق، قسم 6.
- **مفيش أي migration جديدة، ومفيش أي تعديل على أي view/Python** في
  الجلسة دي — الشغل كله CSS/HTML (إضافة include + CSS)، زي ما اتطلب
  بالظبط في نص الجزء الأصلي.

⚠️ حاجات محتاجة انتباه/قرار من Ahmed:
1. ✅ **[اتحل]**: `_group_tabs.html` استُبدلت بالنسخة الحقيقية اللي بعتها
   Ahmed بعد المراجعة (تفاصيل الفرق فوق، قسم 2) — مفيش أي شك دلوقتي في
   مطابقة الملف ده للسيرفر الحقيقي.
2. تاب "الأعضاء" مش بيظهر في 4 صفحات (`live_broadcast`،
   `upload_group_recording`، `join_live_session`/`watch_live_session`،
   `submit_group_assignment`) لإن الـ views دي مفيهاش `is_owner` في الـ
   context — تفاصيل كاملة فوق، قسم 3. الحل (لو مطلوب) بسيط (تمرير
   `is_owner` إضافي في أربع دوال) بس محتاج قرار صريح قبل ما يتعمل، لإنه
   تعديل Python مش CSS/HTML بحت.
3. لسه معملتش أي اختبار فعلي على متصفح حقيقي للتابات الجديدة (نفس حال
   باقي التمبلتس اللي اتعدلت بدون سيرفر فعلي متاح) — لازم Ahmed يتأكد
   بصريًا إن التابات بتتفعّل صح على كل صفحة، وإن الـ scroll التلقائي
   لـ `#live-section`/`#chat-section` في `group_detail.html` شغال زي
   المتوقع.

# إضافة على PROGRESS — Part 38 (المرحلة الثانية)
### (هذا القسم يُلصق في نهاية PROGRESS_PART22.md الحالي — مش ملف بديل)

## ⚠️ ملاحظة عن نطاق المراجعة في الجلسة دي

المراجعة دي اتعملت عن طريق قراءة الكود الفعلي (`groups/tasks.py`، `groups/views.py`، `groups/views_lessons.py`، `groups/views_schedule.py`، `groups/views_assignments.py`، `groups/views_todo.py`، `groups/urls.py`، `groups/access.py`، `Eduvia/celery.py`) اللي بعتهملي Ahmed فعليًا في الجلسة دي — **مش من التوثيق**. السيناريوهين المطلوب اختبارهم يدويًا (نقطة 4 في نص الجزء) اتراجعوا منطقيًا عن طريق تتبّع الكود بس، مش اختبار فعلي على متصفح/سيرفر حقيقي (مفيش سيرفر متاح في الجلسة دي) — لازم Ahmed يأكدهم فعليًا زي باقي الأجزاء اللي فاتت قبل ما يعتبر Part 38 "متأكد 100%".

## 1) مراجعة Celery beat schedule (Eduvia/celery.py)

راجعت `app.conf.beat_schedule` كامل — كل الـ 5 entries مع بعض:

| Task | الجدولة | مسجّلة كـ `@shared_task`؟ |
|---|---|---|
| `send_periodic_reports` (performance_analysis، قبل المرحلة الثانية) | الإتنين 8:00 ص | ❌ لأ (تضارب قديم موثق من Part 15، برة نطاق المرحلة الثانية) |
| `freeze_expired_group_subscriptions` (Part 15) | يوميًا 2:00 ص | ✅ |
| `send_subscription_expiry_reminders` (Part 16) | يوميًا 9:00 ص | ✅ |
| `publish_scheduled_group_lessons` (Part 31) | كل 5 دقايق (`crontab(minute='*/5')`) | ✅ |
| `send_todo_reminders` (Part 36) | كل 10 دقايق (`crontab(minute='*/10')`) | ✅ |

**النتيجة**: كل تاسكات المرحلة الثانية (Part 31، Part 36) مسجّلة صح جنب تاسكات المرحلة الأولى (Part 15، Part 16) في نفس جدول `beat_schedule` الواحد، وكلهم بـ `@shared_task` القياسية من celery (زي القرار الموثق من Part 15) فـ`app.autodiscover_tasks()` قادرة تلاقيهم فعليًا — مفيش أي تاسك "مسجّل بالاسم بس" من غير decorator زي مشكلة `performance_analysis` القديمة.

**مفيش تعارض توقيتات حقيقي**:
- التاسكين اليوميين (2ص، 9ص) بعيدين عن بعض بساعتين، وبعيدين عن أي دورية تانية.
- التاسكين الدوريين (كل 5د، كل 10د) مستقلين تمامًا عن بعض وعن التاسكين اليوميين — فرق الـ 5 دقايق بينهم مقصود ومبرر (تفاصيل في `groups/tasks.py` نفسها): نشر الدرس محتاج دقة أعلى من تذكير المهمة.
- مفيش أي تاسكين بيشتغلوا على نفس الموديل في نفس اللحظة بطريقة ممكن تتعارض (كل تاسك بيفلتر على حقل/حالة مختلفة تمامًا).

⚠️ **ملحوظة قديمة لسه سارية (مش من نطاق المرحلة الثانية)**: `performance_analysis.tasks.send_dashboard_report_to_all`/`send_periodic_reports` لسه من غير `@shared_task` — تضارب موثق من Part 15، يستاهل تصليح منفصل مش جزء من الجزء ده.

## 2) مراجعة صلاحيات الوصول (permissions) — كل الأماكن

راجعت كل view بتلمس محتوى جروب في الملفات الستة (`views.py`، `views_lessons.py`، `views_schedule.py`، `views_assignments.py`، `views_todo.py`، بالإضافة لـ `access.py` نفسها كمرجع).

### النمط الموحّد المستخدم صح في 7 أماكن:
```python
is_owner, is_member = _get_group_and_membership_or_403(request, group)
if is_member and not is_owner and not is_group_content_accessible(group):
    messages.error(request, GROUP_FROZEN_MESSAGE)
    return redirect('groups:my_learning_groups')
```
مستخدم بالحرف في: `group_detail`، `group_recordings`، `watch_group_recording`، `group_lessons_list` (views_lessons.py)، `watch_group_lesson` (views_lessons.py)، `group_schedule` (views_schedule.py)، `group_assignments_list` (views_assignments.py).

### الـ views المقصورة على المدرس صاحب الجروب بس (owner-only، بدون فحص `is_group_content_accessible`):
`create_live_session`، `live_broadcast`، `end_live_session`، `upload_group_recording`، `upload_group_lesson`، `create_group_assignment`، `grade_submissions`، `toggle_chat_mode`، `group_members` — كلهم بيستخدموا `_get_owned_group_or_403` أو فحص `group.teacher_id == request.user.id` مباشر.

**ده مقصود ومتسق، مش نسيان**: المدرس صاحب الجروب دايمًا لازم يوصل حتى لو الجروب متجمد (عشان يقدر يشوف حالته ويجدد، ونفس الاستثناء الموثق في `group_detail` من Part 15) — فمفيش داعي لفحص `is_group_content_accessible` في views المدرس بس دي، وغيابه هنا مش ثغرة.

### تكرار كود بسيط (مش خطأ وظيفي) — يستاهل تنظيف لاحق:
`join_live_session` (views.py، Part 25) و`submit_group_assignment` (views_assignments.py، Part 34) بيعملوا فحص العضوية يدويًا:
```python
is_member = GroupMembership.objects.filter(student=request.user, group=group).exists()
if not is_member:
    raise PermissionDenied(...)
if not is_group_content_accessible(group):
    ...
```
بدل استخدام `_get_group_and_membership_or_403` المشترك. **النتيجة الوظيفية مطابقة تمامًا** (نفس الفحصين بنفس الترتيب)، والسبب منطقي (الصفحتين دول للطالب بس أصلاً — `student_required`/فحص عضوية مباشر — فمفيش داعي فعلي لـ `is_owner` اللي بيرجعها الـ helper). موثق هنا كملاحظة تنظيمية بسيطة، مش كثغرة أمنية.

### النتيجة النهائية:
**مفيش أي صفحة نسيت فحص الصلاحية أو استخدمت منطق بديل/مختلف لـ `is_group_content_accessible`.** كل الأماكن اللي المفروض تتحقق من الجروب "نشط ولا لأ" بتستخدم نفس الدالة المركزية من `groups/access.py` بلا استثناء.

## 3) مراجعة رسائل النجاح/الخطأ/التنبيه

كل الـ views في الملفات الستة (المرحلة الثانية بالكامل) بتستخدم `django.contrib.messages` (`messages.success`/`messages.error`/`messages.info`/`messages.warning`) — نفس المكتبة والأسلوب المستخدم في views المرحلة الأولى من Part 7. مفيش أي مكان في المرحلة الثانية بيستخدم نظام رسائل بديل (زي `JsonResponse` لرسائل نصية أو رسائل مكتوبة يدويًا في التمبلت) إلا `toggle_todo_done` و`live_webhook`، واللي منطقي يكونوا استثناء لأنهم AJAX/webhook endpoints بترجع `JsonResponse`/`HttpResponse` خام مش صفحة HTML.

## 4) اختبار السيناريوهين (مراجعة منطقية عن طريق تتبّع الكود)

⚠️ **دي مراجعة كود، مش تأكيد فعلي على سيرفر حقيقي** — Ahmed لازم يشغّلها فعليًا.

**سيناريو 1 — لايف كامل**:
`create_live_session` (start_choice=now) → `create_room()` تنجح → `status='live'` → ريدايركت لـ `live_broadcast` (المدرس) → طالب عضو يفتح `join_live_session` بنفس `session_id` → `status == 'live'` → `generate_access_token(role='viewer')` → صفحة `watch_live_session.html` (`view_mode='live'`). المدرس يضغط "إنهاء البث" → `end_live_session` → `end_room()` + `status='ended'`. المدرس يرفع التسجيل من `upload_group_recording` (بعد التأكد `status=='ended'`) → `recording_file` بيتحفظ. الطالب يرجع يفتح `join_live_session` لنفس الجلسة → `status == 'ended'` و`recording_file` موجود → ريدايركت مباشر لـ `watch_group_recording`. **التسلسل الكودي متكامل ومنطقي من غير أي فجوة**.

**سيناريو 2 — درس مجدول**:
`upload_group_lesson` (publish_choice=schedule) → `GroupLesson(is_published=False, publish_at=<ميعاد>)`. الطالب يفتح `group_schedule` → `get_group_schedule_items(group)` بتلقط الدرس ده (لسه `is_published=False` وليه `publish_at`) وتعرضه في الجدول. لما `publish_at` يوصل، `publish_scheduled_group_lessons` (كل 5 دقايق) بتلاقيه (`is_published=False`, `publish_at__lte=now`) → `is_published=True` + `_notify_group_members_new_lesson(lesson)` بيبعت إيميل لكل أعضاء الجروب. **التسلسل الكودي متكامل ومنطقي من غير أي فجوة**.

## 5) ملخص المرحلة الثانية (Part 22 → Part 38)

### إيه اللي اتعمل (نظرة عامة)
المرحلة التانية ضافت 4 أنظمة كاملة جوه صفحة الجروب: **بث مباشر حقيقي** (LiveKit WebRTC، كاميرا + مشاركة شاشة + رفع تسجيل يدوي)، **دروس مسجلة** (رفع/جدولة/نشر تلقائي)، **شات متقدم** (وضع إذاعة + مرفقات صور/ملفات)، **جدولة وتقويم** (صفحة جدول قادم موحّدة)، **واجبات** (إنشاء/تسليم/تصحيح يدوي بدرجة وملاحظات)، **مهام يومية** (To-Do شخصي + تذكيرات)، وأخيرًا **مركز تنقل موحّد** (تابات تربط كل ده ببعض في صفحة الجروب).

- **Part 22-26 (البث المباشر)**: قرار معماري باستخدام **LiveKit** (مفتوح المصدر، self-hosted بـDocker أو Cloud) بدل بناء SFU من الصفر بـDjango Channels وحدها — القرار الأهم في المرحلة كلها. موديل `GroupLiveSession`، طبقة `live_provider.py` معزولة (create_room/generate_access_token/end_room، sync wrappers حول async LiveKit SDK)، واجهة المدرس (بدء/جدولة/بث/إنهاء)، واجهة الطالب (انتظار/مشاهدة/تسجيل). نظام التسجيل التلقائي (LiveKit Egress) اتستبدل لاحقًا برفع يدوي من المدرس بعد طلب صريح من Ahmed.
- **Part 27-28 (الدروس المسجلة)**: موديل `GroupLesson` مبني على نفس أسلوب تخزين الفيديو المستخدم في `courses.Lesson` الحقيقي (`video_url` خارجي، مش رفع ملف — قرار مبني على فحص الكود الفعلي مش افتراض)، مع حقلي `is_published`/`publish_at` جاهزين من الأول للجدولة.
- **Part 29-30 (الشات المتقدم)**: حقل `chat_mode` على `TeacherGroup` (وضع الإذاعة)، وحقول مرفقات على `GroupChatMessage` (`message_type`, `attachment_image`, `attachment_file`) مع فحص نوع/حجم يدوي.
- **Part 31-32 (الجدولة)**: Celery task لنشر الدروس المجدولة تلقائيًا + إشعار الأعضاء، وصفحة/دالة تجميع (`get_group_schedule_items`) لعرض كل القادم (لايف + دروس) في قايمة واحدة مرتبة بالتاريخ، مع ودجت مختصر في لوحتي المدرس والطالب.
- **Part 33-34 (الواجبات)**: موديلين `GroupAssignment`/`GroupAssignmentSubmission` بتصحيح **يدوي** (درجة + ملاحظة، مش أوتوماتيكي زي نظام `courses` الحقيقي المختلف تمامًا — اكتشاف معماري موثق في Part 33) + إشعار الطالب بالإيميل بعد التصحيح.
- **Part 35-36 (المهام اليومية)**: موديل `GroupTodoItem` (شخصي، مش لازم مرتبط بجروب) + صفحة AJAX بسيطة (تبديل حالة "تم" من غير reload) + Celery task تذكير قبل الميعاد بساعة.
- **Part 37 (الربط والتنقل)**: كومبوننت `_group_tabs.html` مشترك (8 تابات، التاب النشط بيتحدد تلقائيًا من `request.resolver_match.url_name` من غير أي تعديل على أي view) اتطبّق على 14 تمبلت، + صفحة "الأعضاء" الجديدة بالكامل.
- **Part 38 (المراجعة الحالية)**: تأكيد عدم تعارض التوقيتات، اتساق الصلاحيات، اتساق الرسائل، ومراجعة منطقية لسيناريوهين end-to-end.

### أهم القرارات المعمارية

- **مزود الـ WebRTC (LiveKit)**: القرار الأكبر في المرحلة كلها — تفاصيله الكاملة والبدائل المرفوضة (Jitsi، Agora/Twilio/Zoom، بناء من الصفر) موثقة في "قرارات معمارية اتاخدت (Part 22)". قرار الاستضافة (self-hosted/Cloud) اتسيب مفتوح لـ Ahmed عمدًا.
- **`groups.access.is_group_content_accessible`** فضلت مصدر الحقيقة الوحيد لكل فحوصات "هل الجروب نشط" عبر المرحلة الثانية بالكامل، من غير أي استثناء أو منطق بديل.
- **التقسيم التنظيمي لـ views.py**: بداية من Part 28، الـ views الجديدة اتحطت في ملفات منفصلة حسب الموضوع (`views_lessons.py`, `views_schedule.py`, `views_assignments.py`, `views_todo.py`) بدل ما تتكدس في `views.py` الأصلي — قرار تنظيمي بحت من غير أي أثر على السلوك.
- **التصحيح اليدوي للواجبات** (مش الأوتوماتيكي الموجود في `courses`) — قرار مبني على قراءة الكود الفعلي، موثق كاكتشاف معماري في Part 33.
- **رفع التسجيل اليدوي** بدل LiveKit Egress — تغيير طلبه Ahmed صراحة بعد التنفيذ الأول، واتطبّق بإزالة كاملة لكود الـ Egress القديم مش مجرد تعطيله.

### حاجات محتاجة مراجعة يدوية من Ahmed قبل الإطلاق

1. **الأهم**: تشغيل السيناريوهين الكاملين (لايف كامل، درس مجدول) فعليًا على متصفح حقيقي — المراجعة هنا كانت منطقية (كود) بس، مش تنفيذ فعلي.
2. `join_live_session` و`submit_group_assignment` بيكرروا فحص العضوية بدل استخدام `_get_group_and_membership_or_403` — تنظيف كود اختياري، مفيش أثر وظيفي.
3. قرار استضافة LiveKit (self-hosted/Cloud) لسه مش موثق صراحة رغم إن فيه سيرفر شغال ومتأكد منه (من Part 23/24).
4. الفجوة الوظيفية من Part 24 (مفيش زرار "ابدأ" لجلسة لايف كانت متجدولة من قبل) لسه قايمة.
5. `CELERY_BEAT_SCHEDULER` لسه مش متظبط على `DatabaseScheduler` — الجدولة شغالة بس عن طريق الكود الثابت في `celery.py`، مش من لوحة الأدمن (نفس ملاحظة Part 15/21).
6. تضارب `performance_analysis` (تاسكات من غير `@shared_task`) لسه قايم، برة نطاق المرحلة الثانية.

**Part 38 — تم** (مراجعة كود كاملة؛ الاختبار الفعلي على السيرفر لسه مطلوب من Ahmed).