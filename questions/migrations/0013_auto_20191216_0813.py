# Generated by Django 2.2.5 on 2019-12-16 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20191216_0812'),
        ('questions', '0012_auto_20191212_1309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionreport',
            name='text',
        ),
        migrations.AddField(
            model_name='questionreport',
            name='reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.ReportReasons'),
        ),
    ]
