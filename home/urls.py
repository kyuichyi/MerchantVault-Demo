#pylint: disable=line-too-long

"""
URL configuration for the home app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.LoginInterfaceView.as_view(), name='login'),
    path('overview/', views.MerchantHomeView.as_view(), name='merchant.home'),
    path('home/', views.BankStaffHomeView.as_view(), name='bankstaff.home'),
    path('login/', views.LoginInterfaceView.as_view(), name='login'),
    path('logout/', views.LogoutInterfaceView.as_view(), name='logout'),
    path('signup/', views.MerchantSignUpView.as_view(), name='signup'),
    path('verify/', views.OTPVerificationView.as_view(), name='verify'),
    path('accesslogs/', views.AccessLogListView.as_view(), name='accesslog_list'),
    path('anonymize_data/', views.anonymize_data, name='anonymize_data'),
    path('download_anonymized_data/', views.download_anonymized_data, name='download_anonymized_data'),
]
