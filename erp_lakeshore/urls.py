# erp_lakeshore/urls.py
"""
URL configuration for erp_lakeshore project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Classe de permissão personalizada para o Swagger que aceita JWT e Session Auth


class SwaggerPermission(permissions.BasePermission):
    """
    Permissão personalizada para o Swagger.
    Permite acesso à documentação para usuários autenticados apenas via JWT.
    """

    def has_permission(self, request, view):

        # Verificar autenticação por sessão
        if request.user and request.user.is_authenticated:
            return True  # TOFIX: remover caso não seja necessário

        # Verificar autenticação por JWT
        jwt_auth = JWTAuthentication()
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                return user and user.is_authenticated
        except Exception:
            pass

        return False


# Configuração do Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="ERP Lakeshore API",
        default_version='v1',
        description="""
        # Sistema ERP Lakeshore
        
        API para o sistema ERP da Lakeshore Development, uma plataforma completa para gestão de projetos imobiliários e construção civil.
        
        ## Autenticação
        
        Esta API utiliza autenticação JWT. Para acessar endpoints protegidos:
        
        1. Faça login em `/api/auth/login/` para obter seu token
        2. Use o botão "Authorize" abaixo e insira: `Bearer seu_token_aqui`
        3. Agora você pode testar todos os endpoints protegidos
        
        ## Navegação por Tags
        
        A documentação está organizada por tags para facilitar a navegação:
        
        - **👥 Account & Users**: Autenticação, gerenciamento de usuários e perfis
        - **🏗️ Projects & Construction**: Gerenciamento de projetos e contratos
        - **💰 Financial Management**: Controle financeiro e orçamentário
        - **🛒 Purchases & Suppliers**: Gestão de compras e fornecedores
        - **🎯 Leads & Sales**: Gestão de leads e vendas
        - **📋 Client Portal**: Portal para clientes acompanharem projetos
        - **🔔 Notifications & Tasks**: Sistema de notificações e tarefas
        - **⚙️ Core & Settings**: Configurações e funcionalidades do core
        
        ## Como Usar a Documentação
        
        1. Use o menu de tags à direita para filtrar endpoints por categoria
        2. Expanda um endpoint para ver detalhes, parâmetros e exemplos
        3. Clique em "Try it out" para testar o endpoint diretamente na documentação
        4. Verifique os modelos de dados na seção "Schemas" ao final da página
        """,
        terms_of_service="https://www.lakeshoredevelopmentfl.com/terms/",
        contact=openapi.Contact(email="mmarques@lakeshoredevelopmentfl.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,  # ← Requer autenticação falte se privado
    # Para tornar publico ative esta linha e comente as duas próximas
    permission_classes=(permissions.AllowAny,),
    # permission_classes=(SwaggerPermission,),
    # authentication_classes=(SessionAuthentication,JWTAuthentication),  # dupla authenticação, comente para deixar publica e apenas jwt

   
)


def health_check(request):
    """View de health check"""
    return HttpResponse('ERP Lakeshore - Sistema Online 👾')


def root_view(request):
    """View da página inicial"""
    return HttpResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ERP Lakeshore</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; max-width: 800px; }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            a { color: #007bff; text-decoration: none; display: block; margin: 10px 0; }
            a:hover { text-decoration: underline; }
            .download-section { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .code { background: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🏗️ ERP Lakeshore</h1>
        <p>Sistema de Gestão para Construção Civil</p>
        
        <h2>📋 Admin & Documentation</h2>
        <a href="/admin/">Admin Django</a>
        <a href="/swagger/">API Documentation (Swagger)</a>
        <a href="/redoc/">API Documentation (ReDoc)</a>
        
        <div class="download-section">
            <h2>📥 Schema Downloads (Para Frontend)</h2>
            <p>Links diretos para download do schema da API:</p>
            <a href="/swagger.json" target="_blank">📄 Schema JSON (OpenAPI 3.0)</a>
            <a href="/swagger.yaml" target="_blank">📄 Schema YAML (OpenAPI 3.0)</a>
            <a href="/api/schema-info/" target="_blank">ℹ️ Informações dos Schemas</a>
            
            <p><strong>Comando para automação:</strong></p>
            <div class="code">curl -X GET 'https://api.lakeshoredevelopmentfl.com/swagger.json' -o api-schema.json</div>
        </div>
        
        <h2>🧪 API Test</h2>
        <a href="/api/auth/choices/">API Test</a>
        <a href="/health/">Health Check</a>
    </body>
    </html>
    ''')


urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),

    # Swagger/OpenAPI documentation
    # A solução simples que deveria ter dado desde o início:
    re_path(r'^swagger\.json/?$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger\.yaml/?$',
            schema_view.without_ui(cache_timeout=0), name='schema-yaml'),


    # Documentação UI
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),

    # APIs
    path('api/auth/', include('account.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/financial/', include('financial.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/client-portal/', include('client_portal.urls')),
    path('api/leads/', include('leads.urls')),
    path('integrations/', include('integrations.urls')),
    # path('api/core/', include('core.urls')),

    # Health check - CORRIGIDO 2
    path('health/', health_check, name='health'),

    # webhooks
    # path('webhooks/', include('integrations.urls')),  # Integrations URLs


]

# Servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

# Handlers de erro customizados
handler404 = 'erp_lakeshore.views.custom_404'
handler500 = 'erp_lakeshore.views.custom_500'
handler403 = 'erp_lakeshore.views.custom_403'
handler400 = 'erp_lakeshore.views.custom_400'
