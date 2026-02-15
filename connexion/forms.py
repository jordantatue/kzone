from django import forms

class ConnexionForm(forms.Form):
    """
    Formulaire de connexion pour les utilisateurs.

    Ce formulaire capture l'email et le mot de passe de l'utilisateur
    et les valide.
    """
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Adresse e-mail',
            'class': 'form-control',
            'id': 'email',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe',
            'class': 'form-control',
            'id': 'password',
        })
    )
