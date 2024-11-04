#pylint: disable=line-too-long

"""
This module contains the models for the Home app.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    """
    Custom user model with additional fields for merchant and bank staff.
    """
    is_merchant = models.BooleanField(default=False)
    is_bankstaff = models.BooleanField(default=False)

class Merchant(models.Model):
    """
    Model representing a merchant.
    """
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='merchant')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    home_address = models.CharField(max_length=100)
    phone = PhoneNumberField(region='SG', unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

class BankStaff(models.Model):
    """
    Model representing a bank staff member.
    """
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='bankstaff')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    home_address = models.CharField(max_length=100)
    merchant_account = models.ForeignKey(Merchant, related_name='transactions', on_delete=models.CASCADE, null=True, blank=True)

class AccessLog(models.Model):
    """
    Model representing an access log entry.
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
