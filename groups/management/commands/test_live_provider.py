"""
groups/management/commands/test_live_provider.py
==================================================
Part 23 (المرحلة الثانية — البث المباشر): اختبار يدوي بسيط للتأكد إن
groups/live_provider.py شغال فعليًا مع سيرفر LiveKit حقيقي (self-hosted
بـ Docker أو LiveKit Cloud — أيًا كان اللي اتظبط في LIVEKIT_URL).

الاستخدام:
    python manage.py test_live_provider
    python manage.py test_live_provider --group-id 5

محتاج:
  - LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET متظبطين فعليًا
    (متغيرات بيئة — راجع Eduvia/settings.py، Part 23).
  - سيرفر LiveKit شغال بالفعل وقابل للوصول من السيرفر اللي بتشغل عليه
    الأمر ده.
  - على الأقل TeacherGroup واحد موجود في الداتابيز (أي جروب، مش شرط
    يكون نشط — الأمر ده مش بيلمس صلاحيات الجروب أو حالة اشتراكه خالص).

الأمر بيعمل GroupLiveSession في الذاكرة بس (من غير .save() — مفيش أي
صف جديد بيتحفظ في الداتابيز)، وبيمشي على التسلسل الطبيعي: إنشاء روم،
توليد توكن host، توليد توكن viewer، وأخيرًا قفل الروم — عشان يتأكد إن
الأربع عمليات شغالة.
"""
from django.core.management.base import BaseCommand, CommandError

from groups.models import TeacherGroup, GroupLiveSession
from groups import live_provider


class Command(BaseCommand):
    help = (
        "اختبار يدوي بسيط لطبقة التكامل مع LiveKit (groups/live_provider.py): "
        "بينشئ روم تجريبي، يولّد توكن host وtoken viewer، وبعدين يقفل الروم. "
        "محتاج LIVEKIT_URL/LIVEKIT_API_KEY/LIVEKIT_API_SECRET مظبوطين فعليًا "
        "(سيرفر LiveKit شغال، self-hosted أو Cloud) قبل ما تشغله."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--group-id',
            type=int,
            default=None,
            help=(
                "id بتاع TeacherGroup موجود بالفعل تستخدمه للاختبار. لو "
                "مش متحدد، هياخد أول جروب موجود في الداتابيز تلقائيًا."
            ),
        )

    def handle(self, *args, **options):
        group = self._get_group(options.get('group_id'))
        host_user = group.teacher

        self.stdout.write(self.style.NOTICE(f"بستخدم الجروب: {group} (id={group.pk})"))
        self.stdout.write(self.style.NOTICE(f"المدرس (host): {host_user.username} (id={host_user.pk})"))
        self.stdout.write('')

        # جلسة في الذاكرة بس — مفيش .save()، الأمر ده مش بيعمل بيانات
        # تجريبية دايمة في الداتابيز.
        session = GroupLiveSession(
            group=group,
            host=host_user,
            title="[اختبار] جلسة تجريبية — groups.live_provider",
            mode='camera',
        )

        self.stdout.write("1) create_room ...")
        try:
            room_identifier = live_provider.create_room(session)
        except live_provider.LiveProviderError as exc:
            raise CommandError(f"create_room فشلت: {exc}")
        session.room_identifier = room_identifier
        self.stdout.write(self.style.SUCCESS(f"   ✅ room_identifier = {room_identifier}"))

        self.stdout.write("2) generate_access_token (role='host') ...")
        try:
            host_token = live_provider.generate_access_token(session, host_user, role='host')
        except live_provider.LiveProviderError as exc:
            raise CommandError(f"generate_access_token (host) فشلت: {exc}")
        self.stdout.write(self.style.SUCCESS(f"   ✅ host token (أول 40 حرف): {host_token[:40]}..."))

        self.stdout.write("3) generate_access_token (role='viewer') ...")
        try:
            viewer_token = live_provider.generate_access_token(session, host_user, role='viewer')
        except live_provider.LiveProviderError as exc:
            raise CommandError(f"generate_access_token (viewer) فشلت: {exc}")
        self.stdout.write(self.style.SUCCESS(f"   ✅ viewer token (أول 40 حرف): {viewer_token[:40]}..."))

        self.stdout.write("4) end_room ...")
        try:
            live_provider.end_room(session)
        except live_provider.LiveProviderError as exc:
            raise CommandError(f"end_room فشلت: {exc}")
        self.stdout.write(self.style.SUCCESS("   ✅ end_room اتنفذت من غير أخطاء"))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS("كل الخطوات نجحت — التكامل مع LiveKit شغال فعليًا."))

    def _get_group(self, group_id):
        qs = TeacherGroup.objects.select_related('teacher')
        if group_id is not None:
            try:
                return qs.get(pk=group_id)
            except TeacherGroup.DoesNotExist:
                raise CommandError(f"مفيش TeacherGroup بالـ id={group_id}")
        group = qs.first()
        if not group:
            raise CommandError(
                "مفيش أي TeacherGroup في الداتابيز خالص — اعمل جروب واحد على "
                "الأقل الأول (أو استخدم --group-id لو الجروب في داتابيز تانية)."
            )
        return group