from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed demo CRM data"

    def handle(self, *args, **options):
        self.stdout.write("Demo seed not implemented yet.")
