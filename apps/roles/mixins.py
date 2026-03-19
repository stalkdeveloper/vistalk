# apps/roles/mixins.py
"""
RBAC helpers for Vistalk.

Usage in CBVs
─────────────
    class MyView(SystemUserMixin, PermissionRequiredMixin, View):
        required_permission = 'can_edit_users'

    # No required_permission → just blocks non-system users
    class DashView(SystemUserMixin, View):
        pass

Usage as decorators (FBVs)
──────────────────────────
    @system_required
    @permission_required('can_delete_roles')
    def my_view(request):
        ...
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


# ─────────────────────────────────────────────────────────────
# Low-level helpers (used in templates & other modules)
# ─────────────────────────────────────────────────────────────

def has_permission(user, permission_name: str) -> bool:
    """Return True if the user holds *permission_name* through any role."""
    if not user or not user.is_authenticated:
        return False
    return user.user_roles.filter(
        role__permissions__name=permission_name
    ).exists()


def has_role(user, role_name: str) -> bool:
    """Return True if the user is assigned *role_name*."""
    if not user or not user.is_authenticated:
        return False
    return user.user_roles.filter(role__name=role_name).exists()


def get_user_permissions(user):
    """Return a queryset of all Permission objects the user holds."""
    from apps.roles.models import Permission
    return Permission.objects.filter(
        roles__user_roles__user=user
    ).distinct()


def get_user_roles(user):
    """Return a queryset of all Role objects assigned to the user."""
    from apps.roles.models import Role
    return Role.objects.filter(user_roles__user=user)


# ─────────────────────────────────────────────────────────────
# Class-Based View Mixins
# ─────────────────────────────────────────────────────────────

class LoginRequiredMixin:
    """Redirect unauthenticated requests to the appropriate login page."""
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class SystemUserMixin(LoginRequiredMixin):
    """
    Gate: only system-type users may pass.
    Non-system authenticated users are sent to the platform dashboard.
    Unauthenticated users are sent to the staff login page.
    """
    login_url = '/admin/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        if request.user.user_type != 'system':
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)


class PermissionRequiredMixin:
    """
    Gate: user must hold `required_permission`.

    Set the class attribute on the view:
        required_permission = 'can_create_users'

    Returns 403 if permission is missing.
    Must be used *after* SystemUserMixin in the MRO so authentication
    and user-type checks happen first.
    """
    required_permission: str = None

    def dispatch(self, request, *args, **kwargs):
        if self.required_permission and not has_permission(request.user, self.required_permission):
            return HttpResponseForbidden(
                f"You don't have the required permission: '{self.required_permission}'."
            )
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin:
    """
    Gate: user must hold `required_role`.
    """
    required_role: str = None

    def dispatch(self, request, *args, **kwargs):
        if self.required_role and not has_role(request.user, self.required_role):
            return HttpResponseForbidden(
                f"You don't have the required role: '{self.required_role}'."
            )
        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────
# Function-Based View Decorators
# ─────────────────────────────────────────────────────────────

def system_required(view_func):
    """Ensure the user is authenticated and is a system user."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:system_login')
        if request.user.user_type != 'system':
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required(permission_name: str):
    """
    Decorator factory for FBVs.

        @permission_required('can_delete_roles')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if not has_permission(request.user, permission_name):
                return HttpResponseForbidden("Permission denied.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def role_required(role_name: str):
    """
    Decorator factory for FBVs.

        @role_required('admin')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if not has_role(request.user, role_name):
                return HttpResponseForbidden("Role required.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator