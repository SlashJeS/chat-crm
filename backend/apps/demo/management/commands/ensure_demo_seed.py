from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run seed_demo when demo data is not present yet."

    def handle(self, *args, **options):
        if User.objects.filter(username="lead").exists():
            self.stdout.write("Demo data already present, skipping seed.")
            return

        self.stdout.write("Demo data not found, running seed_demo...")
        call_command("seed_demo")
