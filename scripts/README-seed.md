# Seed demo data

## Option 1 - Powershell
```powershell
.\scripts\seed_demo_data.ps1 -Reset
```

## Option 2 - CMD
```bat
scripts\seed_demo_data.bat --reset
```

## Option 3 - Direct Django command
```powershell
env\Scripts\python.exe manage.py seed_demo_data --reset
```

## Useful flags
- `--reset`: supprime d'abord les donnees seed precedentes
- `--no-images`: insere les produits sans images
- `--timeout 30`: change le timeout reseau en secondes

Les images sont telechargees dans `media/catalogue/produits/`.
