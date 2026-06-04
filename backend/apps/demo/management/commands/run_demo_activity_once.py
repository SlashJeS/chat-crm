from django.core.management.base import BaseCommand

from apps.demo.activity import run_demo_activity_once


class Command(BaseCommand):
    help = "Generate one batch of demo fan messages."

    def handle(self, *args, **options):
        result = run_demo_activity_once()
        self.stdout.write(str(result))
