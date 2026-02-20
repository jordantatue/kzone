from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from annonces.models import (
    Categorie,
    Localisation,
    Produit,
    ProduitAgricole,
    ProduitRetail,
)
from profil.models import AvisConfiance, ProfilUtilisateur


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


class TestsFonctionnelsAccueil(TestFonctionnelCase):
    """Tests fonctionnels des parcours accueil et annonces."""

    def setUp(self):
        """Preparation des donnees de navigation annonces."""
        super().setUp()
        self.url_accueil = reverse("acceuil:accueil")
        self.url_filtre_ajax = reverse("acceuil:catalogue_filtrer")
        self.vendeur = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123!",
        )
        self.acheteur = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="StrongPass123!",
        )
        self.localisation_littoral = Localisation.objects.create(
            region=Localisation.RegionChoices.LITTORAL,
            ville="Douala",
            quartier="Bonamoussadi",
        )
        self.localisation_centre = Localisation.objects.create(
            region=Localisation.RegionChoices.CENTRE,
            ville="Yaounde",
            quartier="Bastos",
        )
        self.categorie_racine_retail = Categorie.objects.create(nom="Retail", slug="retail")
        self.categorie_telephones = Categorie.objects.create(
            nom="Telephones", slug="telephones", parent=self.categorie_racine_retail
        )
        self.produit = Produit.objects.create(
            vendeur=self.vendeur,
            categorie=self.categorie_telephones,
            lieu_vente=self.localisation_littoral,
            titre="iPhone 12",
            description="Telephone en bon etat",
            prix=250000,
        )
        self.url_detail = reverse("acceuil:annonce_detail", kwargs={"produit_id": self.produit.id})
        self.url_action = reverse("acceuil:annonce_action_ajax", kwargs={"produit_id": self.produit.id})
        ProduitRetail.objects.create(
            produit=self.produit,
            marque="Apple",
            etat=ProduitRetail.EtatChoices.OCCASION,
            specifications={"memoire": "128Go", "double_sim": True},
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.vendeur,
            localisation_defaut=self.localisation_littoral,
            type_vendeur=ProfilUtilisateur.TypeVendeurChoices.PROFESSIONNEL,
            numero_paiement="699001122",
            badge_trustcam=True,
        )
        AvisConfiance.objects.create(auteur=self.acheteur, cible=self.vendeur, note=4)
        auteur_2 = User.objects.create_user(
            username="charlie",
            email="charlie@example.com",
            password="StrongPass123!",
        )
        AvisConfiance.objects.create(auteur=auteur_2, cible=self.vendeur, note=5)

    def test_acces_public_page_accueil(self):
        """Acces public de la page accueil."""
        response = self.client.get(self.url_accueil)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_produits"], 1)

    def test_filtrage_ajax_annonces(self):
        """Filtrage AJAX des annonces."""
        response = self.client.get(
            self.url_filtre_ajax,
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

    def test_filtrage_region_exclut_hors_zone(self):
        """Filtrage par region exclut les annonces hors zone."""
        response = self.client.get(self.url_accueil, {"region": Localisation.RegionChoices.CENTRE})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_produits"], 0)

    def test_detail_annonce_charge_contexte(self):
        """Chargement du detail annonce avec contexte metier."""
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["produit"].id, self.produit.id)
        self.assertEqual(response.context["total_avis"], 2)
        self.assertEqual(response.context["note_moyenne"], 4.5)
        self.assertEqual(response.context["membre_depuis"], self.vendeur.date_joined.year)

    def test_detail_annonce_charge_donnees_agricoles(self):
        """Chargement detail annonce agricole."""
        categorie_agricole = Categorie.objects.create(nom="Agricole", slug="agricole-secondaire")
        produit_agri = Produit.objects.create(
            vendeur=self.vendeur,
            categorie=categorie_agricole,
            lieu_vente=self.localisation_centre,
            titre="Plantain",
            description="Produit agricole local",
            prix=12000,
        )
        ProduitAgricole.objects.create(
            produit=produit_agri,
            region_origine=Localisation.RegionChoices.CENTRE,
            unite_mesure="Regime",
        )
        detail_url = reverse("acceuil:annonce_detail", kwargs={"produit_id": produit_agri.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["produit"].produit_agricole.unite_mesure, "Regime")
        self.assertEqual(response.context["produit"].produit_agricole.region_origine, "Centre")

    def test_action_contact_refuse_sans_authentification(self):
        """Action contact refusee sans authentification."""
        response = self.client.post(self.url_action, {"action": "contact"})
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["ok"])
        self.assertIn("login_url", response.json())

    def test_action_voir_numero_retourne_numero_vendeur(self):
        """Action voir numero retourne le numero vendeur."""
        response = self.client.post(self.url_action, {"action": "show_phone"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["phone_number"], "699001122")

    def test_action_contact_retourne_dashboard_connecte(self):
        """Action contact redirige vers dashboard si connecte."""
        self.client.force_login(self.acheteur)
        response = self.client.post(self.url_action, {"action": "contact"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["redirect_url"], reverse("profil:dashboard"))

