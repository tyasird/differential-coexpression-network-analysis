# Generated by Django 3.1.3 on 2021-02-18 18:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20210218_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='network',
            name='diffcoexp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.diffcoexpression'),
        ),
    ]
