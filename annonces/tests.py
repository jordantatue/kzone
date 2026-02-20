"""Tests fonctionnels du service de navigation des annonces."""

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Categorie, Localisation, Produit, ProduitAgricole, ProduitRetail
from .services import CatalogueService


class TestFonctionnelCase(TestCase):
    """Base de tests avec traces courtes et lisibles."""

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


class TestsServiceAnnonces(TestFonctionnelCase):
    """Valide les cas fonctionnels principaux du service d'annonces."""

    def setUp(self):
        """Preparation du jeu de donnees annonces."""
        super().setUp()
        self.utilisateur = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="StrongPass123!",
        )
        self.localisation_douala = Localisation.objects.create(
            region=Localisation.RegionChoices.LITTORAL,
            ville="Douala",
            quartier="Bonanjo",
        )
        self.localisation_yaounde = Localisation.objects.create(
            region=Localisation.RegionChoices.CENTRE,
            ville="Yaounde",
            quartier="Bastos",
        )
        self.categorie_retail = Categorie.objects.create(nom="Retail", slug="retail")
        self.categorie_telephones = Categorie.objects.create(
            nom="Telephones",
            slug="telephones",
            parent=self.categorie_retail,
        )
        self.categorie_agricole = Categorie.objects.create(nom="Agricole", slug="agricole")

        produit_retail = Produit.objects.create(
            vendeur=self.utilisateur,
            categorie=self.categorie_telephones,
            lieu_vente=self.localisation_douala,
            titre="Samsung A54",
            prix=180000,
        )
        ProduitRetail.objects.create(
            produit=produit_retail,
            marque="Samsung",
            etat=ProduitRetail.EtatChoices.NEUF,
        )

        produit_agricole = Produit.objects.create(
            vendeur=self.utilisateur,
            categorie=self.categorie_agricole,
            lieu_vente=self.localisation_yaounde,
            titre="Sacs de cacao",
            prix=50000,
        )
        ProduitAgricole.objects.create(
            produit=produit_agricole,
            region_origine=Localisation.RegionChoices.CENTRE,
            unite_mesure="Sac",
        )

    def test_filtrage_retail_par_etat(self):
        """Filtrage retail par etat."""
        contexte = CatalogueService.get_catalogue_context({"etat": ProduitRetail.EtatChoices.NEUF})
        self.assertEqual(contexte["total_produits"], 1)
        self.assertEqual(contexte["produits"][0].titre, "Samsung A54")

    def test_filtrage_agricole_par_region_origine(self):
        """Filtrage agricole par region d'origine."""
        contexte = CatalogueService.get_catalogue_context(
            {"region_origine": Localisation.RegionChoices.CENTRE}
        )
        self.assertEqual(contexte["total_produits"], 1)
        self.assertEqual(contexte["produits"][0].titre, "Sacs de cacao")

    def test_comptage_sidebar_parent_enfants(self):
        """Comptage sidebar categorie parent et enfants."""
        contexte = CatalogueService.get_catalogue_context({})
        entree_retail = next(
            item for item in contexte["categories_sidebar"] if item["categorie"].slug == "retail"
        )
        self.assertEqual(entree_retail["count"], 1)

