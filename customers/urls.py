# urls.py
from django.urls import path
from .views import customer_upload_file,customer_list_view,customer_list_data,debtors_upload_file

urlpatterns = [
    path('customer_upload/', customer_upload_file, name='customer_upload_file'),
    path('', customer_list_view, name='customer_list'),
    path('api/customers/', customer_list_data, name='customer_list_data'),

    path('debtors_upload/', debtors_upload_file, name='debtors_upload_file'),
]
