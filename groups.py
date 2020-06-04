import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data4life_backend.settings.development')

import django

django.setup()
from django.contrib.auth.models import Group

GROUPS = ['Data Entry Admins', 'Citizens']
MODELS = ['user']

for group in GROUPS:
    new_group, created = Group.objects.get_or_create(name=group)
