# Generated by Django 2.2.5 on 2020-02-22 13:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0025_postowner'),
    ]

    operations = [
        migrations.AddField(
            model_name='postowner',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]