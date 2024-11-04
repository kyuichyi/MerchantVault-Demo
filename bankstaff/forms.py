#pylint: disable=duplicate-code

"""
This module contains forms for the Bankstaff app.
"""

from django import forms
from home.models import Merchant

class MerchantForm(forms.ModelForm):
    """
    Form for creating and updating Merchant instances.
    """
    username = forms.CharField()

    class Meta:
        """
        Meta options for the MerchantForm.
        """
        # pylint: disable=too-few-public-methods
        model = Merchant
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'home_address')

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
