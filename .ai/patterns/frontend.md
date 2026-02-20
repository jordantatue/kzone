# Pattern : Frontend jQuery

## Principes
- **Aucun** JavaScript inline dans les templates
- Un fichier JS par module dans `static/js/`
- Charger dans `{% block javascript %}` en fin de template
- **CSRF token obligatoire** sur tous les appels AJAX

## Structure d'un Fichier JS

```javascript
// static/js/clients.js

/**
 * Module de gestion des clients
 */
(function($) {
    'use strict';
    
    // Variables globales du module
    const clientsModule = {
        csrfToken: null,
        
        /**
         * Initialisation du module
         */
        init: function() {
            this.csrfToken = $('[name=csrfmiddlewaretoken]').val();
            this.attachEvents();
        },
        
        /**
         * Attache les événements
         */
        attachEvents: function() {
            $('#btn-ajouter-client').on('click', this.ouvrirModal.bind(this));
            $('#form-client').on('submit', this.soumettreFormulaire.bind(this));
            $('.btn-supprimer').on('click', this.supprimerClient.bind(this));
        },
        
        /**
         * Ouvre la modale de création
         */
        ouvrirModal: function(e) {
            e.preventDefault();
            $('#modal-client').modal('show');
        },
        
        /**
         * Soumet le formulaire via AJAX
         */
        soumettreFormulaire: function(e) {
            e.preventDefault();
            
            const formData = $(e.target).serialize();
            
            $.ajax({
                url: '/clients/creer/',
                method: 'POST',
                headers: {'X-CSRFToken': this.csrfToken},
                data: formData,
                success: this.handleSuccess.bind(this),
                error: this.handleError.bind(this)
            });
        },
        
        /**
         * Gère le succès de la requête
         */
        handleSuccess: function(response) {
            // Fermer modal
            $('#modal-client').modal('hide');
            
            // Afficher message
            this.showMessage('success', 'Client créé avec succès');
            
            // Recharger liste
            this.rechargerListe();
        },
        
        /**
         * Gère l'erreur de la requête
         */
        handleError: function(xhr) {
            const errors = xhr.responseJSON?.errors || ['Une erreur est survenue'];
            this.showMessage('error', errors.join(', '));
        },
        
        /**
         * Affiche un message utilisateur
         */
        showMessage: function(type, message) {
            const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
            const html = `
                <div class="alert ${alertClass} alert-dismissible fade show">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            $('#messages-container').html(html);
        },
        
        /**
         * Recharge la liste des clients
         */
        rechargerListe: function() {
            window.location.reload();
        },
        
        /**
         * Supprime un client
         */
        supprimerClient: function(e) {
            e.preventDefault();
            
            const clientId = $(e.currentTarget).data('client-id');
            const clientNom = $(e.currentTarget).data('client-nom');
            
            if (!confirm(`Voulez-vous vraiment supprimer ${clientNom} ?`)) {
                return;
            }
            
            $.ajax({
                url: `/clients/${clientId}/supprimer/`,
                method: 'POST',
                headers: {'X-CSRFToken': this.csrfToken},
                success: function() {
                    $(`#client-${clientId}`).fadeOut(300, function() {
                        $(this).remove();
                    });
                },
                error: this.handleError.bind(this)
            });
        }
    };
    
    // Initialisation au chargement du DOM
    $(document).ready(function() {
        clientsModule.init();
    });
    
})(jQuery);
```

## Template Correspondant

```html
{# templates/clients/liste.html #}
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container">
    <h1>Liste des Clients</h1>
    
    <div id="messages-container"></div>
    
    <button id="btn-ajouter-client" class="btn btn-primary">
        Ajouter un client
    </button>
    
    <table class="table">
        <thead>
            <tr>
                <th>Nom</th>
                <th>Email</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for client in clients %}
            <tr id="client-{{ client.id }}">
                <td>{{ client.nom }}</td>
                <td>{{ client.email }}</td>
                <td>
                    <button 
                        class="btn btn-danger btn-sm btn-supprimer"
                        data-client-id="{{ client.id }}"
                        data-client-nom="{{ client.nom }}">
                        Supprimer
                    </button>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- Modal de création -->
    <div id="modal-client" class="modal fade">
        <div class="modal-dialog">
            <div class="modal-content">
                <form id="form-client">
                    {% csrf_token %}
                    <div class="modal-header">
                        <h5>Nouveau Client</h5>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label>Nom</label>
                            <input type="text" name="nom" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label>Email</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            Annuler
                        </button>
                        <button type="submit" class="btn btn-primary">
                            Créer
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block javascript %}
<script src="{% static 'js/clients.js' %}"></script>
{% endblock %}
```

## AJAX avec CSRF Token

### Méthode 1 : Header (Recommandée)

```javascript
const csrfToken = $('[name=csrfmiddlewaretoken]').val();

$.ajax({
    url: '/api/action/',
    method: 'POST',
    headers: {'X-CSRFToken': csrfToken},
    data: {key: 'value'},
    success: function(response) {
        console.log('Succès', response);
    }
});
```

### Méthode 2 : Dans les données

```javascript
$.ajax({
    url: '/api/action/',
    method: 'POST',
    data: {
        csrfmiddlewaretoken: csrfToken,
        key: 'value'
    }
});
```

### Méthode 3 : Configuration globale

```javascript
// À mettre en début de fichier, une seule fois
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
    }
});
```

## Patterns Communs

### Chargement Asynchrone de Données

```javascript
/**
 * Charge les factures d'un client
 */
