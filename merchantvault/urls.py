"""
URL configuration for merchantvault project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin #pylint: disable=unused-import
from django.urls import path, include

urlpatterns = [
    #user paths
    path('', include('home.urls')),
    path('', include('bankstaff.urls')),
    path('', include('merchant.urls')),
    path('', include('transaction.urls')),
]
