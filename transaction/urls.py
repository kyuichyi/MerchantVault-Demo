#pylint: disable=line-too-long

"""
URL configuration for the transaction app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('transfer/new/', views.NewTransactionView.as_view(), name='transaction.new'),
    path('transfer/success/', views.TransactionSuccessView.as_view(), name='transaction.success'),
    path('history/', views.TransactionHistoryView.as_view(), name='transaction.history'),
    path('approve/', views.BankStaffApprovalListView.as_view(), name='approve.list'),
    path('approve/<int:pk>/', views.BankStaffApproveView.as_view(), name='transaction.approve'),
    path('approve-history/', views.BankstaffTransactionHistoryView.as_view(), name='approve.history'),
]
