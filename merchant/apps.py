"""
This module contains the configuration for the Merchant app.
"""
from django.apps import AppConfig

class MerchantConfig(AppConfig):
    """
    Configuration class for the Merchant app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'merchant'
