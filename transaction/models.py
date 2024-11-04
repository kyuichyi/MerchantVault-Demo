#pylint: disable=line-too-long, no-member

"""
This module contains the models for the Transaction app.
"""

from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from home.models import Merchant, BankStaff

class Transaction(models.Model):
    """
    Model representing a transaction between merchants.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(Merchant, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Merchant, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approver = models.CharField(max_length=150, null=True)

    def save(self, *args, **kwargs):
        """
        Save the transaction instance after performing validation checks.
        """
        if self.sender == self.receiver:
            raise ValidationError("Sender and receiver cannot be the same.")
        if self.amount <= Decimal('0.00'):
            raise ValidationError("Transaction amount must be greater than zero.")

        sender_merchant = self.sender
        if self.amount > sender_merchant.balance:
            raise ValidationError("Insufficient balance for the transaction.")

        super().save(*args, **kwargs)

        if self.status == 'approved':
            self.update_balances()

    def update_balances(self):
        """
        Update the balances of the sender and receiver after a transaction.
        """
        if self.sender.balance < self.amount:
            raise ValidationError("Insufficient balance for the transaction.")
        self.sender.balance -= self.amount
        self.receiver.balance += self.amount
        self.sender.save()
        self.receiver.save()

    def assign_bankstaff(self):
        """
        Assign a bank staff member to approve the transaction.
        """
        bankstaffs = list(BankStaff.objects.exclude(merchant_account=self.sender).exclude(merchant_account=self.receiver))
        if not bankstaffs:
            raise ValueError("No bank staff available to assign.")

        last_assigned = Transaction.objects.filter(approver__isnull=False).order_by('-date').first()
        if last_assigned:
            last_bankstaff = BankStaff.objects.get(user__username=last_assigned.approver)
            last_index = bankstaffs.index(last_bankstaff)
            next_index = (last_index + 1) % len(bankstaffs)
        else:
            next_index = 0

        self.approver = bankstaffs[next_index].user.username
        self.save()
