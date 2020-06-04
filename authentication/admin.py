from django.contrib import admin

from .models import User, DataEntryAdmin, Citizen

# Registering the database models in the django admin panel
# When registered these models can be manipulated from the admin panel
admin.site.register(User)
admin.site.register(DataEntryAdmin)
admin.site.register(Citizen)
