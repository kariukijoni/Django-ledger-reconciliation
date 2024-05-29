from django.shortcuts import render
from .forms import UploadFileForm
import pandas as pd
from .models import Transaction
import re
from datetime import datetime
from .filters import TransactionFilter

def separate_narrative(request):
    transactions = Transaction.objects.all()

    trans_filter=TransactionFilter(request.GET,queryset=transactions)
    # trans_filter=filter.qs

    has_filter = any(field in request.GET for field in set(trans_filter.get_fields()))

    for transaction in transactions:
        transaction.phone_number, transaction.payment_code,transaction.till_number, transaction.customer_name = extract_details_from_narrative(transaction.narrative)
        transaction.save()
    return render(request, 'separate_narrative.html', {'transactions': transactions,'trans_filter':trans_filter,'has_filter': has_filter})

def extract_details_from_narrative(narrative):
    # Define regular expression patterns to extract phone number and payment code
    phone_number_pattern = r'\b\d{12}\b'
    # payment_code_pattern = r'MPS\s+\d+\s+SEJ\w{7}'
    payment_code_pattern = r'SE\w{8}'
    # till
    till_number_pattern = r'\b\d{10}\b'

    # remove mps
    mps_code_pattern = r'MPS'

    # Extract phone number
    phone_number_match = re.search(phone_number_pattern, narrative)
    phone_number = phone_number_match.group(0) if phone_number_match else None

    # Extract payment code
    payment_code_match = re.search(payment_code_pattern, narrative)
    payment_code = payment_code_match.group(0) if payment_code_match else None

    till_number_match = re.search(till_number_pattern, narrative)
    till_number = till_number_match.group(0) if till_number_match else None

    # Extract mps code
    mps_code_match = re.search(mps_code_pattern, narrative)
    mps_code = mps_code_match.group(0) if mps_code_match else None

    # Extract customer name (assuming it's the remaining part of the narrative)
    customer_name = narrative

    # Replace phone number if not None
    if phone_number:
        customer_name = customer_name.replace(phone_number, '').strip()

    # Replace payment code if not None
    if payment_code:
        customer_name = customer_name.replace(payment_code, '').strip()

    # Replace till_number if not None
    if till_number:
        customer_name = customer_name.replace(till_number, '').strip()


    # Replace till_number if not None
    if mps_code:
        customer_name = customer_name.replace(mps_code, '').strip()

    return phone_number, payment_code, till_number, customer_name
    # return phone_number, payment_code, customer_name


def convert_date_format(date_str):
    if pd.isna(date_str):  # Check if the value is NaN
        return None  # Return None for NaN values
    try:
        date_obj = datetime.strptime(str(date_str), '%d-%m-%Y').date()
        return date_obj
    except ValueError:
        return None

def handle_decimal_value(value_str):
    if pd.isna(value_str):  # Check if the value is NaN
        return 0  # Replace NaN with a default value (e.g., 0)
    try:
        value = float(value_str.replace(',', ''))  # Remove commas and convert to float
    except ValueError:
        value = 0  # Default value if conversion fails
    return value


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                transaction_date = convert_date_format(row['Transaction Date'])
                value_date = convert_date_format(row['Value Date'])
                if transaction_date and value_date:
                    phone_number, payment_code, till_number, customer_name = extract_details_from_narrative(row['Narrative'])
                    Transaction.objects.create(
                        transaction_date=transaction_date,
                        value_date = value_date,
                        narrative = row['Narrative'],
                        debit = handle_decimal_value(row['Debit']),
                        credit = handle_decimal_value(row['Credit']),
                        running_balance = handle_decimal_value(row['Running Balance']),
                        phone_number = phone_number,
                        payment_code = payment_code,
                        till_number = till_number,
                        customer_name = customer_name
                    )
                else:
                    # Handle invalid date format
                    pass
            return render(request, 'success.html')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})