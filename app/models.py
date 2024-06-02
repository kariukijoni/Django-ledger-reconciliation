from django.db import models
from customers.models import Debtors

class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('unused', 'Unused'),
        ('used', 'Used'),
    ]

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

    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES, default='unused')

class MatchedPayment(models.Model):
    # code = models.ForeignKey(Debtors, on_delete=models.CASCADE)
    debtor = models.ForeignKey(Debtors, on_delete=models.CASCADE)
    # credit = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    customer_code = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    matched_date = models.DateTimeField(auto_now_add=True)
