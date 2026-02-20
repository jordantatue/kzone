# Pattern : Class-Based Views (CBV)

## Principe
**Interdiction des function-based views. Utilise uniquement des CBV Django.**

Les vues :
- N'ont PAS de logique métier (ça va dans services.py)
- Appellent des services
- Passent les données aux templates
- Retournent des HttpResponse

## CBV Natives Django

### ListView - Afficher une liste

```python
# apps/clients/views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Client

class ClientListView(LoginRequiredMixin, ListView):
    """Vue listant tous les clients avec pagination."""
    model = Client
    template_name = 'clients/liste.html'
    context_object_name = 'clients'
    paginate_by = 25
    
    def get_queryset(self):
        """Optimise les requêtes avec select_related."""
        return Client.objects.select_related('utilisateur').filter(
            actif=True
        ).order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        """Ajoute des données supplémentaires au contexte."""
        context = super().get_context_data(**kwargs)
        
        # Appel service pour statistiques
        from .services import ClientService
        context['nb_total'] = ClientService.compter_clients_actifs()
        
        return context
```

### DetailView - Afficher un détail

```python
# apps/clients/views.py
from django.views.generic import DetailView
from .models import Client

class ClientDetailView(LoginRequiredMixin, DetailView):
    """Vue affichant les détails d'un client."""
    model = Client
    template_name = 'clients/detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        """Ajoute statistiques du client."""
        context = super().get_context_data(**kwargs)
        
        # Appel service
        from .services import FacturationService
        context['ca_total'] = FacturationService.calculer_ca_client(
            self.object
        )
        
        return context
```

### CreateView - Créer un objet

```python
# apps/clients/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Client
from .forms import ClientForm
from .services import ClientService

class ClientCreateView(LoginRequiredMixin, CreateView):
    """Vue de création d'un client."""
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:liste')
    
    def form_valid(self, form):
        """Appelle le service pour créer le client."""
        try:
            # Service gère toute la logique métier
            client = ClientService.creer_client(
                nom=form.cleaned_data['nom'],
                email=form.cleaned_data['email'],
                telephone=form.cleaned_data['telephone'],
                utilisateur=self.request.user
            )
            
            messages.success(
                self.request,
                f"Client {client.nom} créé avec succès"
            )
            return redirect(self.success_url)
            
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
```

### UpdateView - Modifier un objet

```python
# apps/clients/views.py
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Client
from .forms import ClientForm

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Vue de modification d'un client."""
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    
    def get_success_url(self):
        """Redirection vers le détail du client modifié."""
        return reverse_lazy('clients:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Appelle le service pour mise à jour."""
        from .services import ClientService
        
        try:
            client = ClientService.mettre_a_jour_client(
                client_id=self.object.pk,
                donnees=form.cleaned_data
            )
            
            messages.success(self.request, "Client mis à jour")
            return redirect(self.get_success_url())
            
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
```

### DeleteView - Supprimer un objet

```python
# apps/clients/views.py
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from .models import Client

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Vue de suppression d'un client."""
    model = Client
    template_name = 'clients/confirm_delete.html'
    success_url = reverse_lazy('clients:liste')
    
    def delete(self, request, *args, **kwargs):
        """Suppression logique (soft delete)."""
        from .services import ClientService
        
        client = self.get_object()
        ClientService.archiver_client(client.pk)
        
        messages.success(request, f"Client {client.nom} archivé")
        return redirect(self.success_url)
```

### TemplateView - Page statique

```python
# apps/accueil/views.py
from django.views.generic import TemplateView

class AccueilView(TemplateView):
    """Page d'accueil."""
    template_name = 'accueil/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Données dynamiques via services
        from apps.clients.services import StatistiquesService
        context['stats'] = StatistiquesService.obtenir_stats_globales()
        
        return context
```

## Mixins Utiles

### LoginRequiredMixin - Authentification requise

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MaVue(LoginRequiredMixin, ListView):
    login_url = '/connexion/'  # URL de redirection si non connecté
    redirect_field_name = 'redirect_to'
```

### PermissionRequiredMixin - Permission requise

```python
from django.contrib.auth.mixins import PermissionRequiredMixin

class ClientDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'clients.delete_client'
    
    def handle_no_permission(self):
        """Action si pas de permission."""
        messages.error(self.request, "Vous n'avez pas les droits")
        return redirect('accueil')
```

### UserPassesTestMixin - Test personnalisé

```python
from django.contrib.auth.mixins import UserPassesTestMixin

class ClientUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        """Seul le propriétaire peut modifier."""
        client = self.get_object()
        return client.utilisateur == self.request.user
```

## Exemple Complet : CRUD Factures

```python
# apps/factures/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Facture
from .forms import FactureForm
from .services import FacturationService

class FactureListView(LoginRequiredMixin, ListView):
    """Liste des factures avec filtres."""
    model = Facture
    template_name = 'factures/liste.html'
    context_object_name = 'factures'
    paginate_by = 25
    
    def get_queryset(self):
        qs = Facture.objects.select_related('client').order_by('-date_emission')
        
        # Filtre statut si fourni
        statut = self.request.GET.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques via service
        context['ca_mois'] = FacturationService.calculer_ca_mois_courant()
        context['statuts'] = Facture.STATUTS_CHOICES
        
        return context


class FactureDetailView(LoginRequiredMixin, DetailView):
    """Détail d'une facture."""
    model = Facture
    template_name = 'factures/detail.html'
    context_object_name = 'facture'
    
    def get_queryset(self):
        return Facture.objects.select_related('client').prefetch_related('lignes')


class FactureCreateView(LoginRequiredMixin, CreateView):
    """Création d'une facture."""
    model = Facture
    form_class = FactureForm
    template_name = 'factures/form.html'
    
    def form_valid(self, form):
        try:
            # Service crée la facture complète
            facture = FacturationService.creer_facture(
                client=form.cleaned_data['client'],
                lignes=form.cleaned_data['lignes'],
                taux_tva=form.cleaned_data.get('taux_tva')
            )
            
            messages.success(
                self.request,
                f"Facture {facture.numero} créée"
            )
            return redirect('factures:detail', pk=facture.pk)
            
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('factures:detail', kwargs={'pk': self.object.pk})


class FactureExportPDFView(LoginRequiredMixin, DetailView):
    """Export PDF d'une facture."""
    model = Facture
    
    def get(self, request, *args, **kwargs):
        facture = self.get_object()
        
        # Service génère le PDF
        from apps.documents.services import PDFService
        return PDFService.generer_pdf_facture(facture)
```

## URLs Correspondantes

```python
# apps/factures/urls.py
from django.urls import path
from . import views

app_name = 'factures'

urlpatterns = [
    path('', views.FactureListView.as_view(), name='liste'),
    path('<int:pk>/', views.FactureDetailView.as_view(), name='detail'),
    path('creer/', views.FactureCreateView.as_view(), name='creer'),
    path('<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='modifier'),
    path('<int:pk>/pdf/', views.FactureExportPDFView.as_view(), name='pdf'),
]
```

## Messages de Retour

Toujours donner un feedback utilisateur avec `messages` :

```python
from django.contrib import messages

# Succès
messages.success(request, "Opération réussie")

# Info
messages.info(request, "Information importante")

# Avertissement
messages.warning(request, "Attention à ce point")

# Erreur
messages.error(request, "Une erreur s'est produite")
```

Dans le template :
```html
{% if messages %}
<div class="messages">
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }}">
        {{ message }}
    </div>
    {% endfor %}
</div>
{% endif %}
```

## Règles Importantes

### 1. Pas de logique métier dans les vues
```python
# ❌ MAUVAIS
def form_valid(self, form):
    client = Client.objects.create(...)
    # 50 lignes de logique métier
    return redirect('...')

# ✅ BON
def form_valid(self, form):
    client = ClientService.creer_client(...)
    return redirect('...')
```

### 2. Optimiser les requêtes
```python
# ❌ MAUVAIS (N+1 queries)
def get_queryset(self):
    return Facture.objects.all()

# ✅ BON
def get_queryset(self):
    return Facture.objects.select_related('client').prefetch_related('lignes')
```

### 3. Toujours utiliser des mixins
```python
# ❌ MAUVAIS (pas de protection)
class MaVue(ListView):
    pass

# ✅ BON
class MaVue(LoginRequiredMixin, ListView):
    pass
```

### 4. Success URL dynamique
```python
# ✅ BON
def get_success_url(self):
    return reverse_lazy('detail', kwargs={'pk': self.object.pk})
```

## Anti-Patterns à Éviter

❌ Function-based views
❌ Logique métier dans les vues
❌ Requêtes non optimisées (N+1)
❌ Pas de mixins d'authentification
❌ Pas de messages de feedback
❌ Success URL hardcodée
