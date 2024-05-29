from django.urls import path
from .views import separate_narrative, upload_file

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('separate/', separate_narrative, name='transactions'),
]
