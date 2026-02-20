from django.urls import path
from . import views

app_name = 'acceuil'

urlpatterns = [
    path('', views.AccueilView.as_view(), name='accueil'),
    path('catalogue/filtrer/', views.CatalogueFiltreAjaxView.as_view(), name='catalogue_filtrer'),
    path('catalogue/annonce/<int:produit_id>/', views.DetailAnnonceView.as_view(), name='annonce_detail'),
    path(
        'catalogue/annonce/<int:produit_id>/action/',
        views.AnnonceActionAjaxView.as_view(),
        name='annonce_action_ajax',
    ),
    path(
        'catalogue/annonce/<int:produit_id>/contacter/',
        views.ContactVendeurRedirectView.as_view(),
        name='annonce_contacter',
    ),
]
