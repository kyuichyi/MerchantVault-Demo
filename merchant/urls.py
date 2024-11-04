#pylint: disable=line-too-long

"""
URL configuration for the merchant app.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('account/', views.UserDetailView.as_view(), name='account.detail'),
    path('account/edit/', views.UserUpdateView.as_view(), name='account.update'),
    path('account/change-password/', views.UserChangePasswordView.as_view(), name='account.change_password'),
    path('account/change-username/', views.UserChangeUsernameView.as_view(), name='account.change_username'),
]
