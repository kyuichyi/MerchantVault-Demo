"""
This module contains the form for creating a new transaction.
"""

from django import forms
from django.core.exceptions import ValidationError

from home.models import Merchant
from .models import Transaction

class NewTransactionForm(forms.ModelForm):
    """
    Form for creating a new transaction.
    """
    receiver_username = forms.CharField(max_length=150)

    class Meta: #pylint: disable=too-few-public-methods, missing-class-docstring
        model = Transaction
        fields = ['receiver_username', 'amount']

    def clean_receiver_username(self):
        """
        Clean and validate the receiver's username.
        """
        username = self.cleaned_data.get('receiver_username')
        try:
            receiver = Merchant.objects.get(user__username=username) #pylint: disable=no-member
        except Merchant.DoesNotExist: #pylint: disable=no-member
            raise ValidationError("The receiver username does not exist.") #pylint: disable=raise-missing-from
        return receiver

    def save(self, commit=True):
        """
        Save the transaction instance.
        """
        try:
            transaction = super().save(commit=False)
            transaction.receiver = self.cleaned_data['receiver_username']
            transaction.amount = self.cleaned_data['amount']
            if commit:
                transaction.save()
            return transaction
        except ValidationError as e:
            raise e
