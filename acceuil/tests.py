from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalogue.models import Categorie, Localisation, Produit, ProduitRetail


class AccueilViewTests(TestCase):
    """Tests de la page d'accueil et du module de filtrage catalogue."""

    def setUp(self):
        self.accueil_url = reverse("acceuil:accueil")
        self.ajax_url = reverse("acceuil:catalogue_filtrer")
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123!",
        )
        self.region_littoral = Localisation.objects.create(
            region=Localisation.RegionChoices.LITTORAL,
            ville="Douala",
            quartier="Bonamoussadi",
        )
        self.region_centre = Localisation.objects.create(
            region=Localisation.RegionChoices.CENTRE,
            ville="Yaounde",
            quartier="Bastos",
        )
        self.categorie_retail = Categorie.objects.create(nom="Retail", slug="retail")
        self.categorie_telephones = Categorie.objects.create(
            nom="Telephones", slug="telephones", parent=self.categorie_retail
        )
        produit = Produit.objects.create(
            vendeur=self.user,
            categorie=self.categorie_telephones,
            lieu_vente=self.region_littoral,
            titre="iPhone 12",
            description="Telephone en bon etat",
            prix=250000,
        )
        ProduitRetail.objects.create(
            produit=produit,
            marque="Apple",
            etat=ProduitRetail.EtatChoices.OCCASION,
        )

    def test_accueil_is_public_for_anonymous_user(self):
        response = self.client.get(self.accueil_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "acceuil/accueil.html")

    def test_accueil_contains_expected_context_metrics(self):
        response = self.client.get(self.accueil_url)
        self.assertEqual(response.context["nombre_clients"], 123)
        self.assertEqual(response.context["nombre_factures"], 42)
        self.assertEqual(response.context["chiffre_affaires"], "12 345,67 EUR")

    def test_accueil_shows_connexion_button_for_anonymous_user(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, "Mon compte")
        self.assertContains(response, "Connexion")
        self.assertContains(response, reverse("connexion:connexion"))

    def test_accueil_shows_deconnexion_button_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.accueil_url)
        self.assertContains(response, "Deconnexion")
        self.assertContains(response, reverse("connexion:deconnexion"))

    def test_accueil_has_mobile_burger_menu_and_offcanvas(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, 'aria-label="Ouvrir le menu"')
        self.assertContains(response, 'id="mobileNavMenu"')

    def test_accueil_has_desktop_centered_search_input(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, 'id="desktop-search"')

    def test_ajax_filter_returns_json_fragments(self):
        response = self.client.get(
            self.ajax_url,
            {
                "categorie": "telephones",
                "region": Localisation.RegionChoices.LITTORAL,
                "etat": ProduitRetail.EtatChoices.OCCASION,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("products_html", response.json())
        self.assertIn("sidebar_html", response.json())
        self.assertIn("total_produits", response.json())
        self.assertEqual(response.json()["total_produits"], 1)

    def test_filter_by_region_hides_other_regions(self):
        response = self.client.get(self.accueil_url, {"region": Localisation.RegionChoices.CENTRE})
        self.assertContains(response, "Aucun produit ne correspond aux filtres selectionnes")

