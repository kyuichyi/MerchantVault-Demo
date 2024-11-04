#pylint: disable=R0903,E1101,R0901

"""
This module contains forms for the Home app.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from home.models import User, Merchant

class OTPForm(forms.Form):
    """
    Form for entering OTP.
    """
    otp = forms.CharField(max_length=6, required=True, label='Enter OTP')

class MerchantSignUpForm(UserCreationForm):
    """
    Form for creating and updating Merchant instances.
    """
    email = forms.EmailField(widget=forms.EmailInput())
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    home_address = forms.CharField(widget=forms.TextInput())
    phone = forms.CharField(
        widget=forms.NumberInput(),
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^[689]\d{7}$',
                message='Phone number must start with 6, 8, or 9 and be 8 digits long.'
            )
        ]
    )

    class Meta(UserCreationForm.Meta): #pylint: disable=C0115
        model = User
        fields = ['username', 'phone', 'first_name', 'last_name', 'email', 'home_address']

    @transaction.atomic
    def save(self): #pylint: disable=W0221
        email = self.cleaned_data.get('email')
        if Merchant.objects.filter(email=email).exists():
            raise ValidationError(
                f"User with the email {email} already exists. Log in instead?"
            )

        phone = self.cleaned_data.get('phone')
        if Merchant.objects.filter(phone=phone).exists():
            raise ValidationError(
                f"User with the phone number {phone} already exists. Log in instead?"
            )

        user = super().save(commit=False)
        user.is_merchant = True
        user.save()
        Merchant.objects.create(user=user,
                                first_name=self.cleaned_data.get('first_name'),
                                last_name=self.cleaned_data.get('last_name'),
                                home_address=self.cleaned_data.get('home_address'),
                                phone=self.cleaned_data.get('phone'),
                                email=self.cleaned_data.get('email')
                                )
        return user
