"""Formulaires de gestion du profil utilisateur."""

from __future__ import annotations

from django import forms

from annonces.models import Localisation

from .models import ProfilUtilisateur


class ProfilIdentiteForm(forms.ModelForm):
    """Formulaire d'edition des informations personnelles."""

    full_name = forms.CharField(
        max_length=150,
        label="Nom complet",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nom et prenom"}
        ),
    )
    region = forms.ChoiceField(
        choices=[("", "Selectionner une region")] + list(Localisation.RegionChoices.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    ville = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ville"}),
    )
    quartier = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Quartier"}),
    )

    class Meta:
        """Configuration du formulaire principal."""

        model = ProfilUtilisateur
        fields = ("photo_profil",)
        widgets = {"photo_profil": forms.ClearableFileInput(attrs={"class": "form-control"})}

    def __init__(self, *args, user=None, **kwargs):
        """Initialise le formulaire avec les valeurs actuelles du profil."""
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["full_name"].initial = f"{user.first_name} {user.last_name}".strip()
        if self.instance and self.instance.localisation_defaut:
            localisation = self.instance.localisation_defaut
            self.fields["region"].initial = localisation.region
            self.fields["ville"].initial = localisation.ville
            self.fields["quartier"].initial = localisation.quartier

    def clean_full_name(self) -> str:
        """Verifie qu'un nom complet est present."""
        full_name = self.cleaned_data["full_name"].strip()
        if len(full_name) < 3:
            raise forms.ValidationError("Le nom complet doit contenir au moins 3 caracteres.")
        return full_name

    def save(self, commit: bool = True) -> ProfilUtilisateur:
        """Persiste les modifications sur l'utilisateur et son profil."""
        profil = super().save(commit=False)
        if self.user:
            full_name = self.cleaned_data["full_name"].split()
            self.user.first_name = full_name[0]
            self.user.last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""
            if commit:
                self.user.save(update_fields=["first_name", "last_name"])

        region = self.cleaned_data.get("region", "")
        ville = self.cleaned_data.get("ville", "").strip()
        quartier = self.cleaned_data.get("quartier", "").strip()
        if region and ville and quartier:
            localisation, _ = Localisation.objects.get_or_create(
                region=region,
                ville=ville,
                quartier=quartier,
            )
            profil.localisation_defaut = localisation

        if commit:
            profil.save()
        return profil


class ProfilFinanceForm(forms.ModelForm):
    """Formulaire d'edition des parametres financiers du profil."""

    class Meta:
        """Configuration du formulaire financier."""

        model = ProfilUtilisateur
        fields = ("moyen_paiement_prefere", "numero_paiement")
        widgets = {
            "moyen_paiement_prefere": forms.Select(attrs={"class": "form-select"}),
            "numero_paiement": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: 6XXXXXXXX"}
            ),
        }

    def clean_numero_paiement(self) -> str:
        """Verifie un format minimal de numero de paiement."""
        numero = self.cleaned_data["numero_paiement"].strip()
        if numero and len(numero) < 8:
            raise forms.ValidationError("Le numero de paiement semble trop court.")
        return numero

