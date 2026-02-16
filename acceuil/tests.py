from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccueilViewTests(TestCase):
    """Tests de la page d'accueil publique."""

    def setUp(self):
        self.accueil_url = reverse("acceuil:accueil")
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123!",
        )

    def test_accueil_is_public_for_anonymous_user(self):
        response = self.client.get(self.accueil_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "acceuil/accueil.html")

    def test_accueil_contains_expected_context_metrics(self):
        response = self.client.get(self.accueil_url)
        self.assertEqual(response.context["nombre_clients"], 123)
        self.assertEqual(response.context["nombre_factures"], 42)
        self.assertEqual(response.context["chiffre_affaires"], "12 345,67 €")

    def test_accueil_shows_connexion_button_for_anonymous_user(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, "Mon compte")
        self.assertContains(response, "Connexion")
        self.assertContains(response, reverse("connexion:connexion"))
        self.assertNotContains(response, 'btn btn-outline-danger btn-sm')

    def test_accueil_shows_deconnexion_button_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.accueil_url)
        self.assertContains(response, "Deconnexion")
        self.assertContains(response, reverse("connexion:deconnexion"))
        self.assertNotContains(response, 'btn btn-outline-danger btn-sm')

    def test_accueil_has_mobile_burger_menu_and_offcanvas(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, 'aria-label="Ouvrir le menu"')
        self.assertContains(response, 'id="mobileNavMenu"')

    def test_accueil_has_favoris_messages_and_panier_icons(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, "bi-heart")
        self.assertContains(response, "bi-envelope")
        self.assertContains(response, "bi-cart3")

    def test_accueil_has_desktop_centered_search_input(self):
        response = self.client.get(self.accueil_url)
        self.assertContains(response, 'id="desktop-search"')
