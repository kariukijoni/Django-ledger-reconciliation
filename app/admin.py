from django.contrib import admin
from .models import Transaction, MatchedPayment
from customers.models import Debtors
# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    list_display=['transaction_date','value_date','customer_name','phone_number','payment_code','till_number','debit','credit']

admin.site.register(Transaction,TransactionAdmin)

class MatchedPaymentAdmin(admin.ModelAdmin):
    list_display = ['debtor_code','debtor_name','customer_code','phone_number']

    def debtor_name(self, obj):
        return obj.debtor.name

    def debtor_code(self, obj):
        return obj.debtor.code

admin.site.register(MatchedPayment, MatchedPaymentAdmin)
