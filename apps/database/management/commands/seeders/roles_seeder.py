from apps.roles.models import Role


def run(stdout, permissions):
    stdout.write('\n🎭 Seeding Roles...')

    # Admin - all permissions
    admin_role, created = Role.objects.get_or_create(
        name='admin',
        defaults={
            'display_name': 'Administrator',
            'description': 'Full access to everything',
            'is_default': False,
        }
    )
    admin_role.permissions.set(list(permissions.values()))
    stdout.write(f"  {'✅ Created' if created else '⏭  Exists'}: Role 'admin'")

    # User - basic permissions, default for new registrations
    user_role, created = Role.objects.get_or_create(
        name='user',
        defaults={
            'display_name': 'User',
            'description': 'Standard platform user',
            'is_default': True,
        }
    )
    user_role.permissions.set([
        permissions['can_view_dashboard'],
        permissions['can_create_post'],
        permissions['can_edit_post'],
    ])
    stdout.write(f"  {'✅ Created' if created else '⏭  Exists'}: Role 'user' (default)")

    return {'admin': admin_role, 'user': user_role}