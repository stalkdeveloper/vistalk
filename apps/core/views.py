# apps/core/views.py
from django.shortcuts import render, redirect
from django.views.generic import View

from apps.roles.mixins import LoginRequiredMixin, SystemUserMixin, get_user_permissions, get_user_roles
from apps.users.models import User
from apps.roles.models import Role, Permission


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.user_type == 'system':
            return redirect('core:admin_dashboard')
        return render(request, 'core/dashboard.html', {
            'user_roles':       get_user_roles(request.user),
            'user_permissions': get_user_permissions(request.user),
        })


class AdminDashboardView(SystemUserMixin, View):
    def get(self, request):
        stats = [
            {'label': 'Total Users',    'value': User.objects.count()},
            {'label': 'Platform Users', 'value': User.objects.filter(user_type='platform').count()},
            {'label': 'System Users',   'value': User.objects.filter(user_type='system').count()},
            {'label': 'Total Roles',    'value': Role.objects.count()},
            {'label': 'Permissions',    'value': Permission.objects.count()},
        ]
        return render(request, 'core/admin_dashboard.html', {
            'stats':            stats,
            'user_roles':       get_user_roles(request.user),
            'user_permissions': get_user_permissions(request.user),
        })