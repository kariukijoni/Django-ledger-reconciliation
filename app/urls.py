from django.urls import path
from .views import separate_narrative, upload_file,transaction_list_view,transaction_list_data

urlpatterns = [
    path('transaction_upload/', upload_file, name='upload_file'),
    path('separate/', separate_narrative, name='transactions'),
    path('transactions/', transaction_list_view, name='transaction_list'),
    path('api/transactions/', transaction_list_data, name='transaction_list_data'),

]
