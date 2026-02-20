"""Configuration de l'application annonces."""

from django.apps import AppConfig


class AnnoncesConfig(AppConfig):
    """Configuration Django de l'application annonces."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "annonces"
    label = "catalogue"

