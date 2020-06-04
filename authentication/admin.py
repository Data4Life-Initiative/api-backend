from django.contrib import admin
from .models import User, DataEntryAdmin, Region, DataEntryAdminRegion, Citizen

admin.site.register(User)
admin.site.register(DataEntryAdmin)
admin.site.register(Region)
admin.site.register(DataEntryAdminRegion)
admin.site.register(Citizen)
