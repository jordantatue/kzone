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
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Produit

class ProduitListView(LoginRequiredMixin, ListView):
    """Vue listant les produits avec pagination."""
    model = Produit
    template_name = 'catalogue/liste.html'
    context_object_name = 'produits'
    paginate_by = 25
    
    def get_queryset(self):
        return Produit.objects.select_related(
            'vendeur', 'categorie', 'lieu_vente'
        ).filter(statut='Disponible').order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .services import CatalogueService
        context['categories'] = CatalogueService.obtenir_categories_avec_comptage()
        return context
```

### DetailView - Afficher un détail
```python
from django.views.generic import DetailView

class ProduitDetailView(DetailView):
    """Vue affichant le détail d'un produit."""
    model = Produit
    template_name = 'catalogue/detail.html'
    context_object_name = 'produit'
    
    def get_queryset(self):
        return Produit.objects.select_related(
            'vendeur', 'categorie', 'lieu_vente'
        ).prefetch_related('galeriemedia_set')
```

### CreateView / UpdateView / DeleteView
```python
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ProduitForm
from .services import CatalogueService

class ProduitCreateView(LoginRequiredMixin, CreateView):
    """Création d'un produit."""
    model = Produit
    form_class = ProduitForm
    template_name = 'catalogue/form.html'
    
    def form_valid(self, form):
        try:
            produit = CatalogueService.creer_produit(
                vendeur=self.request.user,
                **form.cleaned_data
            )
            messages.success(self.request, "Produit créé avec succès")
            return redirect(reverse_lazy('catalogue:detail', kwargs={'pk': produit.pk}))
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
```

## Ce qu'on teste dans les vues (et pas ailleurs)

On ne teste PAS que les pages chargent.
On teste uniquement les **contrôles d'accès** qui ont une valeur métier :
```python
# apps/catalogue/tests.py
from django.test import TestCase
from django.urls import reverse

class AccesVuesTest(TestCase):
    """Tests des règles d'accès aux vues."""

    def test_dashboard_redirige_si_non_connecte(self):
        """Le dashboard est protégé par authentification."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/connexion/?next=/dashboard/')

    def test_achat_securise_refuse_pour_vendeur_proprietaire(self):
        """Un vendeur ne peut pas déclencher l'achat de son propre produit."""
        self.client.force_login(self.vendeur)
        response = self.client.post(
            reverse('achat_securise', args=[self.produit.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.statut, 'Disponible')
```

### Ce qu'on ne teste PAS dans les vues
- ❌ `response.status_code == 200` sur une page publique
- ❌ Que le bon template est rendu
- ❌ Les filtres AJAX d'affichage
- ❌ Le comptage dans la sidebar

## Mixins Utiles

### LoginRequiredMixin
```python
class MaVue(LoginRequiredMixin, ListView):
    login_url = '/connexion/'
```

### UserPassesTestMixin - Contrôle propriétaire
```python
from django.contrib.auth.mixins import UserPassesTestMixin

class ProduitUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        """Seul le vendeur propriétaire peut modifier."""
        produit = self.get_object()
        return produit.vendeur == self.request.user
```

## Règles Importantes

### 1. Pas de logique métier dans les vues
```python
# ❌ MAUVAIS
def form_valid(self, form):
    produit = Produit.objects.create(...)
    produit.statut = 'En_Séquestre'
    produit.save()
    Transaction.objects.create(...)

# ✅ BON
def form_valid(self, form):
    transaction = TransactionService.initier_achat(self.request.user, produit)
    return redirect(...)
```

### 2. Optimiser les requêtes
```python
# ❌ N+1 queries
def get_queryset(self):
    return Produit.objects.all()

# ✅ BON
def get_queryset(self):
    return Produit.objects.select_related('vendeur', 'categorie').prefetch_related('galeriemedia_set')
```

### 3. Toujours utiliser des mixins d'accès
```python
# ❌ MAUVAIS
class MaVue(ListView):
    pass

# ✅ BON
class MaVue(LoginRequiredMixin, ListView):
    pass
```

### 4. Feedback utilisateur systématique
```python
messages.success(request, "Opération réussie")
messages.error(request, "Une erreur s'est produite")
```

## Anti-Patterns à Éviter

❌ Function-based views
❌ Logique métier dans les vues
❌ Requêtes non optimisées (N+1)
❌ Pas de mixins d'authentification
❌ Pas de messages de feedback
❌ Tester que les pages chargent (HTTP 200) dans les tests de vues