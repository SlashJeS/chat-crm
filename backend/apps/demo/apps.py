from django.apps import AppConfig


class DemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.demo"

    def ready(self):
        from apps.demo.runner import start_demo_activity_runner

        start_demo_activity_runner()
