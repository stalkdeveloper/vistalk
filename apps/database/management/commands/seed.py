# # apps/users/management/commands/seed.py
# from django.core.management.base import BaseCommand
# from django.db import transaction
# from apps.users.models import User
# from apps.roles.models import Role, Permission, UserRole


# class Command(BaseCommand):
#     help = 'Seed default roles, permissions, and test users'

#     @transaction.atomic
#     def handle(self, *args, **kwargs):
#         self.stdout.write('🌱 Seeding database...')

#         # ── 1. Create Permissions ──────────────────────────────────────────
#         permissions_data = [
#             {'name': 'can_manage_users',    'display_name': 'Can Manage Users',    'group': 'users'},
#             {'name': 'can_view_users',      'display_name': 'Can View Users',      'group': 'users'},
#             {'name': 'can_manage_roles',    'display_name': 'Can Manage Roles',    'group': 'roles'},
#             {'name': 'can_create_post',     'display_name': 'Can Create Post',     'group': 'posts'},
#             {'name': 'can_edit_post',       'display_name': 'Can Edit Post',       'group': 'posts'},
#             {'name': 'can_delete_post',     'display_name': 'Can Delete Post',     'group': 'posts'},
#             {'name': 'can_view_dashboard',  'display_name': 'Can View Dashboard',  'group': 'core'},
#         ]

#         permissions = {}
#         for p in permissions_data:
#             perm, created = Permission.objects.get_or_create(name=p['name'], defaults=p)
#             permissions[p['name']] = perm
#             status = '✅ Created' if created else '⏭  Exists'
#             self.stdout.write(f"  {status}: Permission '{p['name']}'")

#         # ── 2. Create Roles ────────────────────────────────────────────────
#         # Admin role - all permissions
#         admin_role, created = Role.objects.get_or_create(
#             name='admin',
#             defaults={
#                 'display_name': 'Administrator',
#                 'description': 'Full access to everything',
#                 'is_default': False,
#             }
#         )
#         admin_role.permissions.set(list(permissions.values()))
#         self.stdout.write(f"  {'✅ Created' if created else '⏭  Exists'}: Role 'admin'")

#         # User role - basic permissions (default for new registrations)
#         user_role, created = Role.objects.get_or_create(
#             name='user',
#             defaults={
#                 'display_name': 'User',
#                 'description': 'Standard platform user',
#                 'is_default': True,
#             }
#         )
#         user_role.permissions.set([
#             permissions['can_view_dashboard'],
#             permissions['can_create_post'],
#             permissions['can_edit_post'],
#         ])
#         self.stdout.write(f"  {'✅ Created' if created else '⏭  Exists'}: Role 'user' (default)")

#         # ── 3. Create System User (Staff/Admin) ───────────────────────────
#         system_email = 'admin@vistalk.com'
#         system_user, created = User.objects.get_or_create(
#             email=system_email,
#             defaults={
#                 'username': 'system_admin',
#                 'user_type': 'system',
#                 'is_staff': True,
#                 'is_superuser': True,
#             }
#         )
#         if created:
#             system_user.set_password('Admin@123')
#             system_user.save()
#             UserRole.objects.get_or_create(user=system_user, role=admin_role)
#             self.stdout.write('  ✅ Created: System user admin@vistalk.com / Admin@123')
#         else:
#             self.stdout.write('  ⏭  Exists: System user admin@vistalk.com')

#         # ── 4. Create Platform User (Web User) ────────────────────────────
#         platform_email = 'user@vistalk.com'
#         platform_user, created = User.objects.get_or_create(
#             email=platform_email,
#             defaults={
#                 'username': 'test_user',
#                 'user_type': 'platform',
#                 'is_staff': False,
#                 'is_superuser': False,
#             }
#         )
#         if created:
#             platform_user.set_password('User@123')
#             platform_user.save()
#             UserRole.objects.get_or_create(user=platform_user, role=user_role)
#             self.stdout.write('  ✅ Created: Platform user user@vistalk.com / User@123')
#         else:
#             self.stdout.write('  ⏭  Exists: Platform user user@vistalk.com')

#         # ── Summary ────────────────────────────────────────────────────────
#         self.stdout.write('\n' + '─' * 50)
#         self.stdout.write(self.style.SUCCESS('✅ Seeding complete!\n'))
#         self.stdout.write('🔐 System Login:   http://localhost:8000/admin/login/')
#         self.stdout.write('   Email:    admin@vistalk.com')
#         self.stdout.write('   Password: Admin@123\n')
#         self.stdout.write('🌐 Platform Login: http://localhost:8000/login/')
#         self.stdout.write('   Email:    user@vistalk.com')
#         self.stdout.write('   Password: User@123')
#         self.stdout.write('─' * 50)

from django.core.management.base import BaseCommand
from django.db import transaction

from .seeders import permissions_seeder, roles_seeder, users_seeder


class Command(BaseCommand):
    help = 'Seed database with default data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Starting seed...')

        permissions = permissions_seeder.run(self.stdout)
        roles = roles_seeder.run(self.stdout, permissions)
        users_seeder.run(self.stdout, roles)

        self.stdout.write('\n' + '─' * 50)
        self.stdout.write(self.style.SUCCESS('✅ All seeders complete!\n'))
        self.stdout.write('🔐 System:   http://localhost:8000/admin/login/')
        self.stdout.write('   admin@vistalk.com  /  Admin@123\n')
        self.stdout.write('🌐 Platform: http://localhost:8000/login/')
        self.stdout.write('   user@vistalk.com  /  User@123')
        self.stdout.write('─' * 50)