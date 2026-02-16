# Instructions Agent IA - Projet kzone

## Stack Technique
- Backend : Django 4.2+ / Python 3.10+
- Frontend : Django Templates + jQuery 3.6+ / Bootstrap 5+
- BDD : PostgreSQL et il faut toujours prendre en considération la structure des données de base du fichier data_model.md (OBLIGATOIRE POUR TOUTE MODIFICATION DE MODEL DE DONNEES)
- CSS : Méthodologie BEM
- Nommage (variables et nom de fonctions) : `snake_case` minuscules (Python), `camelCase` premiere lettre minuscule(JavaScript)
- Toujours utiliser des template html réutilisable, modules et fonctions réutilisables

## Structure du Projet

```
kzone/
├── .ai/                           # Instructions pour toi
├── kzone/                         # Configuration Django
├── nom_app/                       # Applications métier
│   ├── templates/nom_app/         # HTML associé à l'app
│   ├── static/nom_app/            # CSS + JS associé à l'app
│   ├── media/nom_app/             # Media de l'app
│   ├── assets/nom_app/            # Assets spécifiques de l'app
│   ├── models.py                  # Structure données
│   ├── services.py                # OBLIGATOIRE - Logique métier
│   ├── views.py                   # CBV uniquement
│   ├── forms.py                   # Validation inputs
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
└── assets/                        # Images globales (logos, etc.)
```

## Règles Fondamentales

### 1. Séparation stricte des responsabilités
- **models.py** : Structure de données uniquement
- **services.py** : TOUTE la logique métier (obligatoire dès qu'il y a de la logique)
- **views.py** : Appelle services, retourne templates (CBV uniquement)
- **forms.py** : Validation des inputs
- **front** : Toujours utiliser le bootstrap, fair le css que si et seulement si pas d'autres solution en bootstrap

### 2. Git Flow Process
Voir `.ai/git-workflow.md` pour le détail. Résumé :
- Créer une branche AVANT toute modification : `[type]_[fonctionnalité]_[app]`
- Types : `feat`, `fix`, `chore`, `refactor`
- Jamais coder sur `master`/`main`/`develop`

### 3. Standards de code
- Docstrings obligatoires (classes, méthodes)
- Limite 300 lignes par fichier
- Type hints Python
- Pas de JS inline dans templates
- CSRF token sur tous les appels AJAX

### 4. Frontend jQuery
- Un fichier JS par module dans `static/js/`
- Charger dans `{% block javascript %}` en fin de template
- Obligatoire : CSRF token dans tous les appels AJAX

### 5. change model data Process
Voir `.ai/data_model.md` pour le détail. Résumé :
- Toujours valider le model de donner avec mi l'humain avant de faire les modification , notamment lors de l'analyse

## Workflow de Développement

### Phase 1 : Plan (OBLIGATOIRE)
1. Annoncer la branche à créer depuis `master`
2. Lister les fichiers à créer/modifier
3. Décrire l'architecture prévue
4. Décrire les changes sur les models de données en cas de modification / ajout ou suppression (model.py)
5. **Attendre validation avant de coder**

### Phase 2 : Act
1. Créer la branche Git
2. Coder selon les patterns (voir `.ai/patterns/`)
3. ajouter ou adapter les Tests unitaires et de couverture de code pour le nouveau code

4. Tester avec `python manage.py test`
5. Type-checker avec `mypy`

### Phase 3 : Reflect
1. Lister fichiers modifiés/créés
2. Migrations générées (`makemigrations --dry-run`)
3. Tests unitaires et de couverture de code ajoutés
4. Résumé des choix architecturaux
5. **Le code doit ^tre compréhensible, maintenable par un humain et évolutif pas trop complexe**

## Commandes Autorisées

### ✅ Sans demander
- Lire fichiers
- Type-check : `mypy apps/nom_app/`
- Format : `black apps/nom_app/` et `isort apps/nom_app/`
- Tests : `python manage.py test apps.nom_app`
- Migrations dry-run : `python manage.py makemigrations --dry-run`

### ⛔ Demander validation
- `pip install` / modifier `requirements.txt`
- Supprimer fichiers
- `git push`
- `python manage.py migrate`
- Modifier config production

## Patterns à Suivre
Consulte `.ai/patterns/` pour des exemples détaillés :
- `services.md` : Structure des services
- `views.md` : CBV avec exemples
- `models.md` : Modèles avec docstrings
- `frontend.md` : jQuery et AJAX

## Anti-Patterns Interdits
❌ Logique métier dans views
❌ JS inline dans templates
❌ Function-based views
❌ Requêtes N+1 (utilise `select_related`/`prefetch_related`)
❌ Fichiers > 300 lignes
❌ Absence de docstrings
❌ AJAX sans CSRF token

# ARCHITECTURE ET ORGANISATION DU CODE (DIRECTIVES GÉNÉRALES)

## 1. DÉCOUPAGE MODULAIRE (DOMAIN DRIVEN DESIGN)
L'agent doit structurer le projet en "Applications Django" correspondant chacune à un domaine fonctionnel unique.
- **Principe de Responsabilité Unique** : Chaque modèle doit résider dans l'application qui possède sa logique métier principale.
- **Exemple** : Si le besoin concerne la gestion des annonces, le modèle `Produit` doit être créé dans une application dédiée (ex: `gestion_catalogue`) et non dans l'application de présentation (ex: `accueil`).

## 2. GESTION DES IMPORTS ET DÉPENDANCES
- **Imports Explicites** : Toujours privilégier les chemins complets (ex: `from utilisateurs.models import Profil`).
- **Éviter les Cycles** : Dans les `models.py`, référencer les clés étrangères par leur nom de chaîne de caractères `app_name.ModelName` pour éviter les imports circulaires.
- **Exemple** : `vendeur = models.ForeignKey('utilisateurs.Utilisateur', on_delete=models.CASCADE)`.

## 4. MÉTHODOLOGIE DE TRAVAIL DE L'AGENT
1. **Analyse du Domaine** : Identifier l'application responsable du besoin. Si elle n'existe pas, la créer proprement.
2. **Implémentation Source** : Coder la logique (Modèle, Formulaire) dans l'application métier.
3. **Consommation** : Importer cette logique dans l'application de destination (celle qui affiche la page à l'utilisateur).
4. **Maintenance** : Garder les vues légères en déportant la logique complexe dans les formulaires ou des services.
