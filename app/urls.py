
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import separate_narrative, upload_file,transaction_list_view,transaction_list_data, match_payments, view_matched_payments, confirm_match, ajax_match_payments

urlpatterns = [

    path('transaction_upload/', upload_file, name='transaction_upload_file'),
    path('separate/', separate_narrative, name='separate_narrative'),
    path('transactions/', transaction_list_view, name='transaction_list'),
    path('api/transactions/', transaction_list_data, name='transaction_list_data'),

    path('match_payments/', match_payments, name='match_payments'),
    path('confirm_match/<int:debtor_id>/<int:transaction_id>/', confirm_match, name='confirm_match'),
    path('view_matched_payments/', view_matched_payments, name='view_matched_payments'),

    path('ajax/match_payments/', ajax_match_payments, name='ajax_match_payments'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
