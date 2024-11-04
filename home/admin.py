"""
Admin configuration for the home app.
"""

from django.contrib import admin
from .models import User, Merchant, BankStaff

# Register your models here.
class BankStaffAdmin(admin.ModelAdmin):
    """
    Admin configuration for the BankStaff model.
    """
    list_display = ('user', 'email')

class MerchantAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Merchant model.
    """
    list_display = ('user', 'email')

admin.site.register(User)
admin.site.register(BankStaff, BankStaffAdmin)
admin.site.register(Merchant, MerchantAdmin)
