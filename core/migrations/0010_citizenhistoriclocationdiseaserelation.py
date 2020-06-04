# Generated by Django 3.0.5 on 2020-06-11 12:08

import authentication.utils
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20200611_0647'),
        ('core', '0009_mobilenumberwhitelist'),
    ]

    operations = [
        migrations.CreateModel(
            name='CitizenHistoricLocationDiseaseRelation',
            fields=[
                ('id', models.CharField(default=authentication.utils.hex_uuid, editable=False, max_length=36, primary_key=True, serialize=False, unique=True)),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
                ('location_name', models.CharField(blank=True, default='', max_length=250, null=True)),
                ('timestamp', models.CharField(max_length=50)),
                ('added_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('citizen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.Citizen')),
                ('disease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Disease')),
            ],
        ),
    ]