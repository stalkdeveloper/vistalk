from apps.roles.models import Permission

PERMISSIONS = [
    # User Management
    {'name': 'can_access_users',   'display_name': 'Can Access Users',   'group': 'users'},
    {'name': 'can_view_users',     'display_name': 'Can View Users',     'group': 'users'},
    {'name': 'can_create_users',   'display_name': 'Can Create Users',   'group': 'users'},
    {'name': 'can_edit_users',     'display_name': 'Can Edit Users',     'group': 'users'},
    {'name': 'can_delete_users',   'display_name': 'Can Delete Users',   'group': 'users'},


    # Role Management
    {'name': 'can_access_roles',    'display_name': 'Can Access Roles',    'group': 'roles'},
    {'name': 'can_view_roles',     'display_name': 'Can View Roles',     'group': 'roles'},
    {'name': 'can_create_roles',   'display_name': 'Can Create Roles',   'group': 'roles'},
    {'name': 'can_edit_roles',     'display_name': 'Can Edit Roles',     'group': 'roles'},
    {'name': 'can_delete_roles',   'display_name': 'Can Delete Roles',   'group': 'roles'},

    # Tasks Management
    {'name': 'can_access_tasks',   'display_name': 'Can Access Tasks',   'group': 'tasks'},
    {'name': 'can_view_tasks',     'display_name': 'Can View Tasks',     'group': 'tasks'},
    {'name': 'can_create_tasks',   'display_name': 'Can Create Tasks',   'group': 'tasks'},
    {'name': 'can_edit_tasks',     'display_name': 'Can Edit Tasks',     'group': 'tasks'},
    {'name': 'can_delete_tasks',   'display_name': 'Can Delete Tasks',   'group': 'tasks'},

    # Organization Management
    
    # Core / Dashboard
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