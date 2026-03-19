# apps/roles/templatetags/rbac_tags.py
from django import template
from apps.roles.mixins import has_permission, has_role

register = template.Library()


@register.filter(name='has_perm')
def user_has_perm(user, permission_name):
    """
    Template usage:
        {% load rbac_tags %}
        {% if request.user|has_perm:"can_create_roles" %}
    """
    return has_permission(user, permission_name)


@register.filter(name='has_role')
def user_has_role(user, role_name):
    """
    Template usage:
        {% if request.user|has_role:"admin" %}
    """
    return has_role(user, role_name)