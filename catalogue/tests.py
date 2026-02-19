"""Tests du service catalogue."""

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Categorie, Localisation, Produit, ProduitAgricole, ProduitRetail
from .services import CatalogueService


class CatalogueServiceTests(TestCase):
    """Valide la logique de navigation et filtrage du catalogue."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="StrongPass123!",
        )
        self.douala = Localisation.objects.create(
            region=Localisation.RegionChoices.LITTORAL,
            ville="Douala",
            quartier="Bonanjo",
        )
        self.yaounde = Localisation.objects.create(
            region=Localisation.RegionChoices.CENTRE,
            ville="Yaounde",
            quartier="Bastos",
        )
        self.retail = Categorie.objects.create(nom="Retail", slug="retail")
        self.phones = Categorie.objects.create(
            nom="Telephones",
            slug="telephones",
            parent=self.retail,
        )
        self.agricole = Categorie.objects.create(nom="Agricole", slug="agricole")

        retail_produit = Produit.objects.create(
            vendeur=self.user,
            categorie=self.phones,
            lieu_vente=self.douala,
            titre="Samsung A54",
            prix=180000,
        )
        ProduitRetail.objects.create(
            produit=retail_produit,
            marque="Samsung",
            etat=ProduitRetail.EtatChoices.NEUF,
        )

        agri_produit = Produit.objects.create(
            vendeur=self.user,
            categorie=self.agricole,
            lieu_vente=self.yaounde,
            titre="Sacs de cacao",
            prix=50000,
        )
        ProduitAgricole.objects.create(
            produit=agri_produit,
            region_origine=Localisation.RegionChoices.CENTRE,
            unite_mesure="Sac",
        )

    def test_filter_by_retail_state(self):
        """Le filtre contextuel retail conserve les produits attendus."""
        context = CatalogueService.get_catalogue_context({"etat": ProduitRetail.EtatChoices.NEUF})
        self.assertEqual(context["total_produits"], 1)
        self.assertEqual(context["produits"][0].titre, "Samsung A54")

    def test_filter_by_origin_region(self):
        """Le filtre contextuel agricole conserve les produits attendus."""
        context = CatalogueService.get_catalogue_context(
            {"region_origine": Localisation.RegionChoices.CENTRE}
        )
        self.assertEqual(context["total_produits"], 1)
        self.assertEqual(context["produits"][0].titre, "Sacs de cacao")

    def test_sidebar_counts_include_children(self):
        """Le total parent de la sidebar additionne les sous-categories."""
        context = CatalogueService.get_catalogue_context({})
        retail_entry = next(item for item in context["categories_sidebar"] if item["categorie"].slug == "retail")
        self.assertEqual(retail_entry["count"], 1)

