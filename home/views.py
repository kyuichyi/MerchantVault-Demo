#pylint: disable=too-many-ancestors, missing-function-docstring

"""
This module contains views for the Home app.
"""

from io import BytesIO
import base64
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.cache import cache
from django.utils import timezone
from django.http import HttpResponse

from django_otp.plugins.otp_email.models import EmailDevice

from transaction.models import Transaction

from .mixins import MerchantOTPRequiredMixin, BankStaffOTPRequiredMixin
from .models import AccessLog, User
from .forms import MerchantSignUpForm

class MerchantSignUpView(CreateView):
    """
    View for merchant sign-up.
    """
    model = User
    form_class = MerchantSignUpForm
    template_name = 'home/signup.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('overview/')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'merchant'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            email_device, create = EmailDevice.objects.get_or_create(user=user) #pylint: disable=unused-variable
            email_device.generate_challenge()
            email_device.confirmed = False
            email_device.save()
            return redirect('verify')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

class LogoutInterfaceView(LogoutView):
    """
    View for user logout.
    """
    template_name = 'home/logout.html'

class MerchantHomeView(MerchantOTPRequiredMixin, TemplateView):
    """
    View for merchant home.
    """
    template_name = 'home/merchant_home.html'
    extra_context = {'today': datetime.today()}
    login_url = 'login'

class BankStaffHomeView(BankStaffOTPRequiredMixin, TemplateView):
    """
    View for bankstaff home.
    """
    template_name = 'home/bankstaff_home.html'
    extra_context = {'today': datetime.today()}
    login_url = 'login'

class AccessLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View for access logs.
    """
    model = AccessLog
    template_name = 'home/accesslog_list.html'
    context_object_name = 'access_logs'

    def get_queryset(self):
        query = self.request.GET.get("q")
        access_logs = AccessLog.objects.all() #pylint: disable=E1101

        if query:
            access_logs = access_logs.filter(
                action__icontains=query
            ) | access_logs.filter(
                details__icontains=query
            ) | access_logs.filter(
                user__username__icontains=query
            )

        return access_logs

    def test_func(self):
        return hasattr(self.request.user, 'bankstaff')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return self.render_to_response(
                {'error_message': 'Access restricted to Bank Staff only'},
                status=403)
        return super().handle_no_permission()

FAILED_ATTEMPT_LIMIT = 1
TIME_LIMIT = 300

class LoginInterfaceView(LoginView):
    """
    View for user log in.
    """
    template_name = 'home/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        cache.delete(user.username)

        AccessLog.objects.create( #pylint: disable=E1101
            user=user,
            action="Login Successful",
            timestamp=timezone.now(),
            details=f"User {user.username} logged in successfully."
        )

        email_device, create = EmailDevice.objects.get_or_create(user=user) #pylint: disable=unused-variable
        email_device.generate_challenge()
        email_device.confirmed = False
        email_device.save()

        return redirect('verify')

    def form_invalid(self, form):
        username = self.request.POST.get('username')
        track_failed_login_attempt(username)
        return super().form_invalid(form)

def track_failed_login_attempt(username):
    attempts = cache.get(username, [])
    attempts = [attempt for attempt in attempts if (timezone.now() - attempt).seconds < TIME_LIMIT]
    attempts.append(timezone.now())
    cache.set(username, attempts, TIME_LIMIT)

    if len(attempts) >= FAILED_ATTEMPT_LIMIT:
        AccessLog.objects.create( #pylint: disable=E1101
            user=None,
            action="Suspicious Activity Detected",
            timestamp=timezone.now(),
            details=f"Suspicious activity detected for username: {username} - Too many failed login attempts" #pylint: disable=line-too-long
        )
        cache.delete(username)

class OTPVerificationView(LoginRequiredMixin, TemplateView):
    """
    View for email OTP verification.
    """
    template_name = 'home/verify.html'

    def post(self, request):
        otp = request.POST.get('otp')
        email_device = EmailDevice.objects.get(user=request.user)

        if email_device.verify_token(otp):
            email_device.confirmed = True
            email_device.save()

            # Redirect to the appropriate home page based on user type after OTP verification
            return redirect(self.get_success_url())
        return render(request, self.template_name, {'error': 'Invalid OTP'})

    def get_success_url(self):
        if hasattr(self.request.user, 'merchant'):
            return reverse_lazy('merchant.home')
        if hasattr(self.request.user, 'bankstaff'):
            return reverse_lazy('bankstaff.home')
        return reverse_lazy('login')

def anonymize_data(request):

    if not hasattr(request.user, 'bankstaff'):
        raise PermissionDenied

    context = {
        'k_values': range(3, 11),
        'anonymized_data': None,
        'privacy_data': None,
        'utility_data': None,
        'k_value': None,
        'show_results': False
    }

    if request.method == 'POST':
        k_value = int(request.POST.get('k_value'))
        context['k_value'] = k_value

        transactions = Transaction.objects.values('amount', #pylint: disable=E1101
                                                  'date',
                                                  'status',
                                                  'approver',
                                                  'receiver_id',
                                                  'sender_id')
        df = pd.DataFrame(transactions)

        anonymized_df = apply_k_anonymization(df, k_value)
        context['anonymized_data'] = anonymized_df.to_html(index=False,
                                                           classes="table table-bordered")
        context['show_results'] = True

        context['privacy_data'] = generate_privacy_utility_graph()

    return render(request, 'home/anonymize_data.html', context)

def apply_k_anonymization(df, k):
    range_multiplier = max(1, k // 3)

    #pylint: disable=line-too-long
    df['amount'] = df['amount'].apply(lambda x: f"{round(x / (100 * range_multiplier)) * 100 * range_multiplier} - {round(x / (100 * range_multiplier) + 1) * 100 * range_multiplier}")

    if k <= 5:
        df['date'] = df['date'].apply(lambda x: x.strftime("%Y-%m"))
    elif k <= 8:
        df['date'] = df['date'].apply(lambda x: f"{x.year}-Q{(x.month - 1) // 3 + 1}")
    else:
        df['date'] = df['date'].apply(lambda x: x.strftime("%Y"))

    if k >= 8:
        df['status'] = 'Reviewed'
    else:
        df['status'] = df['status'].apply(lambda x: 'Reviewed' if x == 'approved' or x == 'pending' else 'Rejected') #pylint: disable=R1714

    if k <= 5:
        df['approver'] = df['approver'].apply(lambda x: (x[0] + '*') if pd.notnull(x) and x else 'N/A')
    else:
        df['approver'] = 'A*'

    if k <= 5:
        df['receiver_id'] = df['receiver_id'].apply(lambda x: f"ID-{str(x)[0]}*")
        df['sender_id'] = df['sender_id'].apply(lambda x: f"ID-{str(x)[0]}*")
    else:
        df['receiver_id'] = 'ID-*'
        df['sender_id'] = 'ID-*'

    return df

def generate_privacy_utility_graph():
    k_values = range(3, 11)

    privacy_values = [np.log(k) / np.log(10) for k in k_values]

    utility_values = [np.exp(-0.3 * (k - 3)) for k in k_values]

    plt.figure(figsize=(8, 6))
    plt.plot(k_values, utility_values, label="Data Utility", color="blue")
    plt.plot(k_values, privacy_values, label="Data Privacy", color="orange")
    plt.xlabel("k value")
    plt.ylabel("Measure (0 to 1)")
    plt.title("Data Utility vs. Data Privacy")
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return graph_base64

def download_anonymized_data(request):
    k_value = int(request.GET.get('k'))
    transactions = Transaction.objects.values('amount', 'date', 'status', 'approver', 'receiver_id', 'sender_id') #pylint: disable=line-too-long,E1101
    df = pd.DataFrame(transactions)
    anonymized_df = apply_k_anonymization(df, k_value)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="anonymized_data_k{k_value}.csv"'
    anonymized_df.to_csv(path_or_buf=response, index=False)
    return response
