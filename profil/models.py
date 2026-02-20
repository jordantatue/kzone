"""Modeles metier lies a la gestion du profil utilisateur."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from annonces.models import Localisation

User = get_user_model()


class ProfilUtilisateur(models.Model):
    """Profil et parametres de confiance relies a un utilisateur."""

    class MoyenPaiementChoices(models.TextChoices):
        """Moyens de paiement supportes."""

        ORANGE_MONEY = "orange_money", "Orange Money"
        MTN_MOMO = "mtn_momo", "MTN Mobile Money"
        MOBILE_MONEY = "mobile_money", "Mobile Money"

    class TypeVendeurChoices(models.TextChoices):
        """Types de vendeurs affiches dans les cartes catalogue."""

        PARTICULIER = "particulier", "Particulier"
        PROFESSIONNEL = "professionnel", "Professionnel"

    utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profil_utilisateur",
    )
    photo_profil = models.FileField(upload_to="profil/photos/", blank=True, null=True)
    localisation_defaut = models.ForeignKey(
        Localisation,
        on_delete=models.SET_NULL,
        related_name="profils_utilisateurs",
        null=True,
        blank=True,
    )
    moyen_paiement_prefere = models.CharField(
        max_length=24,
        choices=MoyenPaiementChoices.choices,
        default=MoyenPaiementChoices.MOBILE_MONEY,
    )
    type_vendeur = models.CharField(
        max_length=20,
        choices=TypeVendeurChoices.choices,
        default=TypeVendeurChoices.PARTICULIER,
    )
    numero_paiement = models.CharField(max_length=20, blank=True)
    badge_trustcam = models.BooleanField(default=False)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Retourne une representation concise du profil."""
        return f"Profil de {self.utilisateur.username}"


class AvisConfiance(models.Model):
    """Avis de confiance permettant de calculer la note moyenne d'un utilisateur."""

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="avis_confiance_donnes",
    )
    cible = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="avis_confiance_recus",
    )
    note = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    commentaire = models.CharField(max_length=255, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Regles d'unicite des avis."""

        unique_together = ("auteur", "cible")
        ordering = ("-date_creation",)

    def __str__(self) -> str:
        """Retourne une representation concise de l'avis."""
        return f"Avis {self.note}/5 de {self.auteur} vers {self.cible}"
