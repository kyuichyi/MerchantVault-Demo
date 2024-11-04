#pylint: disable=too-many-ancestors

"""
This module contains views for the Merchant app.
"""

from django.views.generic import DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView

from home.mixins import MerchantOTPRequiredMixin
from home.models import User, Merchant
from .forms import MerchantForm

class UserChangeUsernameView(MerchantOTPRequiredMixin, UpdateView):
    """
    View for changing the username of a user.
    """
    model = User
    fields = ['username']
    success_url = '/account/'
    template_name = 'merchant/user_change_username.html'

    def get_object(self): #pylint: disable=arguments-differ
        return self.request.user

class UserChangePasswordView(MerchantOTPRequiredMixin, PasswordChangeView):
    """
    View for changing the password of a user.
    """
    model = User
    success_url = '/account/'
    template_name = 'merchant/user_change_password.html'

class UserDetailView(MerchantOTPRequiredMixin, DetailView):
    """
    View for displaying the details of a user.
    """
    model = User
    context_object_name = 'merchant'
    template_name = 'merchant/user_detail.html'

    def get_object(self): #pylint: disable=arguments-differ
        return self.request.user

class UserUpdateView(MerchantOTPRequiredMixin, UpdateView):
    """
    View for updating the details of a user.
    """
    model = Merchant
    form_class = MerchantForm
    success_url = '/account/'
    template_name = 'merchant/user_form.html'

    def get_object(self): #pylint: disable=arguments-differ
        return self.request.user.merchant
