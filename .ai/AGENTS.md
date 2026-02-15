# Instructions Agent IA - Projet kzone

## Stack Technique
- Backend : Django 4.2+ / Python 3.10+
- Frontend : Django Templates + jQuery 3.6+ / Bootstrap 5+
- BDD : PostgreSQL
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

## Workflow de Développement

### Phase 1 : Plan (OBLIGATOIRE)
1. Annoncer la branche à créer depuis `master`
2. Lister les fichiers à créer/modifier
3. Décrire l'architecture prévue
4. **Attendre validation avant de coder**

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
