# Generated by Django 3.0.5 on 2020-06-11 06:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_fcmpushnotificationregistrationtoken'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fcmpushnotificationregistrationtoken',
            options={'verbose_name': 'FCM Device'},
        ),
    ]