chargerFactures: function(clientId) {
    $.ajax({
        url: `/clients/${clientId}/factures/`,
        method: 'GET',
        success: function(response) {
            // response.factures contient la liste
            this.afficherFactures(response.factures);
        }.bind(this),
        error: function() {
            this.showMessage('error', 'Erreur de chargement');
        }.bind(this)
    });
},

/**
 * Affiche les factures dans le DOM
 */
afficherFactures: function(factures) {
    const container = $('#factures-liste');
    container.empty();
    
    factures.forEach(function(facture) {
        const html = `
            <div class="facture-item">
                <span>${facture.numero}</span>
                <span>${facture.montant_ttc}€</span>
            </div>
        `;
        container.append(html);
    });
}
```

### Autocomplétion

```javascript
/**
 * Autocomplétion de recherche client
 */
setupAutocomplete: function() {
    $('#search-client').autocomplete({
        source: function(request, response) {
            $.ajax({
                url: '/clients/recherche/',
                method: 'GET',
                data: {q: request.term},
                success: function(data) {
                    response(data.clients.map(function(client) {
                        return {
                            label: client.nom,
                            value: client.id
                        };
                    }));
                }
            });
        },
        select: function(event, ui) {
            // Client sélectionné
            this.chargerDetailsClient(ui.item.value);
        }.bind(this)
    });
}
```

### Validation Formulaire Côté Client

```javascript
/**
 * Valide le formulaire avant soumission
 */
validerFormulaire: function(formData) {
    const errors = [];
    
    // Validation email
    const email = formData.get('email');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        errors.push('Email invalide');
    }
    
    // Validation téléphone
    const tel = formData.get('telephone');
    const telRegex = /^[0-9]{10}$/;
    if (!telRegex.test(tel)) {
        errors.push('Téléphone doit contenir 10 chiffres');
    }
    
    return errors;
},

/**
 * Soumet avec validation
 */
soumettreAvecValidation: function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const errors = this.validerFormulaire(formData);
    
    if (errors.length > 0) {
        this.showMessage('error', errors.join('<br>'));
        return;
    }
    
    // Soumettre si valide
    $.ajax({
        url: e.target.action,
        method: 'POST',
        headers: {'X-CSRFToken': this.csrfToken},
        data: $(e.target).serialize(),
        success: this.handleSuccess.bind(this)
    });
}
```

### Pagination AJAX

```javascript
/**
 * Charge une page spécifique
 */
chargerPage: function(pageNum) {
    $.ajax({
        url: '/clients/',
        method: 'GET',
        data: {page: pageNum},
        success: function(response) {
            $('#clients-liste').html(response.html);
            this.updatePagination(response.pagination);
        }.bind(this)
    });
},

/**
 * Met à jour les liens de pagination
 */
updatePagination: function(pagination) {
    $('.pagination').html(`
        ${pagination.has_previous ? `<a href="#" data-page="${pagination.previous_page}">Précédent</a>` : ''}
        <span>Page ${pagination.current_page} sur ${pagination.num_pages}</span>
        ${pagination.has_next ? `<a href="#" data-page="${pagination.next_page}">Suivant</a>` : ''}
    `);
    
    // Attacher événements
    $('.pagination a').on('click', function(e) {
        e.preventDefault();
        this.chargerPage($(e.target).data('page'));
    }.bind(this));
}
```

## Vue Django pour AJAX

```python
# apps/clients/views.py
from django.http import JsonResponse
from django.views import View
from .models import Client
from .services import ClientService

class ClientRechercheView(View):
    """API de recherche de clients."""
    
    def get(self, request):
        query = request.GET.get('q', '')
        
        clients = Client.objects.filter(
            nom__icontains=query
        )[:10]
        
        return JsonResponse({
            'clients': [
                {'id': c.id, 'nom': c.nom, 'email': c.email}
                for c in clients
            ]
        })


class ClientCreerAPIView(View):
    """API de création de client."""
    
    def post(self, request):
        try:
            client = ClientService.creer_client(
                nom=request.POST.get('nom'),
                email=request.POST.get('email')
            )
            
            return JsonResponse({
                'success': True,
                'client': {
                    'id': client.id,
                    'nom': client.nom
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'errors': e.messages
            }, status=400)
```

## Règles Importantes

### 1. Nommage camelCase en JavaScript
```javascript
// ✅ BON
const clientsModule = {};
function chargerFactures() {}

// ❌ MAUVAIS (snake_case en JS)
const clients_module = {};
function charger_factures() {}
```

### 2. Toujours bind(this)
```javascript
// ✅ BON
$('#btn').on('click', this.maMethode.bind(this));

// ❌ MAUVAIS (perd le contexte)
$('#btn').on('click', this.maMethode);
```

### 3. Gestion d'erreurs systématique
```javascript
// ✅ BON
$.ajax({
    success: this.handleSuccess.bind(this),
    error: this.handleError.bind(this)
});

// ❌ MAUVAIS (pas de gestion d'erreur)
$.ajax({
    success: function(data) { ... }
});
```

### 4. Pas de JS inline
```html
<!-- ❌ MAUVAIS -->
<button onclick="deleteClient()">Supprimer</button>

<!-- ✅ BON -->
<button class="btn-supprimer" data-client-id="123">Supprimer</button>
```

## Anti-Patterns à Éviter

❌ JS inline dans templates
❌ AJAX sans CSRF token
❌ Pas de gestion d'erreurs
❌ Variables globales non organisées
❌ snake_case en JavaScript
❌ Pas de feedback utilisateur après action
