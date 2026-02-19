"""Vues CBV pour la gestion du profil utilisateur."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from .forms import ProfilFinanceForm, ProfilIdentiteForm
from .services import ProfilService


class ProfilDashboardView(LoginRequiredMixin, View):
    """Affiche et met a jour les informations profil et finance."""

    template_name = "profil/dashboard.html"

    def get(self, request, *args, **kwargs):
        """Affiche le tableau de bord profil avec les formulaires."""
        profil = ProfilService.get_or_create_profil(request.user)
        context = ProfilService.get_dashboard_context(request.user)
        context["identite_form"] = ProfilIdentiteForm(instance=profil, user=request.user)
        context["finance_form"] = ProfilFinanceForm(instance=profil)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Traite la mise a jour identite ou finance selon le formulaire soumis."""
        profil = ProfilService.get_or_create_profil(request.user)
        form_type = request.POST.get("form_type")
        identite_form = ProfilIdentiteForm(instance=profil, user=request.user)
        finance_form = ProfilFinanceForm(instance=profil)

        if form_type == "identite":
            identite_form = ProfilIdentiteForm(
                request.POST, request.FILES, instance=profil, user=request.user
            )
            if identite_form.is_valid():
                identite_form.save()
                messages.success(request, "Informations personnelles mises a jour.")
            else:
                messages.error(request, "Veuillez corriger les erreurs du profil.")
        elif form_type == "finance":
            finance_form = ProfilFinanceForm(request.POST, instance=profil)
            if finance_form.is_valid():
                finance_form.save()
                messages.success(request, "Parametres financiers mis a jour.")
            else:
                messages.error(request, "Veuillez corriger les erreurs financieres.")
        else:
            messages.error(request, "Type de formulaire invalide.")

        context = ProfilService.get_dashboard_context(request.user)
        context["identite_form"] = identite_form
        context["finance_form"] = finance_form
        return render(request, self.template_name, context)

