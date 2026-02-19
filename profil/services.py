"""Services metier pour la gestion du profil utilisateur."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Avg

from .models import AvisConfiance, ProfilUtilisateur

User = get_user_model()


class ProfilService:
    """Service central de lecture et mise a jour du profil."""

    @staticmethod
    def get_or_create_profil(utilisateur: User) -> ProfilUtilisateur:
        """Retourne le profil d'un utilisateur, cree si absent."""
        profil, _ = ProfilUtilisateur.objects.get_or_create(utilisateur=utilisateur)
        return profil

    @staticmethod
    def get_dashboard_context(utilisateur: User) -> dict[str, Any]:
        """Construit le contexte du tableau de bord de confiance."""
        profil = ProfilService.get_or_create_profil(utilisateur)
        moyenne = (
            AvisConfiance.objects.filter(cible=utilisateur).aggregate(moyenne=Avg("note"))[
                "moyenne"
            ]
            or 0
        )
        return {
            "profil": profil,
            "note_moyenne": round(float(moyenne), 2),
            "total_avis": AvisConfiance.objects.filter(cible=utilisateur).count(),
        }

