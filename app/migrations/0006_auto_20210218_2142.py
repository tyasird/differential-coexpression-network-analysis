# Generated by Django 3.1.3 on 2021-02-18 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210218_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='network',
            name='diff_coexp_id',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
    ]
