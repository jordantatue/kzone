================================================================================
SCHEMA CONCEPTUEL DE DONNÉES : CAM-MARKET HUB (TRUSTCAM)
================================================================================

1. DOMAINE : IDENTITÉ & ACCÈS (Extension Django Auth)
--------------------------------------------------------------------------------
[Utilisateur] (Hérite de AbstractUser)
    - id : UUID (PK)
    - telephone : String (Unique, Indexé) <--- Identifiant Principal
    - mot_de_passe : String
    - est_verifie : Boolean (Badge TrustCam)
    - date_jointure : DateTime
    - groupes : FK (Django Groups)
    - permissions : FK (Django Permissions)

[Profil] (Extension 1:1 de Utilisateur)
    - utilisateur_id : FK (Utilisateur)
    - photo_profil : ImageField
    - localisation_defaut : FK (Localisation)
    - moyen_paiement_prefere : Enum (OM, MOMO, CB)
    - numero_paiement : String
    - note_vendeur : Decimal (Moyenne des avis)

2. DOMAINE : GÉOGRAPHIE & FILTRES
--------------------------------------------------------------------------------
[Localisation]
    - id : Integer (PK)
    - region : String (Enum: Littoral, Centre, Ouest, etc.)
    - ville : String
    - quartier : String
    - coordonnees_gps : Point (Optionnel pour livraison)

[Categorie]
    - id : Integer (PK)
    - nom : String
    - slug : String (Unique)
    - id_parent : FK (Self) <--- Structure récursive pour sous-catégories

3. DOMAINE : CATALOGUE & MÉDIAS (Héritage Multi-table)
--------------------------------------------------------------------------------
[Produit] (Classe Mère)
    - id : UUID (PK)
    - vendeur : FK (Utilisateur)
    - categorie : FK (Categorie)
    - lieu_vente : FK (Localisation)
    - titre : String (Indexé)
    - description : Text
    - prix : Decimal
    - statut : Enum (Disponible, En_Séquestre, Vendu)
    - date_creation : DateTime

[ProduitAgricole] (Hérite de Produit)
    - region_origine : String
    - unite_mesure : String (Sac, Seau, Kg)
    - date_recolte : Date
    - duree_conservation : Integer (Jours)

[ProduitRetail] (Hérite de Produit)
    - marque : String
    - etat : Enum (Neuf, Occasion)
    - specifications : JSON (Pour la flexibilité des attributs)

[GalerieMedia] (Relation 1:N avec Produit)
    - id : Integer (PK)
    - produit : FK (Produit)
    - fichier : FileURL (Image ou Vidéo)
    - est_video : Boolean
    - ordre : Integer (Pour l'affichage)

4. DOMAINE : TRANSACTION & SÉQUESTRE (Le Cœur du Système)
--------------------------------------------------------------------------------
[Transaction]
    - id : UUID (PK)
    - acheteur : FK (Utilisateur)
    - produit : FK (Produit)
    - montant_total : Decimal
    - frais_plateforme : Decimal
    - statut_paiement : Enum (En_Attente, Bloqué_Séquestre, Libéré, Remboursé)
    - code_validation : String (Hashé, pour déblocage livraison)
    - reference_mobile_money : String (ID Transaction Opérateur)
    - cree_le : DateTime
    - mis_a_jour_le : DateTime

================================================================================
INVARIANTS MÉTIER À COUVRIR PAR LES TESTS
================================================================================
Ces règles définissent le comportement critique du système.
Chacune DOIT avoir un test unitaire dans le service correspondant.
Les règles d'affichage (sidebar, filtres, ordre) n'ont PAS besoin de tests.

| Règle métier                                                        | Priorité |
|---------------------------------------------------------------------|----------|
| Seule `Transaction` peut modifier le `statut` d'un `Produit`        | CRITIQUE |
| Un vendeur ne peut pas être acheteur de son propre `Produit`        | CRITIQUE |
| `statut_paiement = Bloqué_Séquestre` → `statut produit = En_Séquestre` | CRITIQUE |
| `note_vendeur` = moyenne recalculée à chaque nouvel avis reçu       | HAUTE    |
| Création automatique du `Profil` au premier accès utilisateur       | HAUTE    |
| Un `ProduitAgricole` ne peut pas exister sans `Produit` parent      | NORMALE  |

================================================================================
NOTES POUR L'AGENT IA :
- L'héritage Produit -> ProduitAgricole utilise 'OneToOneField' masqué par Django.
- La table 'Transaction' est la seule habilitée à modifier le 'statut' du Produit.
- Les modèles doivent être implémentés dans les fichiers models.py des applications django en lien fonctionnel principal (ex: model produit dans gestion_catalogue)
================================================================================
# DIRECTIVE TECHNIQUE : GESTION DES MÉDIAS (HYBRIDE)
- **Stockage physique** : Utiliser le système de fichiers (FileSystemStorage).
- **Modèle Django** : Utiliser `models.ImageField` et `models.FileField`.
- **Performance** : L'agent doit configurer 'MEDIA_URL' et 'MEDIA_ROOT'.
- **Sécurité** : Pour les documents sensibles (KYC), stocker dans un dossier protégé non accessible publiquement par URL directe.

## HIÉRARCHIE ET FLUX DE DONNÉES
- **Applications Métier (Back-end)** : Elles contiennent les modèles, les formulaires de gestion et la logique de base (CRUD).
- **Applications de Rendu (Front-end)** : Elles (comme `accueil` ou `dashboard`) servent à l'affichage. Elles doivent **importer** les composants des applications métier.
- **Exemple** : Pour afficher un formulaire de création de produit sur la page d'accueil, l'agent doit importer `ProduitForm` depuis `gestion_catalogue.forms` au lieu de le redéfinir localement.
================================================================================