from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


class RBACMixin:
    """
    Mixin for class-based views.
    Usage:
        class MyView(RBACMixin, View):
            required_permission = 'can_create_post'
    """
    required_permission = None
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if self.required_permission:
            if not has_permission(request.user, self.required_permission):
                return HttpResponseForbidden("You don't have permission.")

        if self.required_role:
            if not has_role(request.user, self.required_role):
                return HttpResponseForbidden("You don't have the required role.")

        return super().dispatch(request, *args, **kwargs)


def has_permission(user, permission_name):
    """Check if user has a specific permission through any of their roles"""
    return user.user_roles.filter(
        role__permissions__name=permission_name
    ).exists()


def has_role(user, role_name):
    """Check if user has a specific role"""
    return user.user_roles.filter(role__name=role_name).exists()


def get_user_permissions(user):
    """Get all permissions for a user"""
    from apps.roles.models import Permission
    return Permission.objects.filter(
        roles__user_roles__user=user
    ).distinct()


def get_user_roles(user):
    """Get all roles for a user"""
    from apps.roles.models import Role
    return Role.objects.filter(user_roles__user=user)


# ─── Decorators for function-based views ────────────────────────────────────

def permission_required(permission_name):
    """
    Usage:
        @permission_required('can_delete_post')
        def my_view(request):
            ...
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


def role_required(role_name):
    """
    Usage:
        @role_required('admin')
        def my_view(request):
            ...
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