import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
    # phone_number = django_filters.CharFilter(lookup_expr='iexact')
    till_number = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Transaction
        fields = ['till_number']