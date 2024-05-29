from django.db import models

class Transaction(models.Model):
    transaction_date = models.DateField()
    value_date = models.DateField()
    narrative = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    running_balance = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    payment_code = models.CharField(max_length=50, blank=True, null=True)
    till_number = models.CharField(max_length=50, blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
