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