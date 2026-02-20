"""Vues de rendu front de l'application accueil."""

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from annonces.models import Produit
from annonces.services import CatalogueService
from .services import AnnonceDetailService


class AccueilView(TemplateView):
    """Affiche l'accueil avec catalogue, sidebar et filtres dynamiques."""

    template_name = "acceuil/accueil.html"

    def get_context_data(self, **kwargs):
        """Ajoute les donnees globales et le contexte catalogue."""
        context = super().get_context_data(**kwargs)
        context.update(CatalogueService.get_catalogue_context(self.request.GET))
        context["nombre_clients"] = 123
        context["chiffre_affaires"] = "12 345,67 EUR"
        context["nombre_factures"] = 42
        return context


class CatalogueFiltreAjaxView(View):
    """Endpoint AJAX qui met a jour le catalogue sans rechargement complet."""

    def get(self, request, *args, **kwargs):
        """Retourne les fragments HTML recalcules selon les filtres courants."""
        context = CatalogueService.get_catalogue_context(request.GET)

        sidebar_html = render_to_string(
            "acceuil/partials/catalog_sidebar.html",
            context=context,
            request=request,
        )
        products_html = render_to_string(
            "acceuil/partials/catalog_products.html",
            context=context,
            request=request,
        )
        context_filters_html = render_to_string(
            "acceuil/partials/catalog_context_filters.html",
            context=context,
            request=request,
        )
        city_options_html = render_to_string(
            "acceuil/partials/catalog_city_options.html",
            context=context,
            request=request,
        )

        return JsonResponse(
            {
                "sidebar_html": sidebar_html,
                "products_html": products_html,
                "context_filters_html": context_filters_html,
                "city_options_html": city_options_html,
                "total_produits": context["total_produits"],
            }
        )


class DetailAnnonceView(TemplateView):
    """Affiche la page detaillee d'une annonce du catalogue."""

    template_name = "acceuil/annonce_detail.html"

    def get_context_data(self, **kwargs):
        """Construit le contexte detail annonce avec confiance vendeur."""
        context = super().get_context_data(**kwargs)
        context.update(AnnonceDetailService.get_detail_context(produit_id=kwargs["produit_id"]))
        return context


class AnnonceActionAjaxView(View):
    """Traite les actions rapides de la page detail (contact, achat securise)."""

    def post(self, request, *args, **kwargs):
        """Execute l'action demandee et retourne un payload JSON minimal."""
        produit = Produit.objects.select_related("vendeur").filter(id=kwargs["produit_id"]).first()
        if produit is None:
            return JsonResponse({"ok": False, "message": "Annonce introuvable."}, status=404)

        action = (request.POST.get("action") or "").strip()
        if not request.user.is_authenticated:
            login_url = reverse("connexion:connexion")
            detail_url = reverse("acceuil:annonce_detail", kwargs={"produit_id": produit.id})
            return JsonResponse(
                {
                    "ok": False,
                    "message": "Veuillez vous connecter pour continuer.",
                    "login_url": f"{login_url}?next={detail_url}",
                },
                status=401,
            )

        if action == "contact":
            dashboard_url = reverse("profil:dashboard")
            return JsonResponse(
                {
                    "ok": True,
                    "message": "Conversation initiee. Continuez depuis votre espace profil.",
                    "redirect_url": dashboard_url,
                }
            )

        if action == "secure_purchase":
            if request.user == produit.vendeur:
                return JsonResponse(
                    {
                        "ok": False,
                        "message": "Vous ne pouvez pas acheter votre propre annonce.",
                    },
                    status=400,
                )
            if produit.statut != Produit.StatutChoices.DISPONIBLE:
                return JsonResponse(
                    {"ok": False, "message": "Cette annonce n'est plus disponible."},
                    status=400,
                )
            produit.statut = Produit.StatutChoices.EN_SEQUESTRE
            produit.save(update_fields=["statut", "date_mise_a_jour"])
            return JsonResponse(
                {
                    "ok": True,
                    "message": "Procedure de paiement securise initialisee (fonds bloques).",
                    "new_status": produit.get_statut_display(),
                    "new_status_value": produit.statut,
                }
            )

        return JsonResponse({"ok": False, "message": "Action non supportee."}, status=400)


class ContactVendeurRedirectView(View):
    """Fallback non-JS pour rediriger vers l'espace de contact interne."""

    def post(self, request, *args, **kwargs):
        """Redirige l'utilisateur vers connexion ou dashboard avec feedback."""
        if not request.user.is_authenticated:
            detail_url = reverse("acceuil:annonce_detail", kwargs={"produit_id": kwargs["produit_id"]})
            return redirect(f"{reverse('connexion:connexion')}?next={detail_url}")

        messages.success(
            request,
            "Conversation initiee. Retrouvez les echanges dans votre espace profil.",
        )
        return redirect("profil:dashboard")
