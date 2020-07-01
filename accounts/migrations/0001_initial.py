# Generated by Django 2.2.5 on 2019-10-21 09:27

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('mobile_number', models.CharField(blank=True, max_length=20, null=True)),
                ('country_code', models.CharField(blank=True, max_length=10, null=True)),
                ('is_mail_verify', models.BooleanField(default=False)),
                ('is_num_verify', models.BooleanField(default=False)),
                ('gender', models.CharField(choices=[('1', 'male'), ('2', 'female')], max_length=20)),
                ('profile_type', models.CharField(blank=True, choices=[('1', 'Personal'), ('2', 'Company'), ('3', 'Guest')], max_length=20)),
                ('cover_image', models.ImageField(blank=True, upload_to='cover_image')),
                ('profile_image', models.ImageField(blank=True, upload_to='profile_image')),
                ('is_profile_created', models.BooleanField(default=False)),
                ('is_social_active', models.BooleanField(default=False)),
                ('device_token', models.TextField()),
                ('device_type', models.CharField(choices=[('1', 'android'), ('2', 'ios')], max_length=5)),
                ('account_type', models.CharField(choices=[('1', 'normal'), ('2', 'fb'), ('3', 'google')], max_length=5)),
                ('about', models.CharField(blank=True, default='', max_length=500, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_guest', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BussinessArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CountryCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('country_code', models.CharField(blank=True, default='', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OTPStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_code', models.CharField(blank=True, max_length=10, null=True)),
                ('mobile', models.CharField(blank=True, max_length=20, null=True)),
                ('otp', models.CharField(blank=True, max_length=10, null=True)),
                ('is_used', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.CharField(max_length=50)),
                ('lon', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('rest_address', models.CharField(max_length=300)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ul_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SocialAccounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('1', 'normal'), ('2', 'fb'), ('3', 'google')], default=1, max_length=500)),
                ('social_id', models.CharField(blank=True, max_length=500, null=True)),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.CharField(choices=[('1', 'android'), ('2', 'ios')], max_length=10)),
                ('device_name', models.CharField(blank=True, max_length=30, null=True)),
                ('operating_system', models.CharField(blank=True, max_length=100, null=True)),
                ('app_version', models.CharField(blank=True, max_length=100, null=True)),
                ('device_id', models.CharField(blank=True, max_length=100, null=True)),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('address_line1', models.CharField(blank=True, max_length=200, null=True)),
                ('address_line2', models.CharField(blank=True, max_length=200, null=True)),
                ('address_line3', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('year_of_foundation', models.CharField(blank=True, max_length=5, null=True)),
                ('picture', models.ImageField(upload_to='company')),
                ('bussiness_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='c_bussiness_area', to='accounts.BussinessArea')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='c_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='profession',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='u_profession', to='accounts.Profession'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('mobile_number', 'country_code')},
        ),
    ]
