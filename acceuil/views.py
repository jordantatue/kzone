"""Vues de rendu front de l'application accueil."""

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView

from catalogue.services import CatalogueService


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
