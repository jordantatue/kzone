"""Administration des modeles profil."""

from django.contrib import admin

from .models import AvisConfiance, ProfilUtilisateur


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    """Configuration admin des profils utilisateurs."""

    list_display = (
        "utilisateur",
        "moyen_paiement_prefere",
        "numero_paiement",
        "badge_trustcam",
        "date_mise_a_jour",
    )
    list_filter = ("badge_trustcam", "moyen_paiement_prefere")
    search_fields = ("utilisateur__username", "utilisateur__email", "numero_paiement")


@admin.register(AvisConfiance)
class AvisConfianceAdmin(admin.ModelAdmin):
    """Configuration admin des avis de confiance."""

    list_display = ("auteur", "cible", "note", "date_creation")
    list_filter = ("note",)
    search_fields = ("auteur__username", "cible__username", "commentaire")

