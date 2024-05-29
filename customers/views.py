# views.py
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from .forms import UploadFileForm
from .models import Customers

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                your_model_instance = Customers(code=row['Code'], name=row['Name'], tel=row['Tel'], route=row['Route'])
                your_model_instance.save()
            return HttpResponse('File uploaded successfully!')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
