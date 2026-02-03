"""
URL configuration for EduPay_RDC project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views_templates import login_view, home_view

urlpatterns = [
    path('', login_view, name='home'),
    path('admin/', admin.site.urls),
    
    # Template URLs
    path('auth/', include(('core.urls', 'core'), namespace='core_templates')),
    path('dashboard/', include(('dashboard_admin.urls', 'dashboard_admin'), namespace='dashboard_admin_templates')),
    path('etablissement/', include('etablissements.urls_templates')),
    path('etudiant/', include('etudiants.urls_templates')),
    path('frais/', include('frais.urls_templates')),
    path('paiement/', include('paiements.urls_templates')),
    
    # API URLs
    path('api/auth/', include('core.urls')),
    path('api/etablissements/', include('etablissements.urls')),
    path('api/etudiants/', include('etudiants.urls')),
    path('api/frais/', include('frais.urls')),
    path('api/paiements/', include('paiements.urls')),
    path('api/dashboard/', include('dashboard_admin.urls')),
]

# URLs pour les médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
