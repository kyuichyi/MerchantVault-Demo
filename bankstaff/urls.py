"""
URL configuration for the Bankstaff app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('manage/', views.MerchantListView.as_view(), name='merchant.list'),
    path('manage/<int:pk>/', views.MerchantDetailView.as_view(), name='merchant.detail'),
    path('manage/<int:pk>/edit', views.MerchantUpdateView.as_view(), name='merchant.update'),
    path('manage/<int:pk>/delete', views.MerchantDeleteView.as_view(), name='merchant.delete'),
]
