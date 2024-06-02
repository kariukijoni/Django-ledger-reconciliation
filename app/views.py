from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse, HttpResponseBadRequest
from .forms import UploadFileForm, ConfirmMatchForm
import pandas as pd
from .models import Transaction, MatchedPayment
import re
from datetime import datetime
from .filters import TransactionFilter
from django.db import IntegrityError
import logging

from customers.models import Customers, Debtors

# Set up logging
logger = logging.getLogger(__name__)

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

def handle_decimal_value(value):
    if pd.isna(value):  # Check if the value is NaN
        return 0  # Replace NaN with a default value (e.g., 0)
    try:
        return float(str(value).replace(',', ''))
    except ValueError:
        return 0

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)

            duplicate_count = 0

            total_records = 0

            for index, row in df.iterrows():
                transaction_date = convert_date_format(row['Transaction Date'])
                value_date = convert_date_format(row['Value Date'])

                if transaction_date and value_date:
                    phone_number, payment_code,till_number, customer_name = extract_details_from_narrative(row['Narrative'])

                    if payment_code:
                        # Check for existing transaction with the same payment_code
                        if Transaction.objects.filter(payment_code=payment_code).exists():
                            # If a duplicate is found, log it and increment the duplicate count
                            logger.warning(f'Duplicate payment code {payment_code} at row {index}')
                            duplicate_count += 1

                        else:

                            try:
                                Transaction.objects.create(
                                    transaction_date=transaction_date,
                                    value_date=value_date,
                                    narrative=row['Narrative'],
                                    debit=handle_decimal_value(row['Debit']),
                                    credit=handle_decimal_value(row['Credit']),
                                    running_balance=handle_decimal_value(row['Running Balance']),
                                    phone_number=phone_number,
                                    payment_code=payment_code,
                                    till_number=till_number,
                                    customer_name=customer_name

                                )
                                total_records += 1
                            except IntegrityError:

                                # Handle duplicate payment_code from database constraints
                                logger.warning(f'Duplicate payment code {payment_code} at row {index}')

                                duplicate_count += 1
                    else:
                        # Handle case where payment_code is None or empty
                        logger.warning(f'Payment code missing at row {index}')
                else:
                    # Handle invalid date format (e.g., log the error or skip the record)
                    logger.warning(f'Invalid date format at row {index}')

            context = {
                'duplicate_count': duplicate_count,
                'total_records': total_records
            }

            return render(request, 'success.html', context)
    else:

        form = UploadFileForm()

    return render(request, 'transaction_upload.html', {'form': form})

def transaction_list_view(request):

    return render(request, 'transaction_list.html')

def transaction_list_data(request):
    transactions = Transaction.objects.all().values('transaction_date', 'value_date','customer_name', 'phone_number', 'payment_code',
                                             'till_number','debit','credit')

    data = list(transactions)

    return JsonResponse({'data': data})


def match_paymentsd(request):
    matches = []

    # Get all customers
    customers = Customers.objects.all()

    for customer in customers:
        # Find the corresponding debtor
        try:
            debtor = Debtors.objects.get(code=customer.code)
        except Debtors.DoesNotExist:
            continue

        # Find transactions that match the conditions
        transactions = Transaction.objects.filter(
            phone_number=customer.tel,
            credit__gt=0,
            status='unused'
        )

        for transaction in transactions:
            # Check if debtor.total_owing is equal to transaction.credit
            if debtor.total_owing == transaction.credit:
                # Update the debtor's total_owing
                debtor.total_owing -= transaction.credit
                debtor.save()

                # Create a matched payment entry
                matched_payment = MatchedPayment(
                    debtor=debtor,
                    transaction=transaction,
                    customer_code=customer.code,
                    phone_number=customer.tel
                )
                matched_payment.save()

                # Mark the transaction as used
                transaction.status = 'used'
                transaction.save()

                # Append match details for display
                matches.append({
                    'debtor_name': debtor.name,
                    'transaction_date': transaction.transaction_date,
                    'amount': transaction.credit,
                    'customer_code': customer.code,
                    'phone_number': customer.tel
                })
            else:
                # Redirect to confirmation page
                return redirect('confirm_match', debtor_id=debtor.id, transaction_id=transaction.id)

    # Render the results to a template (or return a simple HttpResponse)
    return render(request, 'match_results.html', {'matches': matches})


