from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import County, Realtor, HOA
from django.conf import settings
from .serializers import (
    CountyChoiceSerializer,
    RealtorListSerializer,
    RealtorDetailSerializer,
    RealtorCreateUpdateSerializer,
    RealtorChoiceSerializer,
    HOAListSerializer,
    HOADetailSerializer,
    HOACreateUpdateSerializer,
    HOAChoiceSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .swagger_tags import API_TAGS


@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['CORE']],
    operation_summary="API Root",
    operation_description="Lista todos os endpoints disponíveis na API",
    responses={200: 'Lista de endpoints disponíveis'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    """
    API Root - Lista todos os endpoints disponíveis
    """

    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash

    endpoints = {
        "message": "🏗️ ERP Lakeshore Construction - API v1.0",
        "status": "✅ Sistema Funcionando",
        "documentation": {
            "swagger": f"{base_url}/api/swagger/",
            "redoc": f"{base_url}/api/redoc/",
            "admin": f"{base_url}/admin/",
        },

        "endpoints": {
            "authentication": {
                "login": {
                    "url": f"{base_url}/api/auth/login/",
                    "method": "POST",
                    "description": "Fazer login e obter tokens JWT",
                    "data": {
                        "email": "seu@email.com",
                        "password": "sua_senha"
                    }
                },
                "register": {
                    "url": f"{base_url}/api/auth/register/",
                    "method": "POST",
                    "description": "Registrar novo usuário"
                },
                "profile": {
                    "url": f"{base_url}/api/auth/profile/",
                    "method": "GET",
                    "description": "Ver perfil do usuário logado",
                    "requires": "Bearer Token"
                },
                "logout": {
                    "url": f"{base_url}/api/auth/logout/",
                    "method": "POST",
                    "description": "Fazer logout e invalidar token",
                    "requires": "Bearer Token"
                }
            },

            "admin": {
                "users": {
                    "url": f"{base_url}/api/auth/admin/users/",
                    "method": "GET",
                    "description": "Listar usuários (Admin apenas)",
                    "requires": "Admin Level 4+"
                },
                "hierarchy": {
                    "url": f"{base_url}/api/auth/admin/hierarchy/",
                    "method": "GET",
                    "description": "Dashboard hierárquico",
                    "requires": "Admin Level 4+"
                }
            },

            "password_reset": {
                "request": {
                    "url": f"{base_url}/api/auth/password-reset/",
                    "method": "POST",
                    "description": "Solicitar reset de senha"
                },
                "confirm": {
                    "url": f"{base_url}/api/auth/password-reset/confirm/",
                    "method": "POST",
                    "description": "Confirmar reset com token"
                }
            }
        },

        "tips": {
            "1": "Para APIs protegidas, use: Authorization: Bearer <seu_token>",
            "2": "Faça login primeiro para obter o token de acesso",
            "3": "Use POST para login, não GET",
            "4": "Admin interface: /admin/",
            "5": "Documentação completa da API: /api/swagger/ ou /api/redoc/"
        },

        "system_info": {
            "version": "1.0.0",
            "environment": "production" if not settings.DEBUG else "development"
        }
    }

    return Response(endpoints)


@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['CORE']],
    operation_summary="Endpoints de autenticação",
    operation_description="Lista específica de endpoints de autenticação",
    responses={200: 'Lista de endpoints de autenticação'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def auth_endpoints_view(request):
    """
    Lista específica de endpoints de autenticação
    """

    base_url = request.build_absolute_uri('/')[:-1]

    auth_info = {
        "message": "🔐 ERP Lakeshore - Authentication Endpoints",

        "public_endpoints": {
            "login": {
                "url": f"{base_url}/api/auth/login/",
                "method": "POST",
                "example": {
                    "email": "usuario@example.com",
                    "password": "senha123"
                }
            },
            "register": {
                "url": f"{base_url}/api/auth/register/",
                "method": "POST",
                "example": {
                    "email": "novo@example.com",
                    "username": "novo_usuario",
                    "first_name": "Nome",
                    "last_name": "Sobrenome",
                    "tipo_usuario": "INTERNO",
                    "password": "senha123",
                    "password_confirm": "senha123"
                }
            },
            "password_reset": {
                "url": f"{base_url}/api/auth/password-reset/",
                "method": "POST",
                "example": {
                    "email": "usuario@example.com"
                }
            }
        },

        "protected_endpoints": {
            "note": "Requerem Authorization: Bearer <token>",
            "profile": f"{base_url}/api/auth/profile/",
            "permissions": f"{base_url}/api/auth/permissions/",
            "logout": f"{base_url}/api/auth/logout/"
        },

        "admin_endpoints": {
            "note": "Requerem nível de acesso 4+ (Diretoria/Admin)",
            "users": f"{base_url}/api/auth/admin/users/",
            "hierarchy": f"{base_url}/api/auth/admin/hierarchy/",
            "permissions": f"{base_url}/api/auth/admin/permissions/"
        },

        "how_to_use": {
            "step_1": f"POST {base_url}/api/auth/login/ com email/senha",
            "step_2": "Copiar o 'access' token da resposta",
            "step_3": "Usar em outras APIs: Authorization: Bearer <token>",
            "step_4": "Para admin: garantir que usuário tem nível 4+"
        }
    }

    return Response(auth_info)


@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['CORE']],
    operation_summary="Health Check",
    operation_description="Verifica se a API está funcionando",
    responses={200: 'Status da API'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({'status': 'ok'})


class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet read-only para counties (dados de apoio)"""

    queryset = County.get_florida_counties()
    serializer_class = CountyChoiceSerializer
    permission_classes = [AllowAny]  # Público para formulários
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Listar counties",
        operation_description="Retorna uma lista de counties (condados) da Flórida",
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
        operation_description="Retorna counties formatados como choices para formulários",
        responses={200: 'Lista de counties como choices'}
    )
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Retorna counties como choices para forms"""
        counties = self.get_queryset()
        choices = [{'value': county.id, 'label': county.name}
                   for county in counties]
        return Response({'counties': choices})


class RealtorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de realtors
    
    ENDPOINTS:
    - GET /api/core/realtors/ - Lista realtors com filtros
    - POST /api/core/realtors/ - Criar novo realtor
    - GET /api/core/realtors/{id}/ - Detalhes de realtor
    - PATCH /api/core/realtors/{id}/ - Atualizar realtor
    - DELETE /api/core/realtors/{id}/ - Remover realtor
    - GET /api/core/realtors/active/ - Listar apenas realtors ativos
    - GET /api/core/realtors/choices/ - Realtors formatados como choices
    """
    
    queryset = Realtor.objects.select_related().prefetch_related('usually_works_in').all()
    serializer_class = RealtorListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros disponíveis
    filterset_fields = {
        'is_active': ['exact'],
        'usually_works_in': ['exact', 'in'],
        'default_commission_rate': ['gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }
    
    # Campos de busca
    search_fields = ['name', 'email', 'phone']
    
    # Ordenação
    ordering_fields = ['name', 'email', 'default_commission_rate', 'created_at']
    ordering = ['name']  # Default: ordem alfabética
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return RealtorDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RealtorCreateUpdateSerializer
        elif self.action == 'choices':
            return RealtorChoiceSerializer
        return self.serializer_class
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Listar realtors",
        operation_description="Retorna uma lista paginada de realtors com filtros",
        responses={200: RealtorListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Detalhes do realtor",
        operation_description="Retorna detalhes completos de um realtor específico",
        responses={
            200: RealtorDetailSerializer(),
            404: 'Realtor não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Criar realtor",
        operation_description="Cria um novo realtor",
        request_body=RealtorCreateUpdateSerializer,
        responses={
            201: RealtorDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Atualizar realtor",
        operation_description="Atualiza um realtor existente",
        request_body=RealtorCreateUpdateSerializer,
        responses={
            200: RealtorDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Realtor não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Atualizar realtor parcialmente",
        operation_description="Atualiza parcialmente um realtor existente",
        request_body=RealtorCreateUpdateSerializer,
        responses={
            200: RealtorDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Realtor não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Excluir realtor",
        operation_description="Exclui um realtor existente",
        responses={
            204: 'Realtor excluído com sucesso',
            404: 'Realtor não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Realtors ativos",
        operation_description="Retorna apenas realtors ativos",
        responses={200: RealtorListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retorna apenas realtors ativos"""
        active_realtors = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_realtors, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Realtors como choices",
        operation_description="Retorna realtors formatados como choices para formulários",
        responses={200: 'Lista de realtors como choices'}
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def choices(self, request):
        """Retorna realtors como choices para forms"""
        realtors = Realtor.get_active()
        choices = [
            {
                'value': realtor.id,
                'label': realtor.name,
                'email': realtor.email,
                'phone': str(realtor.phone)
            }
            for realtor in realtors
        ]
        return Response({'realtors': choices})


class HOAViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de HOAs (Homeowners Associations)
    
    ENDPOINTS:
    - GET /api/core/hoas/ - Lista HOAs com filtros
    - POST /api/core/hoas/ - Criar novo HOA
    - GET /api/core/hoas/{id}/ - Detalhes de HOA
    - PATCH /api/core/hoas/{id}/ - Atualizar HOA
    - DELETE /api/core/hoas/{id}/ - Remover HOA
    - GET /api/core/hoas/active/ - Listar apenas HOAs ativos
    - GET /api/core/hoas/choices/ - HOAs formatados como choices
    - GET /api/core/hoas/by-county/{county_id}/ - HOAs por county
    """
    
    queryset = HOA.objects.select_related('county').all()
    serializer_class = HOAListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros disponíveis
    filterset_fields = {
        'is_active': ['exact'],
        'county': ['exact', 'in'],
        'has_special_permit_rules': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }
    
    # Campos de busca
    search_fields = ['name', 'permit_requirements', 'contact_info']
    
    # Ordenação
    ordering_fields = ['name', 'county__name', 'created_at']
    ordering = ['name']  # Default: ordem alfabética
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return HOADetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HOACreateUpdateSerializer
        elif self.action == 'choices':
            return HOAChoiceSerializer
        return self.serializer_class
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Listar HOAs",
        operation_description="Retorna uma lista paginada de HOAs com filtros",
        responses={200: HOAListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Detalhes do HOA",
        operation_description="Retorna detalhes completos de um HOA específico",
        responses={
            200: HOADetailSerializer(),
            404: 'HOA não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Criar HOA",
        operation_description="Cria um novo HOA",
        request_body=HOACreateUpdateSerializer,
        responses={
            201: HOADetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Atualizar HOA",
        operation_description="Atualiza um HOA existente",
        request_body=HOACreateUpdateSerializer,
        responses={
            200: HOADetailSerializer(),
            400: 'Dados inválidos',
            404: 'HOA não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Atualizar HOA parcialmente",
        operation_description="Atualiza parcialmente um HOA existente",
        request_body=HOACreateUpdateSerializer,
        responses={
            200: HOADetailSerializer(),
            400: 'Dados inválidos',
            404: 'HOA não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="Excluir HOA",
        operation_description="Exclui um HOA existente",
        responses={
            204: 'HOA excluído com sucesso',
            404: 'HOA não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="HOAs ativos",
        operation_description="Retorna apenas HOAs ativos",
        responses={200: HOAListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retorna apenas HOAs ativos"""
        active_hoas = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_hoas, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="HOAs como choices",
        operation_description="Retorna HOAs formatados como choices para formulários",
        responses={200: 'Lista de HOAs como choices'}
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def choices(self, request):
        """Retorna HOAs como choices para forms"""
        hoas = self.get_queryset().filter(is_active=True).order_by('name')
        choices = [
            {
                'value': hoa.id,
                'label': hoa.name,
                'county': hoa.county.name,
                'county_id': hoa.county.id,
                'has_special_rules': hoa.has_special_permit_rules
            }
            for hoa in hoas
        ]
        return Response({'hoas': choices})
    
    @swagger_auto_schema(
        tags=[API_TAGS['CORE']],
        operation_summary="HOAs por county",
        operation_description="Retorna HOAs de um county específico",
        responses={200: HOAListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-county/(?P<county_id>[^/.]+)')
    def by_county(self, request, county_id=None):
        """Retorna HOAs de um county específico"""
        hoas = self.get_queryset().filter(county_id=county_id, is_active=True)
        serializer = self.get_serializer(hoas, many=True)
        return Response(serializer.data)
    


# configuracao de rota especifica para listar todos os endpoints de schema
@api_view(['GET'])
@permission_classes([AllowAny])
def api_schema_info(request):
    """
    Endpoint que lista todos os formatos de schema disponíveis para download
    """
    base_url = request.build_absolute_uri('/')[:-1]
    
    return Response({
        "message": "📋 ERP Lakeshore - API Schema Downloads",
        "schema_downloads": {
            "json": {
                "url": f"{base_url}/swagger.json",
                "description": "OpenAPI 3.0 Schema em formato JSON",
                "content_type": "application/json",
                "usage": "Ideal para ferramentas de geração de código"
            },
            "yaml": {
                "url": f"{base_url}/swagger.yaml", 
                "description": "OpenAPI 3.0 Schema em formato YAML",
                "content_type": "application/yaml",
                "usage": "Ideal para leitura humana e documentação"
            }
        },
        "documentation_links": {
            "swagger_ui": f"{base_url}/swagger/",
            "redoc": f"{base_url}/redoc/",
        },
        "frontend_integration": {
            "note": "Use os URLs acima para manter seu frontend atualizado",
            "example": "curl -X GET '{base_url}/swagger.json' -H 'Accept: application/json'",
            "automation": "Adicione estes URLs em seu pipeline de CI/CD para sincronização automática"
        }
    })
