from django.contrib import admin
from .models import WorkCenterGroup, Machine, Transaction

admin.site.register(WorkCenterGroup)
admin.site.register(Machine)
admin.site.register(Transaction)
