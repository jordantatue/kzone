# Git Workflow - Projet kzone

## Règle Absolue
**JAMAIS coder directement sur `master`, `main`, `integration` ou `develop`.**

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

### 4. Commits
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
- Tests unitaires pour les règles métier impactées"

git commit -m "[FIX] connexion : Correction validation email

- Regex email plus stricte dans forms.py
- Test cas nominal + cas email invalide"
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
python manage.py test apps.nom_app
mypy apps/nom_app/
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
- Règles métier couvertes par les nouveaux tests

## Commandes Git Essentielles

### Vérifier l'état
```bash
git status
git branch
git log --oneline -5
```

### Annuler des modifications
```bash
git checkout -- fichier.py
git reset HEAD~1
git reset --hard HEAD~1
```

### Commits partiels (recommandé)
```bash
git add -p
```

### Nettoyage de branche
Après merge de la PR :
```bash
git checkout master
git pull origin master
git branch -d feat_paginationListe_clients
```

## Checklist Avant Push

- [ ] Branche créée avec nomenclature correcte
- [ ] Commits avec messages descriptifs
- [ ] Tests passent (`python manage.py test`)
- [ ] Code formaté (`black` + `isort`)
- [ ] Type-check OK (`mypy`)
- [ ] Pas de fichiers sensibles (`.env`, `db.sqlite3`)
- [ ] Migrations dry-run OK si modèles modifiés
- [ ] Tests ajoutés UNIQUEMENT pour les règles métier nouvelles ou modifiées
- [ ] Aucun test de type "la page retourne 200" ajouté
- [ ] Chaque nouveau service a au moins un test cas nominal ET un test cas d'erreur

## Erreurs à Éviter

❌ Coder sur `master`
❌ Noms de branches avec espaces ou majuscules
❌ Commits avec message vague ("fix bug", "update")
❌ Push sans tests
❌ Merge sans validation humaine
❌ Commits énormes (50+ fichiers)
❌ Ajouter des tests qui vérifient qu'une page charge