from django.core.management.base import BaseCommand
from staff.seeder import seed_permissions

class Command(BaseCommand):
    help = "Seed default custom permissions"

    def handle(self, *args, **kwargs):
        seed_permissions()
        self.stdout.write(self.style.SUCCESS("✅ Default permissions have been seeded."))
