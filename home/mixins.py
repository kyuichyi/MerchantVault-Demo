"""
This module contains custom mixins for the Home app.
"""

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django_otp.plugins.otp_email.models import EmailDevice

class BankStaffOTPRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is an authenticated bank staff member with confirmed OTP.
    """
    def test_func(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_bankstaff:
                raise PermissionDenied
            email_device = EmailDevice.objects.filter(user=self.request.user).first()
            return email_device and email_device.confirmed
        return False

    def handle_no_permission(self):
        return redirect('verify')

class MerchantOTPRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is an authenticated merchant with confirmed OTP.
    """
    def test_func(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_merchant:
                raise PermissionDenied
            email_device = EmailDevice.objects.filter(user=self.request.user).first()
            return email_device and email_device.confirmed
        return False

    def handle_no_permission(self):
        return redirect('verify')
