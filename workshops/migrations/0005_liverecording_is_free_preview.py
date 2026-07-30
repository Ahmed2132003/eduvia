from django.db import migrations, models


class Migration(migrations.Migration):

    # Part 18: إضافة حقل is_free_preview على LiveRecording — AddField
    # بسيط، القيمة الافتراضية False مناسبة لكل التسجيلات الموجودة بالفعل
    # (تفضل خاصة زي ما هي لحد ما حد يعلّمها يدويًا كمعاينة مجانية).

    dependencies = [
        ('workshops', '0004_livesession_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='liverecording',
            name='is_free_preview',
            field=models.BooleanField(default=False),
        ),
    ]