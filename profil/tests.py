"""Tests fonctionnels de l'application profil."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from annonces.models import Localisation

from .models import AvisConfiance, ProfilUtilisateur


class TestFonctionnelCase(TestCase):
    """Base de tests avec sortie concise par fonctionnalite."""

    def setUp(self):
        """Affiche la fonctionnalite en cours de test."""
        super().setUp()
        print(f"[TEST START] {self._description_test()}")

    def tearDown(self):
        """Affiche le resultat du test execute."""
        statut = "OK" if self._is_test_successful() else "FAIL"
        print(f"[TEST END] {self._description_test()} => {statut}")
        super().tearDown()

    def _description_test(self) -> str:
        """Retourne une description courte de la fonctionnalite testee."""
        methode = getattr(self, self._testMethodName)
        docstring = (methode.__doc__ or "").strip()
        if docstring:
            return docstring.splitlines()[0]
        return self._testMethodName.replace("_", " ").strip()

    def _is_test_successful(self) -> bool:
        """Retourne True si le test courant est en succes."""
        outcome = getattr(self, "_outcome", None)
        if outcome is None:
            return True
        success = getattr(outcome, "success", None)
        if success is not None:
            return bool(success)
        result = getattr(outcome, "result", None)
        if result is None:
            return True
        for test, _ in list(getattr(result, "errors", [])) + list(getattr(result, "failures", [])):
            if test is self:
                return False
        return True


class TestsFonctionnelsDashboardProfil(TestFonctionnelCase):
    """Valide les comportements fonctionnels du dashboard profil."""

    def setUp(self):
        """Preparation des utilisateurs de test."""
        super().setUp()
        self.utilisateur = User.objects.create_user(
            username="luc",
            email="luc@example.com",
            password="StrongPass123!",
            first_name="Luc",
            last_name="Tamba",
        )
        self.autre_utilisateur = User.objects.create_user(
            username="maya",
            email="maya@example.com",
            password="StrongPass123!",
        )
        self.url_dashboard = reverse("profil:dashboard")

    def test_acces_dashboard_demande_authentification(self):
        """Acces dashboard protege par authentification."""
        response = self.client.get(self.url_dashboard)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("connexion:connexion"), response.url)

    def test_get_dashboard_cree_profil_absent(self):
        """Creation automatique du profil au premier acces."""
        self.client.force_login(self.utilisateur)
        response = self.client.get(self.url_dashboard)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ProfilUtilisateur.objects.filter(utilisateur=self.utilisateur).exists())

    def test_post_identite_met_a_jour_nom_et_localisation(self):
        """Mise a jour identite et localisation du profil."""
        self.client.force_login(self.utilisateur)
        response = self.client.post(
            self.url_dashboard,
            {
                "form_type": "identite",
                "full_name": "Luc Junior Tamba",
                "region": Localisation.RegionChoices.LITTORAL,
                "ville": "Douala",
                "quartier": "Akwa",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.utilisateur.refresh_from_db()
        profil = ProfilUtilisateur.objects.get(utilisateur=self.utilisateur)
        self.assertEqual(self.utilisateur.first_name, "Luc")
        self.assertEqual(self.utilisateur.last_name, "Junior Tamba")
        self.assertIsNotNone(profil.localisation_defaut)
        self.assertEqual(profil.localisation_defaut.ville, "Douala")

    def test_post_finance_met_a_jour_preferences(self):
        """Mise a jour du moyen et numero de paiement."""
        self.client.force_login(self.utilisateur)
        response = self.client.post(
            self.url_dashboard,
            {
                "form_type": "finance",
                "moyen_paiement_prefere": ProfilUtilisateur.MoyenPaiementChoices.MTN_MOMO,
                "numero_paiement": "699000111",
            },
        )
        self.assertEqual(response.status_code, 200)
        profil = ProfilUtilisateur.objects.get(utilisateur=self.utilisateur)
        self.assertEqual(
            profil.moyen_paiement_prefere, ProfilUtilisateur.MoyenPaiementChoices.MTN_MOMO
        )
        self.assertEqual(profil.numero_paiement, "699000111")

    def test_get_dashboard_expose_note_moyenne(self):
        """Calcul de note moyenne des avis recus."""
        self.client.force_login(self.utilisateur)
        AvisConfiance.objects.create(auteur=self.autre_utilisateur, cible=self.utilisateur, note=4)
        response = self.client.get(self.url_dashboard)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["note_moyenne"], 4.0)
        self.assertEqual(response.context["total_avis"], 1)

