# views.py
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import pandas as pd
from .forms import UploadFileForm
from .models import Customers,Debtors

def customers_upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                customers = Customers(code=row['Code'], name=row['Name'], tel=row['Tel'], route=row['Route'])
                customers.save()
            return HttpResponse('File uploaded successfully!')
    else:
        form = UploadFileForm()
    return render(request, 'customers_upload.html', {'form': form})


def customers_list_view(request):
    # customers = Customers.objects.all()
    return render(request, 'customers_list.html')


def customers_list_data(request):
    customers = Customers.objects.all().values('code', 'name', 'tel', 'route')
    data = list(customers)
    return JsonResponse({'data': data})


def handle_uploaded_file(file):
    df = pd.read_excel(file)
    duplicates = []
    success_count = 0

    for index, row in df.iterrows():
        code = str(row['Companyid']).strip() if not pd.isna(row['Companyid']) else ''
        name = str(row['Name']).strip() if not pd.isna(row['Name']) else ''
        total_owing = row['Total Owing'] if not pd.isna(row['Total Owing']) else 0.0

        # Check if company_id already exists
        if Debtors.objects.filter(code=code).exists():
            duplicates.append({
                'code': code,
                'name': name,
                'total_owing': total_owing
            })
        else:
            # Create the company record
            Debtors.objects.create(
                code=code,
                name=name,
                total_owing=total_owing
            )
            success_count += 1

    return success_count, len(duplicates)


def debtors_upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            success_count, duplicate_count = handle_uploaded_file(request.FILES['file'])
            return render(request, 'debtors_upload.html', {
                'form': form,
                'success_count': success_count,
                'duplicate_count': duplicate_count
            })
    else:
        form = UploadFileForm()
    return render(request, 'debtors_upload.html', {
        'form': form,
        'success_count': 0,
        'duplicate_count': 0
    })


def debtors_list_view(request):
    # customers = Customers.objects.all()
    return render(request, 'debtors_list.html')


def debtors_list_data(request):
    debtors = Debtors.objects.all().values('code', 'name', 'total_owing')
    data = list(debtors)
    return JsonResponse({'data': data})
