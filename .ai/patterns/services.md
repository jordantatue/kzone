# Pattern : Services Django

## Principe
**TOUTE logique métier doit être dans `services.py`, JAMAIS dans les vues.**

Les services encapsulent :
- Règles business
- Calculs complexes
- Orchestration de modèles
- Envoi d'emails/notifications
- Appels API externes
- Transactions atomiques

## Structure Type
```python
# apps/nom_app/services.py
from typing import Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import MonModele

class MonService:
    """
    Service gérant [description de la responsabilité].
    
    Responsabilités :
    - Création et validation de [entité]
    - Calcul de [logique métier]
    - Orchestration de [processus]
    """
    
    @staticmethod
    @transaction.atomic
    def creer_entite(param1: str, param2: int) -> MonModele:
        """
        Crée une nouvelle entité avec validation.
        
        Args:
            param1: Description du paramètre
            param2: Description du paramètre
            
        Returns:
            Instance de MonModele créée
            
        Raises:
            ValidationError: Si les données sont invalides
        """
        if param2 < 0:
            raise ValidationError("Le paramètre doit être positif")
        
        instance = MonModele.objects.create(
            champ1=param1,
            champ2=param2
        )
        
        instance.calculer_valeur()
        instance.save()
        
        return instance
```

## Exemple Concret : Service Transaction (Cœur Métier)
```python
# apps/transactions/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.catalogue.models import Produit
from apps.utilisateurs.models import Utilisateur
from .models import Transaction

class TransactionService:
    """
    Service gérant les transactions et le séquestre.
    
    Responsabilités :
    - Initier un achat sécurisé
    - Passer le produit en séquestre
    - Libérer ou rembourser après validation
    """

    @staticmethod
    @transaction.atomic
    def initier_achat(acheteur: Utilisateur, produit: Produit) -> Transaction:
        """
        Initie un achat sécurisé et place le produit en séquestre.
        
        Args:
            acheteur: L'utilisateur qui achète
            produit: Le produit concerné
            
        Returns:
            Transaction créée
            
        Raises:
            ValidationError: Si le vendeur tente d'acheter son propre produit
            ValidationError: Si le produit n'est pas disponible
        """
        if produit.vendeur == acheteur:
            raise ValidationError("Un vendeur ne peut pas acheter son propre produit.")
        
        if produit.statut != 'Disponible':
            raise ValidationError("Ce produit n'est plus disponible.")
        
        produit.statut = 'En_Séquestre'
        produit.save()
        
        return Transaction.objects.create(
            acheteur=acheteur,
            produit=produit,
            montant_total=produit.prix,
            statut_paiement='Bloqué_Séquestre'
        )
```

## Pattern de Test des Services (OBLIGATOIRE)

**On teste uniquement les règles métier critiques définies dans `data_model.md`.**
```python
# apps/transactions/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.transactions.services import TransactionService
from apps.catalogue.models import Produit
from apps.utilisateurs.models import Utilisateur

class TransactionServiceTest(TestCase):
    """Tests des règles métier critiques des transactions."""

    def setUp(self):
        self.vendeur = Utilisateur.objects.create_user(telephone="699000001")
        self.acheteur = Utilisateur.objects.create_user(telephone="699000002")
        self.produit = Produit.objects.create(
            vendeur=self.vendeur,
            statut='Disponible',
            prix=10000
        )

    def test_achat_securise_passe_produit_en_sequestre(self):
        """L'achat sécurisé doit mettre le produit en séquestre."""
        TransactionService.initier_achat(self.acheteur, self.produit)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.statut, 'En_Séquestre')

    def test_vendeur_ne_peut_pas_acheter_son_propre_produit(self):
        """Un vendeur ne peut pas initier un achat sur son propre produit."""
        with self.assertRaises(ValidationError):
            TransactionService.initier_achat(self.vendeur, self.produit)

    def test_achat_impossible_si_produit_non_disponible(self):
        """Un produit déjà en séquestre ne peut pas être acheté à nouveau."""
        self.produit.statut = 'En_Séquestre'
        self.produit.save()
        with self.assertRaises(ValidationError):
            TransactionService.initier_achat(self.acheteur, self.produit)
```

### Règles sur les tests
- Format : `test_[sujet]_[condition]_[résultat_attendu]`
- Un test = une seule règle métier
- Toujours tester le cas nominal ET le cas d'erreur
- Ne jamais tester qu'une page charge ou qu'un formulaire s'affiche

## Règles Importantes

### 1. Un service par responsabilité
- `TransactionService` : Séquestre et paiements
- `ProfilService` : Gestion profil utilisateur
- `CatalogueService` : Filtrage et recherche produits

### 2. Transactions atomiques
```python
@transaction.atomic
def initier_achat(acheteur, produit):
    produit.statut = 'En_Séquestre'
    produit.save()
    Transaction.objects.create(...)
    # Si erreur ici → rollback automatique du statut produit
```

### 3. Validation avant toute modification
```python
# Toujours valider d'abord, modifier ensuite
if produit.vendeur == acheteur:
    raise ValidationError("...")
# Seulement ici on modifie la base
produit.statut = 'En_Séquestre'
```

### 4. Type hints obligatoires
```python
# ✅ BON
def initier_achat(acheteur: Utilisateur, produit: Produit) -> Transaction:

# ❌ MAUVAIS
def initier_achat(acheteur, produit):
```

### 5. Limite 300 lignes
Si un service dépasse 300 lignes, créer des sous-services :
```python
# apps/transactions/services/__init__.py
from .sequestre import SequestreService
from .paiement import PaiementService
```

## Anti-Patterns à Éviter

❌ Logique métier dans les vues
❌ Requêtes DB directement dans les vues
❌ Services sans docstrings
❌ Pas de validation avant modification
❌ Pas de `@transaction.atomic` pour opérations multiples
❌ Pas de type hints
❌ Tests qui vérifient l'affichage plutôt que le comportement métier