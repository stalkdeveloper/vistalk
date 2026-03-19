# apps/users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View

from apps.users.models import User
from apps.roles.models import Role, UserRole
from apps.roles.mixins import SystemUserMixin, PermissionRequiredMixin, get_user_roles
from .forms import UserCreateForm, UserEditForm


# ─────────────────────────────────────────────────────────────
# List
# ─────────────────────────────────────────────────────────────

class UserListView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_view_users'

    def get(self, request):
        search    = request.GET.get('search', '').strip()
        user_type = request.GET.get('user_type', '').strip()

        qs = User.objects.prefetch_related('user_roles__role').order_by('-date_joined')
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(username__icontains=search)
        if user_type:
            qs = qs.filter(user_type=user_type)

        from apps.roles.mixins import has_permission
        return render(request, 'users/index.html', {
            'users':            qs,
            'search':           search,
            'user_type_filter': user_type,
            'total':            User.objects.count(),
            'platform_count':   User.objects.filter(user_type='platform').count(),
            'system_count':     User.objects.filter(user_type='system').count(),
            # Permission flags for template buttons
            'can_create': has_permission(request.user, 'can_create_users'),
            'can_edit':   has_permission(request.user, 'can_edit_users'),
            'can_delete': has_permission(request.user, 'can_delete_users'),
        })


# ─────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────

class UserCreateView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_create_users'
    template_name = 'users/create.html'

    def get(self, request):
        return render(request, self.template_name, {'form': UserCreateForm()})

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name  = form.cleaned_data.get('first_name', '')
            user.middle_name = form.cleaned_data.get('middle_name', '')
            user.last_name   = form.cleaned_data.get('last_name', '')
            # Auto-manage is_staff based on user_type
            user.is_staff = (user.user_type == 'system')
            user.save()

            selected_role = form.cleaned_data.get('role')
            if selected_role:
                UserRole.objects.get_or_create(user=user, role=selected_role)

            messages.success(request, f"User '{user.get_full_name()}' created successfully.")
            return redirect('users:index')

        return render(request, self.template_name, {'form': form})


# ─────────────────────────────────────────────────────────────
# Edit
# ─────────────────────────────────────────────────────────────

class UserEditView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_edit_users'
    template_name = 'users/edit.html'

    def get(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        form   = UserEditForm(instance=target)
        return render(request, self.template_name, {'form': form, 'target_user': target})

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        form   = UserEditForm(request.POST, instance=target)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name  = form.cleaned_data.get('first_name', '')
            user.middle_name = form.cleaned_data.get('middle_name', '')
            user.last_name   = form.cleaned_data.get('last_name', '')
            user.is_staff    = (user.user_type == 'system')
            user.save()

            # Replace role (single role per user)
            UserRole.objects.filter(user=user).delete()
            selected_role = form.cleaned_data.get('role')
            if selected_role:
                UserRole.objects.create(user=user, role=selected_role)

            messages.success(request, f"User '{user.get_full_name()}' updated successfully.")
            return redirect('users:index')

        return render(request, self.template_name, {'form': form, 'target_user': target})


# ─────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────

class UserDeleteView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_delete_users'

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)

        # Cannot delete yourself
        if target == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect('users:index')

        # Cannot delete superusers / system admins
        if target.is_superuser:
            messages.error(request, "Super-admin accounts cannot be deleted.")
            return redirect('users:index')

        name = target.get_full_name()
        target.delete()
        messages.success(request, f"User '{name}' deleted.")
        return redirect('users:index')


# ─────────────────────────────────────────────────────────────
# Toggle active
# ─────────────────────────────────────────────────────────────

class UserToggleActiveView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_edit_users'

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target == request.user:
            messages.error(request, "You cannot deactivate yourself.")
            return redirect('users:index')

        target.is_active = not target.is_active
        target.save()
        status = "activated" if target.is_active else "deactivated"
        messages.success(request, f"User '{target.get_full_name()}' {status}.")
        return redirect('users:index')