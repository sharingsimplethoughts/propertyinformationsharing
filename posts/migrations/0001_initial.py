# Generated by Django 2.2.5 on 2019-10-21 09:27

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
            name='ProjectCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('year', models.DateTimeField()),
                ('tags', models.CharField(blank=True, max_length=500, null=True)),
                ('about_post', models.CharField(blank=True, max_length=1000, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='posts')),
                ('video', models.FileField(blank=True, null=True, upload_to='posts')),
                ('lat', models.CharField(blank=True, max_length=50, null=True)),
                ('lon', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_created_by', to=settings.AUTH_USER_MODEL)),
                ('project_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_project_category', to='posts.ProjectCategory')),
                ('project_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='p_project_type', to='posts.ProjectType')),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p_sector', to='posts.Sector')),
            ],
        ),
    ]
