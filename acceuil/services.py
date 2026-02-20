"""Services metier de l'application acceuil."""

from __future__ import annotations

from typing import Any

from django.db.models import Avg, Count, Prefetch
from django.http import Http404

from annonces.models import ImageProduit, Produit
from profil.models import AvisConfiance, ProfilUtilisateur


class AnnonceDetailService:
    """Construit le contexte detaille d'une annonce du catalogue."""

    STATUT_STYLES = {
        Produit.StatutChoices.DISPONIBLE: "text-bg-success",
        Produit.StatutChoices.EN_SEQUESTRE: "text-bg-warning",
        Produit.StatutChoices.VENDU: "text-bg-secondary",
    }

    @staticmethod
    def get_detail_context(*, produit_id: int) -> dict[str, Any]:
        """Retourne le contexte complet de la page detail annonce."""
        produit = (
            Produit.objects.select_related(
                "categorie",
                "lieu_vente",
                "vendeur",
                "produit_agricole",
                "produit_retail",
            )
            .prefetch_related(
                Prefetch("images", queryset=ImageProduit.objects.order_by("ordre", "id"))
            )
            .filter(id=produit_id)
            .first()
        )
        if produit is None:
            raise Http404("Annonce introuvable.")

        profil_vendeur = ProfilUtilisateur.objects.select_related("localisation_defaut").filter(
            utilisateur=produit.vendeur
        ).first()
        reputation = AvisConfiance.objects.filter(cible=produit.vendeur).aggregate(
            note_moyenne=Avg("note"),
            total_avis=Count("id"),
        )
        note_moyenne = float(reputation["note_moyenne"] or 0)
        etoiles_pleines = int(round(note_moyenne))

        return {
            "produit": produit,
            "images": list(produit.images.all()),
            "profil_vendeur": profil_vendeur,
            "is_vendeur_pro": (
                profil_vendeur is not None
                and profil_vendeur.type_vendeur
                == ProfilUtilisateur.TypeVendeurChoices.PROFESSIONNEL
            ),
            "type_vendeur_label": (
                profil_vendeur.get_type_vendeur_display() if profil_vendeur else "Particulier"
            ),
            "ville_vendeur": (
                profil_vendeur.localisation_defaut.ville
                if profil_vendeur and profil_vendeur.localisation_defaut
                else produit.lieu_vente.ville
            ),
            "note_moyenne": round(note_moyenne, 2),
            "total_avis": int(reputation["total_avis"] or 0),
            "etoiles": [index < etoiles_pleines for index in range(5)],
            "statut_badge_class": AnnonceDetailService.STATUT_STYLES.get(
                produit.statut, "text-bg-light"
            ),
        }

