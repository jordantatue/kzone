"""URLs de l'application profil."""

from django.urls import path

from .views import ProfilDashboardView

app_name = "profil"

urlpatterns = [
    path("", ProfilDashboardView.as_view(), name="dashboard"),
]

