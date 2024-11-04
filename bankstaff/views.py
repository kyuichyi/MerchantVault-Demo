#pylint: disable=R0901

"""
This module contains views for managing merchants in the Bankstaff app.
"""

from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import DeleteView

from home.mixins import BankStaffOTPRequiredMixin
from home.models import User, Merchant
from .forms import MerchantForm

class MerchantDeleteView(BankStaffOTPRequiredMixin, DeleteView):
    """
    View for deleting a Merchant instance.
    """
    model = User
    success_url = '/manage/'
    template_name = 'bankstaff/merchant_delete.html'

class MerchantUpdateView(BankStaffOTPRequiredMixin, UpdateView):
    """
    View for updating a Merchant instance.
    """
    model = Merchant
    form_class = MerchantForm
    success_url = '/manage/'
    template_name = 'bankstaff/merchant_form.html'

class MerchantListView(BankStaffOTPRequiredMixin, ListView):
    """
    View for listing all Merchant instances.
    """
    model = Merchant
    context_object_name = 'merchants'
    template_name = 'bankstaff/merchant_list.html'

class MerchantDetailView(BankStaffOTPRequiredMixin, DetailView):
    """
    View for displaying details of a Merchant instance.
    """
    model = Merchant
    context_object_name = 'merchant'
    template_name = 'bankstaff/merchant_detail.html'
