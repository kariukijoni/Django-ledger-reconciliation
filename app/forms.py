from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()

class ConfirmMatchForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Do you want to match this payment?")
    debtor_id = forms.IntegerField(widget=forms.HiddenInput())
    transaction_id = forms.IntegerField(widget=forms.HiddenInput())
