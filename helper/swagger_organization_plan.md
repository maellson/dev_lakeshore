# Plano de Organização do Swagger/ReDoc

## Objetivo
Organizar o Swagger/ReDoc por seções usando tags do DRF-YASG para melhorar a navegação e usabilidade da documentação da API.

## Estrutura de Tags

Vamos criar constantes para as tags consistentes em um arquivo `apps/core/swagger_tags.py`:

```python
"""
Constantes para organização do Swagger/ReDoc por tags.
"""

# Tags para agrupamento de endpoints
API_TAGS = {
    'ACCOUNT': '👥 Account & Users',
    'PROJECTS': '🏗️ Projects & Construction',
    'FINANCIAL': '💰 Financial Management',
    'PURCHASES': '🛒 Purchases & Suppliers',
    'CLIENT_PORTAL': '📋 Client Portal',
    'NOTIFICATIONS': '🔔 Notifications & Tasks',
    'LEADS': '🎯 Leads & Sales',
    'CORE': '⚙️ Core & Settings',
}
```

## Implementação por App

### 1. Account App (Parcialmente Implementado)

Já existe uma implementação parcial na view `UserProfileView`. Precisamos estender para todas as views:

```python
from core.swagger_tags import API_TAGS

class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para obter token JWT"""
    serializer_class = CustomTokenObtainPairSerializer
    
    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Login de usuário",
        operation_description="Endpoint para autenticação de usuários e obtenção de tokens JWT",
        responses={
            200: openapi.Response('Login bem-sucedido', CustomTokenObtainPairSerializer),
            401: 'Credenciais inválidas'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
```

Aplicar o mesmo padrão para todas as views em `apps/account/views.py`.

### 2. Projects App

Já existe um atributo `swagger_tags = ['🏗️ Projects & Construction']` na classe `ProjectViewSet`, mas precisamos:

1. Substituir pelo uso da constante `API_TAGS['PROJECTS']`
2. Adicionar decoradores `@swagger_auto_schema` em todos os métodos

```python
from core.swagger_tags import API_TAGS

class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de projetos"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar projetos",
        operation_description="Retorna uma lista paginada de projetos com filtros",
        responses={200: ProjectListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes do projeto",
        operation_description="Retorna detalhes completos de um projeto específico",
        responses={
            200: ProjectDetailSerializer(),
            404: 'Projeto não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

Aplicar o mesmo padrão para todas as views em `apps/projects/views.py`.

### 3. Leads App

Implementar tags para todas as views em `apps/leads/views.py`:

```python
from core.swagger_tags import API_TAGS

class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de leads"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Listar leads",
        operation_description="Retorna uma lista paginada de leads com filtros",
        responses={200: LeadListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

### 4. Core App

Implementar tags para todas as views em `apps/core/views.py`:

```python
from core.swagger_tags import API_TAGS

@swagger_auto_schema(
    tags=[API_TAGS['CORE']],
    operation_summary="API Root",
    operation_description="Lista todos os endpoints disponíveis na API"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    """API Root - Lista todos os endpoints disponíveis"""
    # ...
```

### 5. Financial App

Implementar tags para todas as views em `apps/financial/views.py`.

### 6. Purchases App

Implementar tags para todas as views em `apps/purchases/views.py`.

### 7. Client Portal App

Implementar tags para todas as views em `apps/client_portal/views.py`.

### 8. Notifications & Tasks App

Implementar tags para todas as views em `apps/notifications/views.py` e `apps/tasks/views.py`.

## Melhoria na Descrição do Schema View

Atualizar a descrição do `schema_view` no arquivo `erp_lakeshore/urls.py` para incluir seções organizadas:

```python
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
        
        ## Módulos do Sistema
        
        - **👥 Account & Users**: Autenticação, usuários e perfis
        - **🏗️ Projects & Construction**: Gerenciamento de projetos, incorporações e cronogramas
        - **💰 Financial Management**: Controle financeiro, orçamentos e pagamentos
        - **🛒 Purchases & Suppliers**: Gestão de fornecedores e compras
        - **📋 Client Portal**: Portal para clientes acompanharem projetos
        - **🔔 Notifications & Tasks**: Sistema de notificações e tarefas
        - **🎯 Leads & Sales**: Gestão de leads e vendas
        - **⚙️ Core & Settings**: Configurações e funcionalidades centrais
        """,
        terms_of_service="https://www.lakeshoredevelopmentfl.com/terms/",
        contact=openapi.Contact(email="mmarques@lakeshoredevelopmentfl.com"),
        license=openapi.License(name="Proprietary"),
    ),
    # ...
)
```

## Próximos Passos

1. Criar o arquivo de constantes `apps/core/swagger_tags.py`
2. Implementar as tags em cada app, começando pelos que já têm implementação parcial
3. Atualizar a descrição do schema_view
4. Testar a documentação no Swagger e ReDoc para verificar a organização