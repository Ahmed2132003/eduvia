from django.db import migrations, models


class Migration(migrations.Migration):

    # Part 16: إضافة فلاجات تنبيهات انتهاء الاشتراك على GroupSubscription.
    # AddField بسيط بس، من غير أي RunPython — القيمة الافتراضية False
    # مناسبة تمامًا لكل الصفوف الموجودة بالفعل (يعني أي اشتراك قديم
    # هيتعامل معاه التاسك الجديد وكأنه لسه ماتبعتلوش أي تنبيه، وده سلوك
    # صحيح ومتوقع).

    dependencies = [
        ('groups', '0008_groupchatmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupsubscription',
            name='reminder_3days_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='groupsubscription',
            name='reminder_1day_sent',
            field=models.BooleanField(default=False),
        ),
    ]