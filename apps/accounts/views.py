# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import View
from django.utils.crypto import get_random_string
from django.core.cache import cache

from .forms import (
    PlatformRegisterForm, PlatformLoginForm, SystemLoginForm,
    ForgotPasswordForm, SystemForgotPasswordForm, ResetPasswordForm,
)
from apps.roles.models import Role, UserRole
from apps.users.models import User


# ─────────────────────────────────────────────────────────────
# Public / Home
# ─────────────────────────────────────────────────────────────

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


# ─────────────────────────────────────────────────────────────
# Platform (regular user) auth
# ─────────────────────────────────────────────────────────────

class PlatformRegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, self.template_name, {'form': PlatformRegisterForm()})

    def post(self, request):
        form = PlatformRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.user_type  = 'platform'
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name  = form.cleaned_data.get('last_name', '')
            user.save()
            try:
                default_role = Role.objects.get(is_default=True)
                UserRole.objects.create(user=user, role=default_role)
            except Role.DoesNotExist:
                pass
            login(request, user)
            messages.success(request, f"Welcome, {user.get_full_name()}!")
            return redirect('core:dashboard')
        return render(request, self.template_name, {'form': form})


class PlatformLoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, self.template_name, {'form': PlatformLoginForm(request)})

    def post(self, request):
        form = PlatformLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.user_type == 'system':
                messages.error(request, "Staff must use the admin portal.")
                return redirect('accounts:system_login')
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name()}!")
            return redirect('core:dashboard')
        return render(request, self.template_name, {'form': form})


class ForgotPasswordView(View):
    template_name = 'accounts/forgot_password.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ForgotPasswordForm()})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email     = form.cleaned_data['email']
            token     = get_random_string(64)
            cache_key = f'pwd_reset_platform_{token}'
            cache.set(cache_key, email, timeout=3600)
            reset_url = request.build_absolute_uri(f'/reset-password/{token}/')
            # In production replace with email send:
            messages.success(request, f"Reset link (dev only): {reset_url}")
            return redirect('accounts:forgot_password')
        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    template_name = 'accounts/reset_password.html'

    def _get_email(self, token):
        return cache.get(f'pwd_reset_platform_{token}')

    def get(self, request, token):
        if not self._get_email(token):
            messages.error(request, "Reset link is invalid or has expired.")
            return redirect('accounts:forgot_password')
        return render(request, self.template_name, {'form': ResetPasswordForm(), 'token': token})

    def post(self, request, token):
        email = self._get_email(token)
        if not email:
            messages.error(request, "Reset link is invalid or has expired.")
            return redirect('accounts:forgot_password')
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=email)
            user.set_password(form.cleaned_data['password'])
            user.save()
            cache.delete(f'pwd_reset_platform_{token}')
            messages.success(request, "Password reset successfully! Please login.")
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': form, 'token': token})


# ─────────────────────────────────────────────────────────────
# System (staff) auth
# ─────────────────────────────────────────────────────────────

class SystemLoginView(View):
    template_name = 'accounts/system_login.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.user_type == 'system':
            return redirect('core:admin_dashboard')
        return render(request, self.template_name, {'form': SystemLoginForm(request)})

    def post(self, request):
        form = SystemLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Welcome to the staff portal.")
            return redirect('core:admin_dashboard')
        return render(request, self.template_name, {'form': form})


class SystemForgotPasswordView(View):
    template_name = 'accounts/system_forgot_password.html'

    def get(self, request):
        return render(request, self.template_name, {'form': SystemForgotPasswordForm()})

    def post(self, request):
        form = SystemForgotPasswordForm(request.POST)
        if form.is_valid():
            email     = form.cleaned_data['email']
            token     = get_random_string(64)
            cache_key = f'pwd_reset_system_{token}'
            cache.set(cache_key, email, timeout=3600)
            reset_url = request.build_absolute_uri(f'/admin/reset-password/{token}/')
            # In production replace with email send:
            messages.success(request, f"Reset link (dev only): {reset_url}")
            return redirect('accounts:system_forgot_password')
        return render(request, self.template_name, {'form': form})


class SystemResetPasswordView(View):
    template_name = 'accounts/system_reset_password.html'

    def _get_email(self, token):
        return cache.get(f'pwd_reset_system_{token}')

    def get(self, request, token):
        if not self._get_email(token):
            messages.error(request, "Reset link is invalid or has expired.")
            return redirect('accounts:system_forgot_password')
        return render(request, self.template_name, {'form': ResetPasswordForm(), 'token': token})

    def post(self, request, token):
        email = self._get_email(token)
        if not email:
            messages.error(request, "Reset link is invalid or has expired.")
            return redirect('accounts:system_forgot_password')
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=email)
            user.set_password(form.cleaned_data['password'])
            user.save()
            cache.delete(f'pwd_reset_system_{token}')
            messages.success(request, "Password reset successfully! Please login.")
            return redirect('accounts:system_login')
        return render(request, self.template_name, {'form': form, 'token': token})


# ─────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────

class LogoutView(View):
    def get(self, request):
        user_type = request.user.user_type if request.user.is_authenticated else 'platform'
        logout(request)
        messages.info(request, "Logged out successfully.")
        return redirect('accounts:system_login' if user_type == 'system' else 'accounts:login')