from apps.roles.models import Permission


PERMISSIONS = [
    {'name': 'can_manage_users',   'display_name': 'Can Manage Users',   'group': 'users'},
    {'name': 'can_view_users',     'display_name': 'Can View Users',     'group': 'users'},
    {'name': 'can_manage_roles',   'display_name': 'Can Manage Roles',   'group': 'roles'},
    {'name': 'can_create_post',    'display_name': 'Can Create Post',    'group': 'posts'},
    {'name': 'can_edit_post',      'display_name': 'Can Edit Post',      'group': 'posts'},
    {'name': 'can_delete_post',    'display_name': 'Can Delete Post',    'group': 'posts'},
    {'name': 'can_view_dashboard', 'display_name': 'Can View Dashboard', 'group': 'core'},
]


def run(stdout):
    stdout.write('\n📋 Seeding Permissions...')
    permissions = {}
    for p in PERMISSIONS:
        perm, created = Permission.objects.get_or_create(name=p['name'], defaults=p)
        permissions[p['name']] = perm
        status = '  ✅ Created' if created else '  ⏭  Exists'
        stdout.write(f"{status}: {p['name']}")
    return permissions