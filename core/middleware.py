"""
Middleware pour forcer HTTP en développement et éviter les erreurs HTTPS
"""
class ForceHTTPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Forcer HTTP en développement
        if request.is_secure():
            # Rediriger vers HTTP si c'est une requête HTTPS
            from django.http import HttpResponsePermanentRedirect
            http_url = request.build_absolute_uri().replace('https://', 'http://')
            return HttpResponsePermanentRedirect(http_url)
        
        response = self.get_response(request)
        return response
