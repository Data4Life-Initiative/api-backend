# Generated by Django 3.0.5 on 2020-05-31 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('core', '0003_areaseveritylevel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areaseveritylevel',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.Region'),
        ),
    ]