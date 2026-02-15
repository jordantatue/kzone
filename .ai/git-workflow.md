# Git Workflow - Projet kzone

## Règle Absolue
**JAMAIS coder directement sur `master`, `main` ou `develop`.**

## Nomenclature des Branches

Format strict : `[type]_[fonctionnalité]_[app]`

### Types autorisés
- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `chore` : Modification de modèles/structure
- `refactor` : Refactorisation sans changement fonctionnel

### Exemples valides
```
feat_tableauStats_accueil
fix_authentification_connexion
chore_ajoutModelServices_accueil
refactor_optimisationQueries_clients
```

### Exemples INVALIDES
❌ `nouvelle-feature` (pas de type, tirets au lieu d'underscores)
❌ `FIX_bug` (majuscules)
❌ `feat-ajout-stats` (tirets au lieu d'underscores)

## Workflow Étape par Étape

### 1. Avant de coder : Annonce
Avant toute modification, tu DOIS annoncer :

```
"Je vais créer la branche feat_paginationListe_clients depuis master pour ajouter 
la pagination aux listes de clients."
```

**Attends validation humaine avant de continuer.**

### 2. Création de la branche
```bash
git checkout master
git pull origin master
git checkout -b feat_paginationListe_clients
```

### 3. Développement
Code en suivant les conventions de `.ai/AGENTS.md`.

### 4. Commits fréquents

Format des messages de commit :
```
[TYPE] [App(s)] : Description claire

Détails techniques si nécessaire
```

Exemples :
```bash
git commit -m "[FEAT] clients : Ajout pagination dans ListView

- Ajout paramètre paginate_by=25
- Création template pagination.html
- Tests unitaires pour pagination"

git commit -m "[FIX] connexion : Correction validation email

- Regex email plus stricte dans forms.py
- Test avec emails invalides"

git commit -m "[CHORE] clients : Ajout modèle ClientNote

- Migration 0003_clientnote
- Relation ForeignKey vers Client
- Admin configuration"
```

### 5. Commit granulaire
Un commit = un changement logique.

✅ BON :
```
Commit 1: [FEAT] clients : Création modèle Client
Commit 2: [FEAT] clients : Service ClientService
Commit 3: [FEAT] clients : Vues CRUD Client
Commit 4: [FEAT] clients : Templates liste et détail
```

❌ MAUVAIS :
```
Commit 1: [FEAT] clients : Tout le module clients (50 fichiers)
```

### 6. Tests avant commit
Avant chaque commit, vérifie :
```bash
# Tests unitaires
python manage.py test apps.nom_app

# Type checking
mypy apps/nom_app/

# Format du code
black apps/nom_app/
isort apps/nom_app/
```

### 7. Push de la branche
```bash
git push origin feat_paginationListe_clients
```

### 8. Création Pull Request
**Ne fais PAS de merge automatique.** Crée une PR pour validation humaine avec :
- Description des modifications
- Liste des fichiers modifiés
- Screenshots si UI modifiée
- Tests ajoutés/modifiés

## Commandes Git Essentielles

### Vérifier l'état
```bash
git status                    # Fichiers modifiés
git branch                    # Branche actuelle
git log --oneline -5          # 5 derniers commits
```

### Annuler des modifications
```bash
git checkout -- fichier.py    # Annuler modifications non commitées
git reset HEAD~1              # Annuler dernier commit (garde les modifs)
git reset --hard HEAD~1       # Annuler dernier commit (supprime les modifs)
```

### Commits partiels (recommandé)
```bash
git add -p                    # Commit granulaire (ligne par ligne)
```

### Nettoyage de branche
Après merge de la PR :
```bash
git checkout master
git pull origin master
git branch -d feat_paginationListe_clients  # Suppression locale
```

## Scénarios Fréquents

### Scénario 1 : Feature complète
```bash
git checkout master
git pull
git checkout -b feat_exportPDF_factures

# Développement...
git add apps/factures/services.py
git commit -m "[FEAT] factures : Service génération PDF"

git add apps/factures/views.py
git commit -m "[FEAT] factures : Vue export PDF"

git add apps/factures/templates/
git commit -m "[FEAT] factures : Template PDF"

git push origin feat_exportPDF_factures
# Créer PR sur GitHub/GitLab
```

### Scénario 2 : Bug urgent
```bash
git checkout master
git pull
git checkout -b fix_calculTotal_factures

# Correction du bug
git add apps/factures/services.py
git commit -m "[FIX] factures : Correction calcul total TTC

Le calcul ne prenait pas en compte la TVA à 5.5%.
Ajout test unitaire pour vérifier."

git push origin fix_calculTotal_factures
# Créer PR urgente
```

### Scénario 3 : Refactorisation
```bash
git checkout master
git pull
git checkout -b refactor_optimisationQueries_clients

# Refactorisation
git add apps/clients/views.py
git commit -m "[REFACTOR] clients : Ajout select_related

Optimisation des queries pour éviter N+1.
Temps de réponse réduit de 800ms à 150ms."

git push origin refactor_optimisationQueries_clients
```

## Checklist Avant Push

- [ ] Branche créée avec nomenclature correcte
- [ ] Commits avec messages descriptifs
- [ ] Tests passent (`python manage.py test`)
- [ ] Code formaté (`black` + `isort`)
- [ ] Type-check OK (`mypy`)
- [ ] Pas de fichiers sensibles (`.env`, `db.sqlite3`)
- [ ] Migrations dry-run OK si modèles modifiés

## Erreurs à Éviter

❌ Coder sur `master`
❌ Noms de branches avec espaces ou majuscules
❌ Commits avec message vague ("fix bug", "update")
❌ Push sans tests
❌ Merge sans validation humaine
❌ Commits énormes (50+ fichiers)
