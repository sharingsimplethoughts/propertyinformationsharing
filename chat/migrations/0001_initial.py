# Generated by Django 2.2.5 on 2020-02-11 11:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatReportReasons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='ReportChat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField()),
                ('report_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_report_id', to='chat.ChatReportReasons')),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_reported_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('chat_id', 'report_id')},
            },
        ),
    ]