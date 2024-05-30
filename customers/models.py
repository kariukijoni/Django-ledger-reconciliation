# models.py
from django.db import models
from import_export import resources

class Customers(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    tel = models.CharField(max_length=20)
    route = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f'{self.code}-{self.name}'

class Debtors(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    total_owing = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = 'Debtors'

    def __str__(self) -> str:
        return f'{self.code}-{self.name}-{self.total_owing}'