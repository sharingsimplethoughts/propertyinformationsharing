# Generated by Django 2.2.5 on 2019-11-02 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_postimages_image_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tag_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
