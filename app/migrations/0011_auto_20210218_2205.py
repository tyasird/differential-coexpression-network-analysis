# Generated by Django 3.1.3 on 2021-02-18 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20210218_2202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='network',
            name='diff_coexp_id',
        ),
        migrations.RemoveField(
            model_name='network',
            name='diffcoexp',
        ),
        migrations.AddField(
            model_name='network',
            name='diff_coexp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.diffcoexpression'),
        ),
    ]