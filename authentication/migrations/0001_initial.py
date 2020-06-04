# Generated by Django 3.0.5 on 2020-05-25 11:03

import authentication.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.CharField(default=authentication.utils.hex_uuid, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(db_index=True, max_length=255, unique=True)),
                ('email', models.EmailField(blank=True, db_index=True, max_length=254, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('otp', models.CharField(blank=True, max_length=500, null=True)),
                ('otp_expiry', models.DateTimeField(blank=True, default=None, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataEntryAdmin',
            fields=[
                ('id', models.CharField(default=authentication.utils.hex_uuid, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('mobile_number', models.CharField(blank=True, default='', max_length=15, null=True)),
                ('fullname', models.CharField(max_length=50)),
                ('department', models.CharField(max_length=100)),
                ('designation', models.CharField(max_length=100)),
                ('organisation', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.CharField(default=authentication.utils.hex_uuid, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('lat', models.FloatField(default=0.0)),
                ('long', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='DataEntryAdminRegion',
            fields=[
                ('id', models.CharField(default=authentication.utils.hex_uuid, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('data_entry_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.DataEntryAdmin')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.Region')),
            ],
        ),
        migrations.CreateModel(
            name='Citizen',
            fields=[
                ('id', models.CharField(default=authentication.utils.hex_uuid, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('mobile_number', models.CharField(max_length=15)),
                ('fullname', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('dob', models.CharField(blank=True, default='01-01-1970', max_length=12, null=True)),
                ('home_latitude', models.FloatField(default=0.0)),
                ('home_longitude', models.FloatField(default=0.0)),
                ('is_profile_complete', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]