from django.contrib import admin
from .models import Transaction
# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    list_display=['transaction_date','value_date','customer_name','phone_number','payment_code','till_number','debit','credit']

admin.site.register(Transaction,TransactionAdmin)