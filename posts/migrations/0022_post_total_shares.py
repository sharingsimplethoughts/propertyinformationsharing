# Generated by Django 2.2.5 on 2019-12-16 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20191216_0812'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='total_shares',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
