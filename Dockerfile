 # إعداد البيئة
 ENV PYTHONDONTWRITEBYTECODE=1
 ENV PYTHONUNBUFFERED=1

 # إنشاء مجلد العمل
 WORKDIR /app

 # تثبيت التبعيات
 RUN pip install --upgrade pip
 COPY requirements.txt .
 RUN pip install -r requirements.txt

 # نسخ ملفات المشروع
 COPY . .

 # جمع الملفات الثابتة
 RUN python manage.py collectstatic --noinput

 # تعريض المنفذ
 EXPOSE 8000

 # تشغيل Gunicorn
 CMD ["gunicorn", "--bind", "0.0.0.0:8000", "Eduvia.wsgi"]