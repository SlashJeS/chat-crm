from django.db import models


class ModelAccount(models.Model):
    name = models.CharField(max_length=255)
    avatar_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name
