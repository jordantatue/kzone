"""Tests de l'application profil."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalogue.models import Localisation

from .models import AvisConfiance, ProfilUtilisateur


class ProfilDashboardViewTests(TestCase):
    """Tests du tableau de bord profil utilisateur."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="luc",
            email="luc@example.com",
            password="StrongPass123!",
            first_name="Luc",
            last_name="Tamba",
        )
        self.other_user = User.objects.create_user(
            username="maya",
            email="maya@example.com",
            password="StrongPass123!",
        )
        self.url = reverse("profil:dashboard")

    def test_dashboard_requires_authentication(self):
        """La page profil redirige un visiteur non connecte."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("connexion:connexion"), response.url)

    def test_dashboard_get_creates_profile(self):
        """Le profil est cree automatiquement au premier affichage."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ProfilUtilisateur.objects.filter(utilisateur=self.user).exists())
        self.assertContains(response, "Tableau de confiance")

    def test_post_identity_updates_name_and_location(self):
        """Le formulaire identite met a jour user + localisation."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "form_type": "identite",
                "full_name": "Luc Junior Tamba",
                "region": Localisation.RegionChoices.LITTORAL,
                "ville": "Douala",
                "quartier": "Akwa",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        profil = ProfilUtilisateur.objects.get(utilisateur=self.user)
        self.assertEqual(self.user.first_name, "Luc")
        self.assertEqual(self.user.last_name, "Junior Tamba")
        self.assertIsNotNone(profil.localisation_defaut)
        self.assertEqual(profil.localisation_defaut.ville, "Douala")

    def test_post_finance_updates_payment_preferences(self):
        """Le formulaire finance met a jour le moyen et numero de paiement."""
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "form_type": "finance",
                "moyen_paiement_prefere": ProfilUtilisateur.MoyenPaiementChoices.MTN_MOMO,
                "numero_paiement": "699000111",
            },
        )
        self.assertEqual(response.status_code, 200)
        profil = ProfilUtilisateur.objects.get(utilisateur=self.user)
        self.assertEqual(
            profil.moyen_paiement_prefere, ProfilUtilisateur.MoyenPaiementChoices.MTN_MOMO
        )
        self.assertEqual(profil.numero_paiement, "699000111")

    def test_dashboard_displays_average_rating(self):
        """La note moyenne affichee provient des avis recus."""
        self.client.force_login(self.user)
        AvisConfiance.objects.create(auteur=self.other_user, cible=self.user, note=4)
        response = self.client.get(self.url)
        self.assertContains(response, "4.0/5")

