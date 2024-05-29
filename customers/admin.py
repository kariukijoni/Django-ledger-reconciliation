from django.contrib import admin
from .models import Customers

# Register your models here.

class CustomersAdmin(admin.ModelAdmin):
    list_display = ["code","name","tel","route",]
    list_filter = ['route', ]

admin.site.register(Customers,CustomersAdmin)
