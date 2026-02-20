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
        # Validation métier
        if param2 < 0:
            raise ValidationError("Le paramètre doit être positif")
        
        # Création
        instance = MonModele.objects.create(
            champ1=param1,
            champ2=param2
        )
        
        # Actions post-création
        instance.calculer_valeur()
        instance.save()
        
        return instance
    
    @staticmethod
    def calculer_statistiques(date_debut, date_fin) -> dict:
        """
        Calcule les statistiques sur une période.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        # Logique de calcul
        pass
```

## Exemples Concrets

### Service d'authentification

```python
# apps/connexion/services.py
from typing import Optional
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
import re

class AuthService:
    """
    Service gérant l'authentification et inscription utilisateurs.
    
    Responsabilités :
    - Inscription avec validation email
    - Connexion utilisateur
    - Envoi emails de bienvenue
    """
    
    @staticmethod
    def valider_email(email: str) -> bool:
        """Valide le format d'un email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    @transaction.atomic
    def inscrire_utilisateur(
        email: str,
        password: str,
        prenom: str,
        nom: str
    ) -> User:
        """
        Inscrit un nouvel utilisateur.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            prenom: Prénom
            nom: Nom de famille
            
        Returns:
            User créé et activé
            
        Raises:
            ValidationError: Si email invalide ou déjà utilisé
        """
        # Validation email
        if not AuthService.valider_email(email):
            raise ValidationError("Format d'email invalide")
        
        # Vérifier unicité
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé")
        
        # Création utilisateur
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom
        )
        
        # Envoi email bienvenue (appel autre service)
        from apps.notifications.services import EmailService
        EmailService.envoyer_email_bienvenue(user)
        
        return user
    
    @staticmethod
    def connecter_utilisateur(request, email: str, password: str) -> Optional[User]:
        """
        Authentifie et connecte un utilisateur.
        
        Args:
            request: Objet request Django
            email: Email de l'utilisateur
            password: Mot de passe
            
        Returns:
            User si authentification réussie, None sinon
        """
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return user
        return None
```

### Service de facturation

```python
# apps/factures/services.py
from decimal import Decimal
from typing import List
from django.db import transaction
from django.utils import timezone
from .models import Facture, LigneFacture, Client

class FacturationService:
    """
    Service gérant la création et calcul des factures.
    
    Responsabilités :
    - Création factures avec lignes
    - Calcul TVA et totaux
    - Génération numéros facture
    """
    
    TVA_NORMALE = Decimal('0.20')  # 20%
    TVA_REDUITE = Decimal('0.055')  # 5.5%
    
    @staticmethod
    def generer_numero_facture() -> str:
        """
        Génère un numéro de facture unique.
        
        Format: FAC-YYYYMM-NNNN
        Exemple: FAC-202501-0042
        """
        maintenant = timezone.now()
        prefix = f"FAC-{maintenant.year}{maintenant.month:02d}"
        
        # Compter factures du mois
        count = Facture.objects.filter(
            numero__startswith=prefix
        ).count()
        
        return f"{prefix}-{count + 1:04d}"
    
    @staticmethod
    @transaction.atomic
    def creer_facture(
        client: Client,
        lignes: List[dict],
        taux_tva: Decimal = TVA_NORMALE
    ) -> Facture:
        """
        Crée une facture avec ses lignes.
        
        Args:
            client: Client facturé
            lignes: Liste de dicts avec 'designation', 'quantite', 'prix_unitaire'
            taux_tva: Taux de TVA à appliquer
            
        Returns:
            Facture créée avec totaux calculés
            
        Raises:
            ValidationError: Si données invalides
        """
        # Création facture
        facture = Facture.objects.create(
            numero=FacturationService.generer_numero_facture(),
            client=client,
            date_emission=timezone.now().date(),
            taux_tva=taux_tva
        )
        
        # Création lignes et calcul totaux
        total_ht = Decimal('0')
        for ligne_data in lignes:
            ligne = LigneFacture.objects.create(
                facture=facture,
                designation=ligne_data['designation'],
                quantite=ligne_data['quantite'],
                prix_unitaire=ligne_data['prix_unitaire']
            )
            total_ht += ligne.montant_ht()
        
        # Mise à jour totaux facture
        facture.montant_ht = total_ht
        facture.montant_tva = total_ht * taux_tva
        facture.montant_ttc = total_ht + facture.montant_tva
        facture.save()
        
        return facture
    
    @staticmethod
    def calculer_ca_periode(client: Client, date_debut, date_fin) -> Decimal:
        """
        Calcule le CA d'un client sur une période.
        
        Args:
            client: Client concerné
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            Chiffre d'affaires TTC
        """
        factures = Facture.objects.filter(
            client=client,
            date_emission__gte=date_debut,
            date_emission__lte=date_fin,
            statut='payee'
        )
        
        return sum(f.montant_ttc for f in factures)
