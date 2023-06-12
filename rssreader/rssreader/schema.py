from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class KnoxTokenSpectacularAuthExtension(OpenApiAuthenticationExtension):
    target_class = 'knox.auth.TokenAuthentication'
    name = 'Bearer Token Authentication'
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        knox_settings = getattr(settings, 'REST_KNOX', {})
        prefix = knox_settings.get('AUTH_HEADER_PREFIX', 'Token')
        
        description = f'Token-based authentication with required prefix "{prefix}"'
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'header_name': 'Authorization',
            'token_prefix': prefix,
            'description': description,
        }