# apps/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from apps.users.models import User
from apps.roles.models import Role, Permission


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class DashboardView(View):
    def get(self, request):
        if request.user.user_type == 'system':
            return redirect('core:admin_dashboard')
        return render(request, 'core/dashboard.html')


@method_decorator(login_required(login_url='/admin/login/'), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        if request.user.user_type != 'system':
            return redirect('core:dashboard')

        stats = [
            {'label': 'Total Users',    'value': User.objects.count()},
            {'label': 'Platform Users', 'value': User.objects.filter(user_type='platform').count()},
            {'label': 'Staff Users',    'value': User.objects.filter(user_type='system').count()},
            {'label': 'Total Roles',    'value': Role.objects.count()},
            {'label': 'Permissions',    'value': Permission.objects.count()},
        ]
        return render(request, 'core/admin_dashboard.html', {'stats': stats})