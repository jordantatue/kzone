from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.views.generic.base import RedirectView
from django.contrib import messages

from .forms import ConnexionForm
from .services import AuthenticationService

class ConnexionView(View):
    """
    Vue pour gérer la connexion des utilisateurs.
    """
    template_name = 'connexion/connexion.html'
    form_class = ConnexionForm

    def get(self, request, *args, **kwargs):
        """
        Affiche le formulaire de connexion.
        """
        if request.user.is_authenticated:
            return redirect('acceuil:accueil')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Traite la soumission du formulaire de connexion.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            authenticated = AuthenticationService.authenticate_user(request, email, password)
            
            if authenticated:
                return redirect('acceuil:accueil')
            else:
                messages.error(request, "L'adresse e-mail ou le mot de passe est incorrect.")
        
        return render(request, self.template_name, {'form': form})

class DeconnexionView(RedirectView):
    """
    Vue pour gérer la déconnexion des utilisateurs.
    """
    pattern_name = 'connexion:connexion'

    def get(self, request, *args, **kwargs):
        """
        Déconnecte l'utilisateur et le redirige.
        """
        logout(request)
        return super().get(request, *args, **kwargs)

class HomeView(View):
    def get(self,request):
        return render(request, 'home.html')
