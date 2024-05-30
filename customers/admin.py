from django.contrib import admin
from .models import Customers,Debtors

# Register your models here.

class CustomersAdmin(admin.ModelAdmin):
    list_display = ["code","name","tel","route",]
    list_filter = ['route', ]

class DebtorsAdmin(admin.ModelAdmin):
    list_display = ['code','name','total_owing']


admin.site.register(Customers,CustomersAdmin)

admin.site.register(Debtors,DebtorsAdmin)
