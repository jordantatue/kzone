from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ConnexionViewTests(TestCase):
    """Tests des flux de connexion/deconnexion."""

    def setUp(self):
        self.connexion_url = reverse("connexion:connexion")
        self.deconnexion_url = reverse("connexion:deconnexion")
        self.accueil_url = reverse("acceuil:accueil")
        self.user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="StrongPass123!",
        )

    def test_get_connexion_displays_form_for_anonymous_user(self):
        response = self.client.get(self.connexion_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "connexion/connexion.html")
        self.assertContains(response, "Se Conecter")

    def test_get_connexion_redirects_authenticated_user_to_accueil(self):
        self.client.force_login(self.user)
        response = self.client.get(self.connexion_url)
        self.assertRedirects(response, self.accueil_url)

    def test_post_connexion_with_valid_credentials_logs_user_in(self):
        response = self.client.post(
            self.connexion_url,
            {"email": "bob@example.com", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, self.accueil_url)
        self.assertIn("_auth_user_id", self.client.session)

    def test_post_connexion_with_invalid_password_shows_error_message(self):
        response = self.client.post(
            self.connexion_url,
            {"email": "bob@example.com", "password": "WrongPass!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "connexion/connexion.html")
        self.assertContains(
            response,
            "mot de passe est incorrect.",
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_post_connexion_with_invalid_form_keeps_user_anonymous(self):
        response = self.client.post(
            self.connexion_url,
            {"email": "invalid-email", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "connexion/connexion.html")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_deconnexion_logs_user_out_and_redirects_to_connexion(self):
        self.client.force_login(self.user)
        response = self.client.get(self.deconnexion_url)
        self.assertRedirects(response, self.connexion_url)
        self.assertNotIn("_auth_user_id", self.client.session)
