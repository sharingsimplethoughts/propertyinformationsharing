# Generated by Django 2.2.5 on 2019-10-22 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_bussinessarea_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bussinessarea',
            name='subscription',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='barea_subs', to='subscriptions.SubscriptionPlan'),
        ),
    ]
