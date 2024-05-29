# urls.py
from django.urls import path
from .views import upload_file,customer_list_view,customer_list_data

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
     path('', customer_list_view, name='customer_list'),
     path('api/customers/', customer_list_data, name='customer_list_data'),
]
