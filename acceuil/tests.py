from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalogue.models import (
    Categorie,
    ImageProduit,
    Localisation,
    Produit,
    ProduitAgricole,
    ProduitRetail,
)
from profil.models import AvisConfiance, ProfilUtilisateur


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
        self.produit = produit
        self.detail_url = reverse("acceuil:annonce_detail", kwargs={"produit_id": produit.id})
        self.action_url = reverse("acceuil:annonce_action_ajax", kwargs={"produit_id": produit.id})
        ProduitRetail.objects.create(
            produit=produit,
            marque="Apple",
            etat=ProduitRetail.EtatChoices.OCCASION,
            specifications={"memoire": "128Go", "double_sim": True},
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.user,
            localisation_defaut=self.region_littoral,
            type_vendeur=ProfilUtilisateur.TypeVendeurChoices.PROFESSIONNEL,
            badge_trustcam=True,
        )
        self.buyer = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="StrongPass123!",
        )
        AvisConfiance.objects.create(auteur=self.buyer, cible=self.user, note=4)
        auteur_2 = User.objects.create_user(
            username="charlie",
            email="charlie@example.com",
            password="StrongPass123!",
        )
        AvisConfiance.objects.create(auteur=auteur_2, cible=self.user, note=5)
        image_bytes = (
            b"<svg xmlns='http://www.w3.org/2000/svg' width='100' height='80'>"
            b"<rect width='100' height='80' fill='#009639'/></svg>"
        )
        ImageProduit.objects.create(
            produit=produit,
            image=SimpleUploadedFile("produit.svg", image_bytes, content_type="image/svg+xml"),
            ordre=1,
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

    def test_detail_annonce_displays_core_information(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "acceuil/annonce_detail.html")
        self.assertContains(response, "iPhone 12")
        self.assertContains(response, "250000 FCFA")
        self.assertContains(response, "Douala, Bonamoussadi")
        self.assertContains(response, "Contacter le vendeur")
        self.assertContains(response, "Acheter avec tiers de confiance")

    def test_detail_annonce_displays_retail_specific_fields(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, "Etat")
        self.assertContains(response, "Occasion")
        self.assertContains(response, "Marque")
        self.assertContains(response, "Apple")
        self.assertContains(response, "Specifications")

    def test_detail_annonce_displays_agricole_specific_fields(self):
        categorie_agricole = Categorie.objects.create(nom="Agricole", slug="agricole")
        produit_agri = Produit.objects.create(
            vendeur=self.user,
            categorie=categorie_agricole,
            lieu_vente=self.region_centre,
            titre="Plantain",
            description="Produit agricole local",
            prix=12000,
        )
        ProduitAgricole.objects.create(
            produit=produit_agri,
            region_origine=Localisation.RegionChoices.CENTRE,
            unite_mesure="Regime",
            date_recolte=timezone.now().date() - timedelta(days=2),
            duree_conservation=7,
        )
        detail_url = reverse("acceuil:annonce_detail", kwargs={"produit_id": produit_agri.id})

        response = self.client.get(detail_url)

        self.assertContains(response, "Region d'origine")
        self.assertContains(response, "Regime")
        self.assertContains(response, "Conservation estimee")
        self.assertNotContains(response, "Marque")

    def test_detail_annonce_displays_seller_reputation(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "(2 avis)")
        self.assertContains(response, "Ville de reference")

    def test_detail_annonce_uses_placeholder_without_images(self):
        produit_sans_image = Produit.objects.create(
            vendeur=self.user,
            categorie=self.categorie_telephones,
            lieu_vente=self.region_littoral,
            titre="Produit sans image",
            description="Aucune image",
            prix=5000,
        )
        detail_url = reverse("acceuil:annonce_detail", kwargs={"produit_id": produit_sans_image.id})
        response = self.client.get(detail_url)
        self.assertContains(response, "kzone-placeholder.svg")

    def test_annonce_action_requires_authentication(self):
        response = self.client.post(self.action_url, {"action": "contact"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("login_url", response.json())

    def test_secure_purchase_action_updates_status(self):
        self.client.force_login(self.buyer)
        response = self.client.post(self.action_url, {"action": "secure_purchase"})
        self.assertEqual(response.status_code, 200)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.statut, Produit.StatutChoices.EN_SEQUESTRE)