def confirm_match(request, debtor_id, transaction_id):
    debtor = get_object_or_404(Debtors, id=debtor_id)
    transaction = get_object_or_404(Transaction, id=transaction_id)
    customer = get_object_or_404(Customers, tel=transaction.phone_number)

    if request.method == 'POST':
        form = ConfirmMatchForm(request.POST)
        if form.is_valid():
            confirm = form.cleaned_data['confirm']
            if confirm:
                # Update the debtor's total_owing
                debtor.total_owing -= transaction.credit
                debtor.save()

                # Create a matched payment entry
                matched_payment = MatchedPayment(
                    debtor=debtor,
                    transaction=transaction,
                    customer_code=customer.code,
                    phone_number=customer.tel
                )
                matched_payment.save()

                # Mark the transaction as used
                transaction.status = 'used'
                transaction.save()

            return redirect('view_matched_payments')
    else:
        form = ConfirmMatchForm(initial={
            'debtor_id': debtor.id,
            'transaction_id': transaction.id
        })

    return render(request, 'confirm_match.html', {
        'form': form,
        'debtor': debtor,
        'transaction': transaction
    })

def view_matched_payments(request):
    matched_payments = MatchedPayment.objects.all().select_related('debtor', 'transaction')

    matches = [{
        'debtor_name': mp.debtor.name,
        'transaction_date': mp.transaction.transaction_date,
        'amount': mp.transaction.credit,
        'matched_date': mp.matched_date,
        'customer_code': mp.customer_code,
        'phone_number': mp.phone_number

    } for mp in matched_payments]

    return render(request, 'view_matched_results.html', {'matches': matches})


def ajax_match_payments(request):
    if request.method == 'POST':
        customer_code = request.POST.get('customer_code')
        phone_number = request.POST.get('phone_number')
        transaction_id = request.POST.get('transaction_id')
        confirm_match = request.POST.get('confirm_match', 'false') == 'true'

        try:
            customer = get_object_or_404(Customers, code=customer_code, tel=phone_number)
            debtor = get_object_or_404(Debtors, code=customer_code)
            transaction = get_object_or_404(Transaction, id=transaction_id, phone_number=phone_number)

            if debtor.total_owing == transaction.credit or confirm_match:
                # Update the debtor's total_owing
                debtor.total_owing -= transaction.credit
                debtor.save()

                # Create a matched payment entry
                matched_payment = MatchedPayment(
                    debtor=debtor,
                    transaction=transaction,
                    customer_code=customer.code,
                    phone_number=customer.tel
                )
                matched_payment.save()

                # Mark the transaction as used
                transaction.status = 'used'
                transaction.save()

                response = {
                    'status': 'success',
                    'message': 'Payment matched successfully.',
                    'debtor_name': debtor.name,
                    'transaction_date': transaction.transaction_date,
                    'amount': transaction.credit,
                    'customer_code': customer.code,
                    'phone_number': customer.tel
                }
            else:
                response = {
                    'status': 'confirm',
                    'message': 'Debtor total owing does not match transaction credit. Do you want to match anyway?',
                    'debtor_name': debtor.name,
                    'transaction_date': transaction.transaction_date,
                    'amount': transaction.credit,
                    'customer_code': customer.code,
                    'phone_number': customer.tel,
                    'transaction_id': transaction.id
                }

            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return HttpResponseBadRequest('Invalid request method.')


def match_payments(request):
    matches = []
    unmatched = []

    # Get all customers
    customers = Customers.objects.all()

    for customer in customers:
        # Find the corresponding debtor
        try:
            debtor = Debtors.objects.get(code=customer.code)
        except Debtors.DoesNotExist:
            continue

        # Find transactions that match the conditions
        transactions = Transaction.objects.filter(
            phone_number=customer.tel,
            credit__gt=0,
            status='unused'
        )

        for transaction in transactions:
            if debtor.total_owing == transaction.credit:
                matches.append({
                    'debtor_name': debtor.name,
                    'transaction_date': transaction.transaction_date,
                    'amount': transaction.credit,
                    'customer_code': customer.code,
                    'phone_number': customer.tel,
                    'transaction_id': transaction.id
                })
            else:
                unmatched.append({
                    'debtor_name': debtor.name,
                    'transaction_date': transaction.transaction_date,
                    'amount': transaction.credit,
                    'customer_code': customer.code,
                    'phone_number': customer.tel,
                    'transaction_id': transaction.id
                })

    # Render the results to a template
    return render(request, 'match_results.html', {'matches': matches, 'unmatched': unmatched})
