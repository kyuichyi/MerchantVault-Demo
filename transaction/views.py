#pylint: disable=no-member, too-many-ancestors

"""
This module contains views for the Transaction app.
"""

from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView, UpdateView, ListView
from django.core.exceptions import ValidationError, PermissionDenied

from home.mixins import MerchantOTPRequiredMixin, BankStaffOTPRequiredMixin

from .models import Transaction
from .forms import NewTransactionForm

class NewTransactionView(MerchantOTPRequiredMixin, CreateView):
    """
    View for creating a new transaction.
    """
    model = Transaction
    template_name = 'transaction/new_transaction.html'
    form_class = NewTransactionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['merchant'] = self.request.user.merchant  # Pass Merchant object to context
        return context

    def form_valid(self, form):
        try:
            transaction = form.save(commit=False)
            # Set sender to logged-in user's merchant instance
            transaction.sender = self.request.user.merchant
            transaction.save()
            transaction.assign_bankstaff()
            return redirect('transaction.success')
        except ValidationError as e: # Catch ValidationError from transaction/model.py
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class TransactionSuccessView(MerchantOTPRequiredMixin, TemplateView):
    """
    View for displaying a success message after a transaction is created.
    """
    template_name = 'transaction/transaction_success.html'

class TransactionHistoryView(MerchantOTPRequiredMixin, ListView):
    """
    View for displaying the transaction history of a merchant.
    """
    template_name = 'transaction/transaction_history.html'
    model = Transaction
    context_object_name = 'transactions'

    def get_queryset(self):
        return (Transaction.objects.filter(sender=self.request.user.merchant).order_by('-date') |
                Transaction.objects.filter(receiver=self.request.user.merchant, status='approved').order_by('-date')) #pylint: disable=line-too-long

class BankStaffApprovalListView(BankStaffOTPRequiredMixin, ListView):
    """
    View for displaying a list of transactions pending approval by a bank staff member.
    """
    model = Transaction
    template_name = 'transaction/approve_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(approver=self.request.user.username, status='pending')

class BankStaffApproveView(BankStaffOTPRequiredMixin, UpdateView):
    """
    View for approving or rejecting a transaction by a bank staff member.
    """
    model = Transaction
    template_name = 'transaction/approve_transaction.html'
    fields = ['status']

    def get_queryset(self):
        return Transaction.objects

    def get_object(self, queryset=None):
        transaction = super().get_object(queryset)
        if (transaction.status != 'pending' or transaction.approver != self.request.user.username):
            raise PermissionDenied("This transaction has already been processed and cannot be modified.") #pylint: disable=line-too-long
        return transaction

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.approver = self.request.user.username
        transaction.save()
        return redirect('approve.list')

class BankstaffTransactionHistoryView(BankStaffOTPRequiredMixin, ListView):
    """
    View for displaying the transaction approval history of a bank staff member.
    """
    model = Transaction
    template_name = 'transaction/bankstaff_transaction_history.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        #pylint: disable=line-too-long
        return (Transaction.objects.filter(approver=self.request.user.username, status='approved').order_by('-date') |
                Transaction.objects.filter(approver=self.request.user.username, status='rejected').order_by('-date'))
