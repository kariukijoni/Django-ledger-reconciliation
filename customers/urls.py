# urls.py
from django.urls import path
from .views import customers_upload_file, customers_list_view, customers_list_data, debtors_upload_file, debtors_list_view, debtors_list_data

urlpatterns = [
    path('', customers_list_view, name='customers_list'),
    path('customers_upload/', customers_upload_file, name='customers_upload_file'),
    path('api/customers/', customers_list_data, name='customers_list_data'),

    path('debtors_upload/', debtors_upload_file, name='debtors_upload_file'),
    path('debtors/', debtors_list_view, name='debtors_list'),
    path('api/debtors/', debtors_list_data, name='debtors_list_data'),

]
