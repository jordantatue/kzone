"""Modeles metier pour la navigation et le catalogue produits."""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class Localisation(models.Model):
    """Represente une localisation geographique exploitable par les filtres."""

    class RegionChoices(models.TextChoices):
        """Regions usuelles du Cameroun."""

        ADAMAOUA = "Adamaoua", "Adamaoua"
        CENTRE = "Centre", "Centre"
        EST = "Est", "Est"
        EXTREME_NORD = "Extreme-Nord", "Extreme-Nord"
        LITTORAL = "Littoral", "Littoral"
        NORD = "Nord", "Nord"
        NORD_OUEST = "Nord-Ouest", "Nord-Ouest"
        OUEST = "Ouest", "Ouest"
        SUD = "Sud", "Sud"
        SUD_OUEST = "Sud-Ouest", "Sud-Ouest"

    region = models.CharField(max_length=32, choices=RegionChoices.choices)
    ville = models.CharField(max_length=120)
    quartier = models.CharField(max_length=120)

    class Meta:
        """Contraintes metier de localisation."""

        ordering = ("region", "ville", "quartier")
        unique_together = ("region", "ville", "quartier")

    def __str__(self) -> str:
        """Retourne une representation lisible de la localisation."""
        return f"{self.region} / {self.ville} / {self.quartier}"


class Categorie(models.Model):
    """Categorie recursive pour construire la sidebar parent/sous-categories."""

    nom = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="enfants",
    )

    class Meta:
        """Contraintes metier de categorie."""

        ordering = ("nom",)

    def save(self, *args, **kwargs) -> None:
        """Genere le slug depuis le nom quand il n'est pas fourni."""
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Retourne le nom de la categorie."""
        return self.nom


class Produit(models.Model):
    """Modele racine des produits affiches dans le catalogue."""

    class StatutChoices(models.TextChoices):
        """Statuts de disponibilite des produits."""

        DISPONIBLE = "disponible", "Disponible"
        EN_SEQUESTRE = "en_sequestre", "En sequestre"
        VENDU = "vendu", "Vendu"

    vendeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="produits")
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="produits")
    lieu_vente = models.ForeignKey(Localisation, on_delete=models.PROTECT, related_name="produits")
    titre = models.CharField(max_length=180, db_index=True)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.DISPONIBLE,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Contraintes metier sur les produits."""

        ordering = ("-date_creation",)

    def __str__(self) -> str:
        """Retourne le titre du produit."""
        return self.titre


class ProduitAgricole(models.Model):
    """Extension des attributs specifiques aux produits agricoles."""

    produit = models.OneToOneField(
        Produit,
        on_delete=models.CASCADE,
        related_name="produit_agricole",
    )
    region_origine = models.CharField(max_length=32, choices=Localisation.RegionChoices.choices)
    unite_mesure = models.CharField(max_length=24)
    date_recolte = models.DateField(null=True, blank=True)
    duree_conservation = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        """Retourne une representation lisible de la variante agricole."""
        return f"Agricole: {self.produit.titre}"


class ProduitRetail(models.Model):
    """Extension des attributs specifiques aux produits retail."""

    class EtatChoices(models.TextChoices):
        """Etats rapides pour filtrage retail."""

        NEUF = "neuf", "Neuf"
        OCCASION = "occasion", "Occasion"
        RECONDITIONNE = "reconditionne", "Reconditionne"

    produit = models.OneToOneField(
        Produit,
        on_delete=models.CASCADE,
        related_name="produit_retail",
    )
    marque = models.CharField(max_length=120)
    etat = models.CharField(max_length=24, choices=EtatChoices.choices, default=EtatChoices.NEUF)
    specifications = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        """Retourne une representation lisible de la variante retail."""
        return f"Retail: {self.produit.titre}"