```

### Service d'export PDF

```python
# apps/documents/services.py
from typing import Optional
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

class PDFService:
    """
    Service gérant la génération de documents PDF.
    
    Responsabilités :
    - Génération PDF factures
    - Génération PDF rapports
    """
    
    @staticmethod
    def generer_pdf_facture(facture) -> HttpResponse:
        """
        Génère un PDF pour une facture.
        
        Args:
            facture: Instance de Facture
            
        Returns:
            HttpResponse avec PDF généré
        """
        # Créer buffer mémoire
        buffer = io.BytesIO()
        
        # Créer PDF
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # En-tête
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, f"Facture {facture.numero}")
        
        # Informations client
        p.setFont("Helvetica", 12)
        y = height - 100
        p.drawString(50, y, f"Client: {facture.client.nom}")
        p.drawString(50, y - 20, f"Date: {facture.date_emission}")
        
        # Lignes de facture
        y -= 60
        p.drawString(50, y, "Désignation")
        p.drawString(300, y, "Qté")
        p.drawString(400, y, "Prix HT")
        
        y -= 20
        for ligne in facture.lignes.all():
            p.drawString(50, y, ligne.designation[:30])
            p.drawString(300, y, str(ligne.quantite))
            p.drawString(400, y, f"{ligne.montant_ht()}€")
            y -= 20
        
        # Totaux
        y -= 40
        p.drawString(300, y, f"Total HT: {facture.montant_ht}€")
        y -= 20
        p.drawString(300, y, f"TVA ({facture.taux_tva*100}%): {facture.montant_tva}€")
        y -= 20
        p.setFont("Helvetica-Bold", 12)
        p.drawString(300, y, f"Total TTC: {facture.montant_ttc}€")
        
        # Finaliser PDF
        p.showPage()
        p.save()
        
        # Préparer réponse
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
        
        return response
```

## Règles Importantes

### 1. Un service par responsabilité
Ne pas créer un service fourre-tout. Découper en services spécialisés :
- `AuthService` : Authentification
- `EmailService` : Envoi emails
- `FacturationService` : Gestion factures
- `StatistiquesService` : Calculs statistiques

### 2. Transactions atomiques
Utiliser `@transaction.atomic` pour les opérations qui doivent être groupées :

```python
@transaction.atomic
def creer_commande(client, lignes):
    commande = Commande.objects.create(client=client)
    for ligne in lignes:
        LigneCommande.objects.create(commande=commande, **ligne)
    # Si erreur ici, tout est rollback automatiquement
    return commande
```

### 3. Validation avant création
Toujours valider les données avant de créer des objets :

```python
@staticmethod
def creer_client(email: str, nom: str) -> Client:
    # Validation
    if not email or '@' not in email:
        raise ValidationError("Email invalide")
    
    if Client.objects.filter(email=email).exists():
        raise ValidationError("Email déjà utilisé")
    
    # Création seulement si validation OK
    return Client.objects.create(email=email, nom=nom)
```

### 4. Type hints obligatoires
Toujours typer les arguments et retours :

```python
# ✅ BON
def calculer_total(montant: Decimal, tva: Decimal) -> Decimal:
    return montant * (1 + tva)

# ❌ MAUVAIS
def calculer_total(montant, tva):
    return montant * (1 + tva)
```

### 5. Limite 300 lignes
Si un service dépasse 300 lignes, créer des sous-services :

```python
# apps/factures/services/__init__.py
from .facturation import FacturationService
from .export import ExportService
from .calcul import CalculService
```

## Anti-Patterns à Éviter

❌ Logique métier dans les vues
❌ Requêtes DB directement dans les vues
❌ Services sans docstrings
❌ Pas de validation avant création
❌ Pas de `@transaction.atomic` pour opérations multiples
❌ Pas de type hints
