# Generated by Django 3.1.3 on 2021-02-18 15:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200922_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='diff',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.diffcoexpression'),
            preserve_default=False,
        ),
    ]
