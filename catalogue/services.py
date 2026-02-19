"""Services metier pour la navigation et le filtrage du catalogue."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from django.db.models import Count, QuerySet

from .models import Categorie, Localisation, Produit, ProduitAgricole, ProduitRetail


@dataclass(frozen=True)
class CatalogueFiltres:
    """Valeur immuable representant les filtres saisis par l'utilisateur."""

    categorie: str
    region: str
    ville: str
    etat: str
    region_origine: str


class CatalogueService:
    """Service principal de construction des donnees du catalogue."""

    @staticmethod
    def parse_filtres(params: dict[str, Any]) -> CatalogueFiltres:
        """Convertit la querystring en objet filtre nettoye."""
        return CatalogueFiltres(
            categorie=(params.get("categorie") or "").strip(),
            region=(params.get("region") or "").strip(),
            ville=(params.get("ville") or "").strip(),
            etat=(params.get("etat") or "").strip(),
            region_origine=(params.get("region_origine") or "").strip(),
        )

    @staticmethod
    def get_catalogue_context(params: dict[str, Any]) -> dict[str, Any]:
        """Construit tout le contexte necessaire pour la page catalogue."""
        filtres = CatalogueService.parse_filtres(params)
        produits = CatalogueService._filtrer_produits(filtres)
        categorie_selectionnee = CatalogueService._get_categorie_by_slug(filtres.categorie)

        return {
            "filtres": filtres,
            "produits": produits,
            "total_produits": produits.count(),
            "regions": CatalogueService._get_regions_disponibles(),
            "villes": CatalogueService._get_villes_disponibles(filtres.region),
            "categories_sidebar": CatalogueService._build_sidebar_categories(filtres),
            "show_retail_filters": CatalogueService._show_retail_filters(categorie_selectionnee),
            "show_agricole_filters": CatalogueService._show_agricole_filters(categorie_selectionnee),
            "etat_options": CatalogueService._get_retail_etats(),
            "region_origine_options": CatalogueService._get_regions_origine(),
        }

    @staticmethod
    def _filtrer_produits(filtres: CatalogueFiltres) -> QuerySet[Produit]:
        """Applique les filtres principaux et contextuels sur les produits."""
        queryset = (
            Produit.objects.select_related(
                "categorie",
                "lieu_vente",
                "vendeur",
                "produit_agricole",
                "produit_retail",
            )
            .filter(statut=Produit.StatutChoices.DISPONIBLE)
            .order_by("-date_creation")
        )

        if filtres.categorie:
            categorie = CatalogueService._get_categorie_by_slug(filtres.categorie)
            if categorie:
                ids_categories = CatalogueService._get_descendant_ids(categorie.id)
                queryset = queryset.filter(categorie_id__in=ids_categories)

        if filtres.region:
            queryset = queryset.filter(lieu_vente__region=filtres.region)
        if filtres.ville:
            queryset = queryset.filter(lieu_vente__ville=filtres.ville)

        if filtres.etat:
            queryset = queryset.filter(produit_retail__etat=filtres.etat)
        if filtres.region_origine:
            queryset = queryset.filter(produit_agricole__region_origine=filtres.region_origine)

        return queryset

    @staticmethod
    def _build_sidebar_categories(filtres: CatalogueFiltres) -> list[dict[str, Any]]:
        """Construit la structure parent/enfants avec compte de produits."""
        categories = list(Categorie.objects.select_related("parent").all())
        if not categories:
            return []

        counts_map = CatalogueService._get_counts_by_categorie(filtres)
        children_map: dict[int | None, list[Categorie]] = defaultdict(list)
        by_id = {categorie.id: categorie for categorie in categories}
        for categorie in categories:
            children_map[categorie.parent_id].append(categorie)

        cache_total: dict[int, int] = {}

        def count_recursive(category_id: int) -> int:
            if category_id in cache_total:
                return cache_total[category_id]
            total = counts_map.get(category_id, 0)
            for child in children_map.get(category_id, []):
                total += count_recursive(child.id)
            cache_total[category_id] = total
            return total

        sidebar = []
        for parent in children_map.get(None, []):
            sidebar.append(
                {
                    "categorie": parent,
                    "count": count_recursive(parent.id),
                    "children": [
                        {
                            "categorie": enfant,
                            "count": count_recursive(enfant.id),
                        }
                        for enfant in children_map.get(parent.id, [])
                    ],
                }
            )

        for element in sidebar:
            element["is_active"] = CatalogueService._is_category_active(
                element["categorie"], filtres.categorie, by_id
            )
            for child in element["children"]:
                child["is_active"] = child["categorie"].slug == filtres.categorie

        return sidebar

    @staticmethod
    def _get_counts_by_categorie(filtres: CatalogueFiltres) -> dict[int, int]:
        """Retourne le nombre de produits disponibles par categorie directe."""
        queryset = Produit.objects.filter(statut=Produit.StatutChoices.DISPONIBLE)
        if filtres.region:
            queryset = queryset.filter(lieu_vente__region=filtres.region)
        if filtres.ville:
            queryset = queryset.filter(lieu_vente__ville=filtres.ville)
        return dict(
            queryset.values("categorie_id")
            .annotate(total=Count("id"))
            .values_list("categorie_id", "total")
        )

    @staticmethod
    def _get_descendant_ids(categorie_id: int) -> list[int]:
        """Retourne tous les ids descendants, categorie source incluse."""
        parent_by_id = dict(Categorie.objects.values_list("id", "parent_id"))
        descendants: list[int] = []
        queue = [categorie_id]
        while queue:
            current = queue.pop(0)
            descendants.append(current)
            for enfant_id, parent_id in parent_by_id.items():
                if parent_id == current:
                    queue.append(enfant_id)
        return descendants

    @staticmethod
    def _is_category_active(
        categorie: Categorie, selected_slug: str, by_id: dict[int, Categorie]
    ) -> bool:
        """Indique si la categorie est active ou ancetre de la categorie active."""
        if not selected_slug:
            return False
        current = next((item for item in by_id.values() if item.slug == selected_slug), None)
        while current:
            if current.id == categorie.id:
                return True
            current = by_id.get(current.parent_id)
        return False

    @staticmethod
    def _show_retail_filters(categorie: Categorie | None) -> bool:
        """Determine si les filtres retail doivent etre affiches."""
        if categorie is None:
            return True
        return CatalogueService._get_root_slug(categorie) == "retail"

    @staticmethod
    def _show_agricole_filters(categorie: Categorie | None) -> bool:
        """Determine si les filtres agricoles doivent etre affiches."""
        if categorie is None:
            return True
        return CatalogueService._get_root_slug(categorie) == "agricole"

    @staticmethod
    def _get_root_slug(categorie: Categorie) -> str:
        """Retourne le slug de la racine de la categorie."""
        current = categorie
        while current.parent_id:
            current = current.parent
        return current.slug

    @staticmethod
    def _get_regions_disponibles() -> list[str]:
        """Retourne la liste des regions disponibles pour le selecteur."""
        return list(
            Localisation.objects.order_by("region")
            .values_list("region", flat=True)
            .distinct()
        )

    @staticmethod
    def _get_villes_disponibles(region: str) -> list[str]:
        """Retourne les villes disponibles, optionnellement filtrees par region."""
        queryset = Localisation.objects.order_by("ville")
        if region:
            queryset = queryset.filter(region=region)
        return list(queryset.values_list("ville", flat=True).distinct())

    @staticmethod
    def _get_retail_etats() -> list[str]:
        """Retourne les etats retail presents dans le catalogue."""
        return list(
            ProduitRetail.objects.filter(produit__statut=Produit.StatutChoices.DISPONIBLE)
            .values_list("etat", flat=True)
            .distinct()
        )

    @staticmethod
    def _get_regions_origine() -> list[str]:
        """Retourne les regions d'origine disponibles pour les produits agricoles."""
        return list(
            ProduitAgricole.objects.filter(produit__statut=Produit.StatutChoices.DISPONIBLE)
            .values_list("region_origine", flat=True)
            .distinct()
        )

    @staticmethod
    def _get_categorie_by_slug(slug: str) -> Categorie | None:
        """Charge une categorie a partir de son slug."""
        if not slug:
            return None
        return Categorie.objects.select_related("parent").filter(slug=slug).first()

