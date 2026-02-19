"""Configuration de l'application catalogue."""

from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    """Configuration Django de l'application catalogue."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "catalogue"

