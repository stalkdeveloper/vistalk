# apps/roles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View

from apps.roles.models import Role, Permission, UserRole
from apps.roles.mixins import SystemUserMixin, PermissionRequiredMixin


# ─────────────────────────────────────────────────────────────
# List
# ─────────────────────────────────────────────────────────────

class RoleListView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_view_roles'

    def get(self, request):
        roles = Role.objects.prefetch_related('permissions', 'user_roles').order_by('name')
        return render(request, 'roles/index.html', {
            'roles':        roles,
            'total':        roles.count(),
            'perm_count':   Permission.objects.count(),
            'default_role': Role.objects.filter(is_default=True).first(),
        })


# ─────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────

class RoleCreateView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_create_roles'
    template_name = 'roles/create.html'

    def get(self, request):
        permissions = Permission.objects.all().order_by('group', 'display_name')
        return render(request, self.template_name, {
            'perm_groups':    _group_permissions(permissions),
            'selected_perm_ids': [],
        })

    def post(self, request):
        name             = request.POST.get('name', '').strip().lower().replace(' ', '_')
        display_name     = request.POST.get('display_name', '').strip()
        description      = request.POST.get('description', '').strip()
        is_default       = request.POST.get('is_default') == 'on'
        selected_perm_ids = list(map(int, request.POST.getlist('permissions')))

        errors = {}
        if not name:
            errors['name'] = 'Role name is required.'
        elif Role.objects.filter(name=name).exists():
            errors['name'] = 'A role with this name already exists.'
        if not display_name:
            errors['display_name'] = 'Display name is required.'

        if errors:
            permissions = Permission.objects.all().order_by('group', 'display_name')
            return render(request, self.template_name, {
                'perm_groups':       _group_permissions(permissions),
                'errors':            errors,
                'old':               request.POST,
                'selected_perm_ids': selected_perm_ids,
            })

        if is_default:
            Role.objects.filter(is_default=True).update(is_default=False)

        role = Role.objects.create(
            name=name, display_name=display_name,
            description=description, is_default=is_default,
        )
        role.permissions.set(Permission.objects.filter(id__in=selected_perm_ids))
        messages.success(request, f"Role '{role.display_name}' created.")
        return redirect('roles:index')


# ─────────────────────────────────────────────────────────────
# Edit
# ─────────────────────────────────────────────────────────────

class RoleEditView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_edit_roles'
    template_name = 'roles/edit.html'

    def get(self, request, pk):
        role         = get_object_or_404(Role, pk=pk)
        permissions  = Permission.objects.all().order_by('group', 'display_name')
        assigned_ids = set(role.permissions.values_list('id', flat=True))
        return render(request, self.template_name, {
            'role':              role,
            'perm_groups':       _group_permissions(permissions),
            'assigned_ids':      assigned_ids,
        })

    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)

        name             = request.POST.get('name', '').strip().lower().replace(' ', '_')
        display_name     = request.POST.get('display_name', '').strip()
        description      = request.POST.get('description', '').strip()
        is_default       = request.POST.get('is_default') == 'on'
        selected_perm_ids = list(map(int, request.POST.getlist('permissions')))

        errors = {}
        if not name:
            errors['name'] = 'Role name is required.'
        elif Role.objects.filter(name=name).exclude(pk=pk).exists():
            errors['name'] = 'A role with this name already exists.'
        if not display_name:
            errors['display_name'] = 'Display name is required.'

        if errors:
            permissions = Permission.objects.all().order_by('group', 'display_name')
            return render(request, self.template_name, {
                'role':              role,
                'perm_groups':       _group_permissions(permissions),
                'assigned_ids':      set(selected_perm_ids),
                'errors':            errors,
                'old':               request.POST,
            })

        if is_default:
            Role.objects.filter(is_default=True).exclude(pk=pk).update(is_default=False)

        role.name         = name
        role.display_name = display_name
        role.description  = description
        role.is_default   = is_default
        role.save()
        role.permissions.set(Permission.objects.filter(id__in=selected_perm_ids))
        messages.success(request, f"Role '{role.display_name}' updated.")
        return redirect('roles:index')


# ─────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────

class RoleDeleteView(SystemUserMixin, PermissionRequiredMixin, View):
    required_permission = 'can_delete_roles'

    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        if role.is_default:
            messages.error(request, f"Cannot delete '{role.display_name}' - it is the default role.")
            return redirect('roles:index')
        user_count = UserRole.objects.filter(role=role).count()
        if user_count:
            messages.error(
                request,
                f"Cannot delete '{role.display_name}' - {user_count} user(s) assigned to it.",
            )
            return redirect('roles:index')
        name = role.display_name
        role.delete()
        messages.success(request, f"Role '{name}' deleted.")
        return redirect('roles:index')


# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────

def _group_permissions(permissions):
    groups = {}
    for perm in permissions:
        groups.setdefault(perm.group, []).append(perm)
    return groups