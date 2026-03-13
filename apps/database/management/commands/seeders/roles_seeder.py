from apps.roles.models import Role

def run(stdout, permissions):
    stdout.write('\n🎭 Seeding Roles...')

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
    ])
    
    stdout.write(f"  {'✅ Created' if created else '⏭  Exists'}: Role 'user' (default)")

    return {'admin': admin_role, 'user': user_role}
