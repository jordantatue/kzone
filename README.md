# kzone

Projet Django structure par application metier.

## Structure

```text
kzone/
├── .ai/
├── kzone/
├── acceuil/
│   ├── templates/acceuil/
│   ├── static/acceuil/
│   ├── media/acceuil/
│   ├── assets/acceuil/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── connexion/
│   ├── templates/connexion/
│   ├── static/connexion/
│   ├── media/connexion/
│   ├── assets/connexion/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
└── assets/
```

## Configuration Django

- `INSTALLED_APPS` utilise `acceuil` et `connexion`.
- `APP_DIRS = True` permet de charger les templates dans chaque app (`templates/nom_app/`).
- Les fichiers statiques sont resolus depuis `static/nom_app/` de chaque app.
- Les assets globaux (logo, etc.) sont servis via:
  - `ASSETS_URL = 'assets/'`
  - `ASSETS_ROOT = BASE_DIR / 'assets'`

## Regles fonctionnelles d'acces

- L'accueil (`/`) est accessible avec ou sans connexion.
- Apres connexion reussie, l'utilisateur est redirige vers l'accueil.
- Un utilisateur connecte peut se deconnecter depuis le bouton de la navbar.
- Sans connexion, les entrees de navbar liees aux fonctionnalites protegees (compte, suivi, panier) redirigent vers la page de connexion.

## Lancer le projet

```bash
python manage.py runserver
```
