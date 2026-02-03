"""
Vue d'accueil pour la plateforme EduPay RDC
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def home(request):
    """
    Vue d'accueil qui affiche les informations de l'API
    """
    return JsonResponse({
        'message': 'Bienvenue sur EduPay RDC - Plateforme de paiement des frais scolaires',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'auth': '/api/auth/',
                'etablissements': '/api/etablissements/',
                'etudiants': '/api/etudiants/',
                'frais': '/api/frais/',
                'paiements': '/api/paiements/',
                'dashboard': '/api/dashboard/',
            },
            'documentation': {
                'readme': 'Voir README.md pour la documentation complète',
                'api_docs': 'Consultez le README.md pour la liste complète des endpoints'
            }
        },
        'status': 'active'
    })





