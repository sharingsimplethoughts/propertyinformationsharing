# Generated by Django 2.2.5 on 2019-12-26 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0022_post_total_shares'),
    ]

    operations = [
        migrations.AlterField(
            model_name='markinvolvement',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='Involvement_images'),
        ),
    ]
