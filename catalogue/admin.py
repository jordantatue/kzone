"""Administration des modeles catalogue."""

from django.contrib import admin

from .models import Categorie, Localisation, Produit, ProduitAgricole, ProduitRetail


@admin.register(Localisation)
class LocalisationAdmin(admin.ModelAdmin):
    """Configuration admin de localisation."""

    list_display = ("region", "ville", "quartier")
    list_filter = ("region", "ville")
    search_fields = ("ville", "quartier")


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """Configuration admin de categorie."""

    list_display = ("nom", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("nom", "slug")
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    """Configuration admin du produit principal."""

    list_display = ("titre", "categorie", "lieu_vente", "prix", "statut", "date_creation")
    list_filter = ("statut", "categorie", "lieu_vente__region")
    search_fields = ("titre", "description")


@admin.register(ProduitRetail)
class ProduitRetailAdmin(admin.ModelAdmin):
    """Configuration admin des produits retail."""

    list_display = ("produit", "marque", "etat")
    list_filter = ("etat", "marque")
    search_fields = ("produit__titre", "marque")


@admin.register(ProduitAgricole)
class ProduitAgricoleAdmin(admin.ModelAdmin):
    """Configuration admin des produits agricoles."""

    list_display = ("produit", "region_origine", "unite_mesure", "date_recolte")
    list_filter = ("region_origine", "unite_mesure")
    search_fields = ("produit__titre",)

