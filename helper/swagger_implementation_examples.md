# Exemplos de Implementação do Swagger por App

Este documento contém exemplos detalhados de como implementar as tags do Swagger em cada app do projeto.

## Arquivo de Constantes

Primeiro, precisamos criar o arquivo `apps/core/swagger_tags.py` com as constantes:

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

## 1. App Account

### Exemplo para CustomTokenObtainPairView

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

### Exemplo para RegisterView

```python
from core.swagger_tags import API_TAGS

class RegisterView(APIView):
    """View para registro de novos usuários com verificação de email"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Registro de usuário",
        operation_description="Endpoint para registro de novos usuários com verificação de email",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response('Usuário criado com sucesso', UserRegistrationSerializer),
            400: 'Dados inválidos'
        }
    )
    def post(self, request):
        # Implementação existente
```

### Exemplo para LogoutView

```python
from core.swagger_tags import API_TAGS

class LogoutView(APIView):
    """View para logout do usuário"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Logout de usuário",
        operation_description="Endpoint para logout e invalidação do token JWT",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de refresh')
            },
            required=['refresh_token']
        ),
        responses={
            200: 'Logout realizado com sucesso',
            400: 'Token inválido'
        }
    )
    def post(self, request):
        # Implementação existente
```

### Exemplo para UserProfileView (já parcialmente implementado)

```python
from core.swagger_tags import API_TAGS

class UserProfileView(APIView):
    """View para visualizar e atualizar perfil do usuário"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Obter perfil do usuário",
        operation_description="Obter perfil do usuário logado",
        responses={200: UserProfileSerializer}
    )
    def get(self, request):
        # Implementação existente
        
    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Atualizar perfil do usuário",
        operation_description="Atualizar perfil do usuário",
        request_body=UserUpdateSerializer,
        responses={
            200: openapi.Response('Perfil atualizado com sucesso', UserProfileSerializer),
            400: 'Dados inválidos'
        }
    )
    def patch(self, request):
        # Implementação existente
```

### Exemplo para função decorada com api_view

```python
from core.swagger_tags import API_TAGS

@swagger_auto_schema(
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Verificar token",
    operation_description="Endpoint para verificar se um token JWT é válido",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token JWT')
        },
        required=['token']
    ),
    responses={
        200: openapi.Response('Token válido'),
        401: 'Token inválido'
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_token_view(request):
    # Implementação existente
```

## 2. App Projects

### Exemplo para ProjectViewSet

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
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar projeto",
        operation_description="Cria um novo projeto",
        request_body=ProjectCreateUpdateSerializer,
        responses={
            201: ProjectDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar projeto",
        operation_description="Atualiza um projeto existente",
        request_body=ProjectCreateUpdateSerializer,
        responses={
            200: ProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Projeto não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar projeto parcialmente",
        operation_description="Atualiza parcialmente um projeto existente",
        request_body=ProjectCreateUpdateSerializer,
        responses={
            200: ProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Projeto não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir projeto",
        operation_description="Exclui um projeto existente",
        responses={
            204: 'Projeto excluído com sucesso',
            404: 'Projeto não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar fases do projeto",
        operation_description="Retorna uma lista de fases do projeto",
        responses={
            200: PhaseProjectListSerializer(many=True),
            404: 'Projeto não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def phases(self, request, pk=None):
        # Implementação existente
```

### Exemplo para IncorporationViewSet

```python
from core.swagger_tags import API_TAGS

class IncorporationViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de incorporações (empreendimentos)"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar incorporações",
        operation_description="Retorna uma lista paginada de incorporações com filtros",
        responses={200: IncorporationListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Outros métodos seguem o mesmo padrão
```

## 3. App Leads

### Exemplo para LeadViewSet

```python
from core.swagger_tags import API_TAGS

class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento completo de leads"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Listar leads",
        operation_description="Retorna uma lista paginada de leads com filtros",
        responses={200: LeadListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Criar lead",
        operation_description="Cria um novo lead",
        request_body=LeadCreateSerializer,
        responses={
            201: LeadDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    # Outros métodos seguem o mesmo padrão
    
    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Dados para formulário de lead",
        operation_description="Endpoint para obter dados necessários para formulário",
        responses={200: 'Dados para formulário'}
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def form_data(self, request):
        # Implementação existente
```

## 4. App Core

### Exemplo para api_root_view

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
    # Implementação existente
```

### Exemplo para CountyViewSet

```python
from core.swagger_tags import API_TAGS

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet read-only para counties (dados de apoio)"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Listar counties",
        operation_description="Retorna uma lista de counties",
        responses={200: CountyChoiceSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Detalhes do county",
        operation_description="Retorna detalhes de um county específico",
        responses={
            200: CountyChoiceSerializer(),
            404: 'County não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Counties como choices",
        operation_description="Retorna counties como choices para forms",
        responses={200: 'Lista de choices'}
    )
    @action(detail=False, methods=['get'])
    def choices(self, request):
        # Implementação existente
```

## 5. App Financial

### Exemplo para views do app Financial

```python
from core.swagger_tags import API_TAGS

# Exemplo para um ViewSet
class FinancialViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento financeiro"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['FINANCIAL']],
        operation_summary="Listar registros financeiros",
        operation_description="Retorna uma lista paginada de registros financeiros com filtros",
        responses={200: 'Lista de registros financeiros'}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Outros métodos seguem o mesmo padrão
```

## 6. App Purchases

### Exemplo para views do app Purchases

```python
from core.swagger_tags import API_TAGS

# Exemplo para um ViewSet
class PurchaseViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de compras"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['PURCHASES']],
        operation_summary="Listar compras",
        operation_description="Retorna uma lista paginada de compras com filtros",
        responses={200: 'Lista de compras'}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Outros métodos seguem o mesmo padrão
```

## 7. App Client Portal

### Exemplo para views do app Client Portal

```python
from core.swagger_tags import API_TAGS

# Exemplo para um ViewSet
class ClientPortalViewSet(viewsets.ModelViewSet):
    """ViewSet para portal do cliente"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['CLIENT_PORTAL']],
        operation_summary="Listar projetos do cliente",
        operation_description="Retorna uma lista de projetos do cliente",
        responses={200: 'Lista de projetos do cliente'}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Outros métodos seguem o mesmo padrão
```

## 8. App Notifications & Tasks

### Exemplo para views do app Notifications

```python
from core.swagger_tags import API_TAGS

# Exemplo para um ViewSet
class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de notificações"""
    
    @swagger_auto_schema(
        tags=[API_TAGS['NOTIFICATIONS']],
        operation_summary="Listar notificações",
        operation_description="Retorna uma lista paginada de notificações do usuário",
        responses={200: 'Lista de notificações'}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Outros métodos seguem o mesmo padrão
```

## Melhoria na Descrição do Schema View

Atualizar a descrição do `schema_view` no arquivo `erp_lakeshore/urls.py`:

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