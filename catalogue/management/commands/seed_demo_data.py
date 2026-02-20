"""Commande de seed pour injecter des donnees de demo dans la base K-Zone."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from catalogue.models import Categorie, ImageProduit, Localisation, Produit, ProduitAgricole, ProduitRetail
from profil.models import ProfilUtilisateur

User = get_user_model()

SEED_PASSWORD = "KzoneDemo123!"

SEED_LOCATIONS = [
    {"region": Localisation.RegionChoices.LITTORAL, "ville": "Douala", "quartier": "Akwa"},
    {"region": Localisation.RegionChoices.LITTORAL, "ville": "Douala", "quartier": "Bonanjo"},
    {"region": Localisation.RegionChoices.LITTORAL, "ville": "Douala", "quartier": "Bonamoussadi"},
    {"region": Localisation.RegionChoices.CENTRE, "ville": "Yaounde", "quartier": "Bastos"},
    {"region": Localisation.RegionChoices.CENTRE, "ville": "Yaounde", "quartier": "Mvog-Ada"},
    {"region": Localisation.RegionChoices.OUEST, "ville": "Bafoussam", "quartier": "Centre-ville"},
    {"region": Localisation.RegionChoices.NORD, "ville": "Garoua", "quartier": "Plateau"},
    {"region": Localisation.RegionChoices.SUD_OUEST, "ville": "Buea", "quartier": "Molyko"},
]

SEED_USERS = [
    {
        "username": "seed_pro_marchecentral",
        "email": "pro.marchecentral@kzone.demo",
        "first_name": "Paul",
        "last_name": "Njoya",
        "type_vendeur": ProfilUtilisateur.TypeVendeurChoices.PROFESSIONNEL,
        "numero_paiement": "699010101",
        "localisation": ("Littoral", "Douala", "Akwa"),
    },
    {
        "username": "seed_particulier_bastos",
        "email": "particulier.bastos@kzone.demo",
        "first_name": "Aline",
        "last_name": "Mbianda",
        "type_vendeur": ProfilUtilisateur.TypeVendeurChoices.PARTICULIER,
        "numero_paiement": "677010101",
        "localisation": ("Centre", "Yaounde", "Bastos"),
    },
    {
        "username": "seed_pro_agro_ouest",
        "email": "pro.agro.ouest@kzone.demo",
        "first_name": "Serge",
        "last_name": "Kemga",
        "type_vendeur": ProfilUtilisateur.TypeVendeurChoices.PROFESSIONNEL,
        "numero_paiement": "675010101",
        "localisation": ("Ouest", "Bafoussam", "Centre-ville"),
    },
    {
        "username": "seed_particulier_akwa",
        "email": "particulier.akwa@kzone.demo",
        "first_name": "Nadine",
        "last_name": "Ewane",
        "type_vendeur": ProfilUtilisateur.TypeVendeurChoices.PARTICULIER,
        "numero_paiement": "670010101",
        "localisation": ("Littoral", "Douala", "Bonamoussadi"),
    },
]

SEED_CATEGORIES = [
    {"slug": "retail", "nom": "Retail", "parent_slug": None},
    {"slug": "agricole", "nom": "Agricole", "parent_slug": None},
    {"slug": "telephones", "nom": "Telephones", "parent_slug": "retail"},
    {"slug": "electromenager", "nom": "Electromenager", "parent_slug": "retail"},
    {"slug": "mode-beaute", "nom": "Mode & Beaute", "parent_slug": "retail"},
    {"slug": "fruits-legumes", "nom": "Fruits & Legumes", "parent_slug": "agricole"},
    {"slug": "cereales-legumineuses", "nom": "Cereales & Legumineuses", "parent_slug": "agricole"},
    {"slug": "epices-produits-secs", "nom": "Epices & Produits secs", "parent_slug": "agricole"},
]

SEED_PRODUCTS = [
    {
        "titre": "iPhone 12 128Go",
        "description": "Telephone iOS en tres bon etat, batterie 87%, boite incluse.",
        "prix": Decimal("265000"),
        "vendeur": "seed_pro_marchecentral",
        "categorie_slug": "telephones",
        "localisation": ("Littoral", "Douala", "Akwa"),
        "type": "retail",
        "etat": ProduitRetail.EtatChoices.OCCASION,
        "images": [
            "https://picsum.photos/seed/kzone-iphone-1/1200/900",
            "https://picsum.photos/seed/kzone-iphone-2/1200/900",
        ],
    },
    {
        "titre": "Samsung Galaxy A54 Neuf",
        "description": "Version 256Go, dual sim, garantie vendeur 6 mois.",
        "prix": Decimal("210000"),
        "vendeur": "seed_pro_marchecentral",
        "categorie_slug": "telephones",
        "localisation": ("Littoral", "Douala", "Bonanjo"),
        "type": "retail",
        "etat": ProduitRetail.EtatChoices.NEUF,
        "images": [
            "https://picsum.photos/seed/kzone-samsung-1/1200/900",
            "https://picsum.photos/seed/kzone-samsung-2/1200/900",
        ],
    },
    {
        "titre": "Refrigerateur Hisense 220L",
        "description": "Faible consommation, ideal pour petit commerce ou famille.",
        "prix": Decimal("189000"),
        "vendeur": "seed_particulier_akwa",
        "categorie_slug": "electromenager",
        "localisation": ("Littoral", "Douala", "Bonamoussadi"),
        "type": "retail",
        "etat": ProduitRetail.EtatChoices.OCCASION,
        "images": [
            "https://picsum.photos/seed/kzone-frigo-1/1200/900",
            "https://picsum.photos/seed/kzone-frigo-2/1200/900",
        ],
    },
    {
        "titre": "Mixeur Moulinex 600W",
        "description": "Robot blender pratiquement neuf, utilise 3 fois.",
        "prix": Decimal("32000"),
        "vendeur": "seed_particulier_bastos",
        "categorie_slug": "electromenager",
        "localisation": ("Centre", "Yaounde", "Mvog-Ada"),
        "type": "retail",
        "etat": ProduitRetail.EtatChoices.RECONDITIONNE,
        "images": [
            "https://picsum.photos/seed/kzone-mixeur-1/1200/900",
            "https://picsum.photos/seed/kzone-mixeur-2/1200/900",
        ],
    },
    {
        "titre": "Sac de cacao premium 50kg",
        "description": "Cacao sec, tri manuel, pret pour export ou transformation locale.",
        "prix": Decimal("78000"),
        "vendeur": "seed_pro_agro_ouest",
        "categorie_slug": "cereales-legumineuses",
        "localisation": ("Ouest", "Bafoussam", "Centre-ville"),
        "type": "agricole",
        "region_origine": Localisation.RegionChoices.OUEST,
        "unite_mesure": "Sac",
        "jours_recolte": 6,
        "images": [
            "https://picsum.photos/seed/kzone-cacao-1/1200/900",
            "https://picsum.photos/seed/kzone-cacao-2/1200/900",
        ],
    },
    {
        "titre": "Plantain frais (regime)",
        "description": "Plantains selectionnes calibre export, excellent etat de maturite.",
        "prix": Decimal("9500"),
        "vendeur": "seed_pro_agro_ouest",
        "categorie_slug": "fruits-legumes",
        "localisation": ("Sud-Ouest", "Buea", "Molyko"),
        "type": "agricole",
        "region_origine": Localisation.RegionChoices.SUD_OUEST,
        "unite_mesure": "Regime",
        "jours_recolte": 2,
        "images": [
            "https://picsum.photos/seed/kzone-plantain-1/1200/900",
            "https://picsum.photos/seed/kzone-plantain-2/1200/900",
        ],
    },
    {
        "titre": "Tomates bio (caisse 20kg)",
        "description": "Tomates fraiches sans conservateurs, livraison Douala/Yaounde.",
        "prix": Decimal("14000"),
        "vendeur": "seed_particulier_bastos",
        "categorie_slug": "fruits-legumes",
        "localisation": ("Centre", "Yaounde", "Bastos"),
        "type": "agricole",
        "region_origine": Localisation.RegionChoices.CENTRE,
        "unite_mesure": "Caisse",
        "jours_recolte": 1,
        "images": [
            "https://picsum.photos/seed/kzone-tomate-1/1200/900",
            "https://picsum.photos/seed/kzone-tomate-2/1200/900",
        ],
    },
    {
        "titre": "Gingembre frais 10kg",
        "description": "Gingembre de qualite marchande pour cuisine, jus et infusion.",
        "prix": Decimal("18500"),
        "vendeur": "seed_particulier_akwa",
        "categorie_slug": "epices-produits-secs",
        "localisation": ("Nord", "Garoua", "Plateau"),
        "type": "agricole",
        "region_origine": Localisation.RegionChoices.NORD,
        "unite_mesure": "Lot 10kg",
        "jours_recolte": 3,
        "images": [
            "https://picsum.photos/seed/kzone-gingembre-1/1200/900",
            "https://picsum.photos/seed/kzone-gingembre-2/1200/900",
        ],
    },
]


class Command(BaseCommand):
    help = "Injecte un jeu de donnees de demonstration complet dans la base."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime les donnees seed precedentes avant reinsertion.",
        )
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="N'attache pas d'images aux produits seed.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=20,
            help="Timeout reseau (secondes) pour le telechargement des images.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.timeout_seconds = max(5, int(options["timeout"]))
        use_images = not options["no_images"]

        if options["reset"]:
            self._reset_seed_data()

        locations = self._seed_locations()
        categories = self._seed_categories()
        users = self._seed_users(locations)
        products_created, products_updated = self._seed_products(
            users=users,
            categories=categories,
            locations=locations,
            use_images=use_images,
        )

        self.stdout.write(self.style.SUCCESS("Seed termine avec succes."))
        self.stdout.write(
            f"- Utilisateurs seed: {len(SEED_USERS)} (mot de passe: {SEED_PASSWORD})"
        )
        self.stdout.write(
            f"- Produits seed: {products_created} crees, {products_updated} mis a jour"
        )
        self.stdout.write(
            f"- Dossier media: {Path('media').resolve()}"
        )

    def _reset_seed_data(self) -> None:
        usernames = [item["username"] for item in SEED_USERS]
        users = User.objects.filter(username__in=usernames)
        product_count = Produit.objects.filter(vendeur__in=users).count()
        user_count = users.count()
        users.delete()
        self.stdout.write(
            self.style.WARNING(
                f"Reset effectue: {user_count} utilisateurs seed et {product_count} produits supprimes."
            )
        )

    def _seed_locations(self) -> dict[tuple[str, str, str], Localisation]:
        mapping: dict[tuple[str, str, str], Localisation] = {}
        for payload in SEED_LOCATIONS:
            location, _ = Localisation.objects.get_or_create(
                region=payload["region"],
                ville=payload["ville"],
                quartier=payload["quartier"],
            )
            mapping[(location.region, location.ville, location.quartier)] = location
        return mapping

    def _seed_categories(self) -> dict[str, Categorie]:
        categories: dict[str, Categorie] = {}
        for payload in SEED_CATEGORIES:
            parent = categories.get(payload["parent_slug"])
            category, created = Categorie.objects.get_or_create(
                slug=payload["slug"],
                defaults={"nom": payload["nom"], "parent": parent},
            )
            changed = False
            if category.nom != payload["nom"]:
                category.nom = payload["nom"]
                changed = True
            if category.parent_id != (parent.id if parent else None):
                category.parent = parent
                changed = True
            if changed:
                category.save(update_fields=["nom", "parent"])
            categories[payload["slug"]] = category
            if created:
                self.stdout.write(f"Categorie creee: {category.slug}")
        return categories

    def _seed_users(
        self,
        locations: dict[tuple[str, str, str], Localisation],
    ) -> dict[str, User]:
        users_by_username: dict[str, User] = {}
        for payload in SEED_USERS:
            user, _ = User.objects.get_or_create(
                username=payload["username"],
                defaults={
                    "email": payload["email"],
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                },
            )
            user.email = payload["email"]
            user.first_name = payload["first_name"]
            user.last_name = payload["last_name"]
            user.set_password(SEED_PASSWORD)
            user.save()

            ProfilUtilisateur.objects.update_or_create(
                utilisateur=user,
                defaults={
                    "localisation_defaut": locations[payload["localisation"]],
                    "type_vendeur": payload["type_vendeur"],
                    "numero_paiement": payload["numero_paiement"],
                    "badge_trustcam": payload["type_vendeur"]
                    == ProfilUtilisateur.TypeVendeurChoices.PROFESSIONNEL,
                },
            )
            users_by_username[user.username] = user
        return users_by_username

    def _seed_products(
        self,
        *,
        users: dict[str, User],
        categories: dict[str, Categorie],
        locations: dict[tuple[str, str, str], Localisation],
        use_images: bool,
    ) -> tuple[int, int]:
        created = 0
        updated = 0

        for payload in SEED_PRODUCTS:
            product, was_created = Produit.objects.update_or_create(
                vendeur=users[payload["vendeur"]],
                titre=payload["titre"],
                defaults={
                    "categorie": categories[payload["categorie_slug"]],
                    "lieu_vente": locations[payload["localisation"]],
                    "description": payload["description"],
                    "prix": payload["prix"],
                    "statut": Produit.StatutChoices.DISPONIBLE,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

            if payload["type"] == "retail":
                ProduitAgricole.objects.filter(produit=product).delete()
                ProduitRetail.objects.update_or_create(
                    produit=product,
                    defaults={
                        "marque": payload["titre"].split(" ")[0],
                        "etat": payload["etat"],
                        "specifications": {
                            "livraison": True,
                            "retour_sous_48h": False,
                        },
                    },
                )
            else:
                ProduitRetail.objects.filter(produit=product).delete()
                ProduitAgricole.objects.update_or_create(
                    produit=product,
                    defaults={
                        "region_origine": payload["region_origine"],
                        "unite_mesure": payload["unite_mesure"],
                        "date_recolte": timezone.now().date()
                        - timedelta(days=payload["jours_recolte"]),
                        "duree_conservation": 10,
                    },
                )

            if use_images:
                self._replace_product_images(product, payload["images"])
            else:
                product.images.all().delete()

        return created, updated

    def _replace_product_images(self, product: Produit, urls: list[str]) -> None:
        product.images.all().delete()
        for index, image_url in enumerate(urls, start=1):
            binary, extension = self._download_or_placeholder(image_url, product.titre)
            image = ImageProduit(produit=product, ordre=index)
            filename = f"{slugify(product.titre)[:50]}-{index}.{extension}"
            image.image.save(filename, ContentFile(binary), save=True)

    def _download_or_placeholder(self, url: str, label: str) -> tuple[bytes, str]:
        try:
            request = Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; KZoneSeeder/1.0)"},
            )
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read()
                if not payload:
                    raise ValueError("Le fichier distant est vide.")
                content_type = (response.headers.get("Content-Type") or "").split(";")[0]
            extension = self._guess_extension(url=url, content_type=content_type)
            return payload, extension
        except Exception as exc:
            self.stderr.write(
                self.style.WARNING(
                    f"Echec telechargement image ({url}): {exc}. Placeholder SVG utilise."
                )
            )
            return self._build_svg_placeholder(label), "svg"

    def _guess_extension(self, *, url: str, content_type: str) -> str:
        from_url = Path(urlparse(url).path).suffix.lower().lstrip(".")
        if from_url in {"jpg", "jpeg", "png", "webp", "gif", "svg"}:
            return "jpg" if from_url == "jpeg" else from_url

        mapping = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/svg+xml": "svg",
        }
        return mapping.get(content_type.lower(), "jpg")

    def _build_svg_placeholder(self, label: str) -> bytes:
        safe_label = escape(label[:28])
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='900' viewBox='0 0 1200 900'>"
            "<defs><linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>"
            "<stop offset='0%' stop-color='#005a2f'/>"
            "<stop offset='100%' stop-color='#22c55e'/>"
            "</linearGradient></defs>"
            "<rect width='1200' height='900' fill='url(#g)'/>"
            "<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' "
            "font-family='Arial, sans-serif' font-size='56' fill='#ffffff'>"
            f"{safe_label}"
            "</text></svg>"
        )
        return svg.encode("utf-8")
