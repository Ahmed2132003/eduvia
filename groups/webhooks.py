"""
groups/webhooks.py
===================
Part 23 (المرحلة الثانية — البث المباشر): نقطة استقبال (endpoint) فاضية
لـ webhook مزود البث (LiveKit).

Part 26 (نسخة معدّلة — Manual Recording Upload): الملف ده كان اتملى في
نسخة سابقة من Part 26 بمنطق كامل للتحقق من توقيع LiveKit ومعالجة حدث
'egress_ended' (نظام التسجيل التلقائي، Egress -> S3) — المنطق ده اتشال
بالكامل دلوقتي، لإن التسجيل بقى بيتم بالكامل عن طريق رفع يدوي من المدرس
(groups/views.py::upload_group_recording)، مش عن طريق إشعار من مزود
خارجي. الملف رجع لنفس حالته الأصلية من Part 23: endpoint فاضي بيرد
200 بس، من غير أي تحقق توقيع أو معالجة أي حدث.

قرار: الـ URL (`groups:live_webhook`) اتسابت موجودة في urls.py من غير
حذف — مفيش أي ضرر من endpoint فاضي بيرد 200، ولو Ahmed حابب يستخدمه
مستقبلاً لأي غرض تاني (زي أحداث room_started مثلاً، أو لو رجع لفكرة
التسجيل التلقائي يومًا ما)، البنية جاهزة من غير أي تعديل في urls.py.

@csrf_exempt / @require_POST اتسابوا زي ما هما — نفس السبب الأصلي من
Part 23: الطلب (لو حصل) جاي من سيرفر خارجي مش من متصفح فيه CSRF token،
ومفيش داعي نقبل أي method غير POST.
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def live_webhook(request):
    return HttpResponse(status=200)