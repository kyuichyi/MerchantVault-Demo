"""
This module contains the configuration of the transaction app.
"""

from django.apps import AppConfig

class TransactionConfig(AppConfig):
    """
    Configuration class for the Merchant app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transaction'
