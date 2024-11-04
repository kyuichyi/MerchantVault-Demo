"""
This module contains forms for the merchant app.
"""
from django import forms

from home.models import Merchant

class MerchantForm(forms.ModelForm):
    """
    Form for creating a merchant.
    """
    class Meta: # pylint: disable=too-few-public-methods, missing-class-docstring
        model = Merchant
        fields = ['email', 'first_name', 'last_name', 'phone', 'home_address']

    def save(self, commit=True):
        merchant = super().save(commit=False)
        user = merchant.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            merchant.save()
        return merchant
