from django.urls import path
from . import views

app_name = 'acceuil'

urlpatterns = [
    path('', views.AccueilView.as_view(), name='accueil'),
    path('catalogue/filtrer/', views.CatalogueFiltreAjaxView.as_view(), name='catalogue_filtrer'),
]
