# Generated by Django 2.2.5 on 2019-11-02 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20191102_1030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='sector',
        ),
    ]
