from apps.users.models import User
from apps.roles.models import UserRole


def run(stdout, roles):
    stdout.write('\n👤 Seeding Users...')

    # System user
    system_user, created = User.objects.get_or_create(
        email='admin@vistalk.com',
        defaults={
            'username': 'system_admin',
            'user_type': 'system',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        system_user.set_password('Admin@123')
        system_user.save()
        UserRole.objects.get_or_create(user=system_user, role=roles['admin'])
        stdout.write('  ✅ Created: admin@vistalk.com / Admin@123')
    else:
        stdout.write('  ⏭  Exists: admin@vistalk.com')

    # Platform user
    platform_user, created = User.objects.get_or_create(
        email='user@vistalk.com',
        defaults={
            'username': 'test_user',
            'user_type': 'platform',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        platform_user.set_password('User@123')
        platform_user.save()
        UserRole.objects.get_or_create(user=platform_user, role=roles['user'])
        stdout.write('  ✅ Created: user@vistalk.com / User@123')
    else:
        stdout.write('  ⏭  Exists: user@vistalk.com')