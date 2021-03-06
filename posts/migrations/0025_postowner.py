# Generated by Django 2.2.5 on 2020-02-22 10:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0024_flagpost_postflagreasons'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_joined', models.BooleanField(default=False)),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_owner', to=settings.AUTH_USER_MODEL)),
                ('post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_post_id', to='posts.Post')),
            ],
        ),
    ]
