# Generated by Django 2.2.5 on 2019-11-27 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripecustomer',
            name='exp_month',
            field=models.CharField(default=12, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stripecustomer',
            name='exp_year',
            field=models.CharField(default=12, max_length=10),
            preserve_default=False,
        ),
    ]