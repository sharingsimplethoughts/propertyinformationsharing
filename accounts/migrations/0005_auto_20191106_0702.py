# Generated by Django 2.2.5 on 2019-11-06 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20191022_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_type',
            field=models.CharField(blank=True, choices=[('1', 'Personal'), ('2', 'Company')], max_length=20),
        ),
    ]
