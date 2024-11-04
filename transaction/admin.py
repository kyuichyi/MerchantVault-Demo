"""
This module registers the Transaction model with the Django admin interface.
"""

from django.contrib import admin
from .models import Transaction

# Register your models here.
admin.site.register(Transaction)
