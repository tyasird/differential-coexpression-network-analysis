# Generated by Django 3.1.3 on 2021-02-18 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20210218_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='network',
            name='diffcoexp',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='app.diffcoexpression'),
        ),
    ]
