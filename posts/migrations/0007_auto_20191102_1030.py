# Generated by Django 2.2.5 on 2019-11-02 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_projecttype_is_t_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='t_type_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='t_type_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]