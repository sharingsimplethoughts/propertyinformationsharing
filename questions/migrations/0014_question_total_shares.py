# Generated by Django 2.2.5 on 2019-12-16 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0013_auto_20191216_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='total_shares',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]