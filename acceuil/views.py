from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class AccueilView(LoginRequiredMixin, TemplateView):
    """
    Affiche la page d'accueil protégée après connexion.
    """
    template_name = 'acceuil/accueil.html'

    def get_context_data(self, **kwargs):
        """
        Ajoute des données de contexte au template.
        """
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # Statistiques factices
        context['nombre_clients'] = 123
        context['chiffre_affaires'] = "12 345,67 €"
        context['nombre_factures'] = 42
        return context
