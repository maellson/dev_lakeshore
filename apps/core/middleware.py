# apps/core/middleware.py

from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class TrailingSlashMiddleware(MiddlewareMixin):
    """
    Middleware customizado para lidar com trailing slashes de forma mais elegante
    """

    def process_request(self, request):
        # Não processar arquivos estáticos
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None

        # Se APPEND_SLASH está ativo e o path não tem barra final
        if getattr(settings, 'APPEND_SLASH', True) and not request.path.endswith('/'):
            # Excluir alguns paths que não devem ter barra final
            exclude_paths = ['/api', '/health', '/favicon.ico',
                             '/robots.txt', '/swagger.json', '/swagger.yaml']

            # Se o path não está na lista de exclusão
            if not any(request.path.startswith(path) for path in exclude_paths):
                # Adicionar barra final e redirecionar
                return HttpResponsePermanentRedirect(request.path + '/')

        return None


class FriendlyErrorMiddleware(MiddlewareMixin):
    """
    Middleware para tornar erros mais amigáveis
    """

    def process_response(self, request, response):
        # Se é um erro 404 e não tem template customizado
        if response.status_code == 404 and not settings.DEBUG:
            # Log do erro para monitoramento
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f'404 Error: {request.path} - User: {request.user} - IP: {request.META.get("REMOTE_ADDR")}')

        return response


class DisableCSRFForAPIMiddleware:
    """Desabilita CSRF para endpoints de API"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # DEBUG: Log para verificar se a lógica está correta
        print(f"🔍 Request path: {request.path}")

        if (request.path.startswith('/api/') and
                not request.path.startswith('/api/auth/admin/')):
            print(f"✅ Desabilitando CSRF para: {request.path}")
            setattr(request, '_dont_enforce_csrf_checks', True)
        else:
            print(f"❌ MANTENDO CSRF para: {request.path}")

        response = self.get_response(request)
        return response
