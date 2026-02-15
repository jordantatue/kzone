from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

class AuthenticationService:
    """
    Service pour gérer la logique d'authentification des utilisateurs.
    """
    
    @staticmethod
    def authenticate_user(request, email, password):
        """
        Authentifie un utilisateur et le connecte.

        Args:
            request: L'objet HttpRequest.
            email: L'email de l'utilisateur.
            password: Le mot de passe de l'utilisateur.

        Returns:
            bool: True si l'authentification réussit, False sinon.
        """
        # Django's authenticate function uses 'username', not 'email'.
        # We need to fetch the user by email first.
        try:
            user = User.objects.get(email=email)
            # Now we can authenticate with the username
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return True
        except User.DoesNotExist:
            # User with this email does not exist
            return False
        
        return False
