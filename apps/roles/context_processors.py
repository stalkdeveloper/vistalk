from .mixins import get_user_roles, get_user_permissions, has_permission, has_role


def rbac_context(request):
    """Inject user roles and permissions into every template"""
    if request.user.is_authenticated:
        return {
            'user_roles': get_user_roles(request.user),
            'user_permissions': get_user_permissions(request.user),
        }
    return {
        'user_roles': [],
        'user_permissions': [],
    }