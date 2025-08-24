# apps/leads/views.py
import csv
import io
from django.forms import ValidationError
import xlsxwriter
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
from core.models import County, Realtor, HOA
from core.pagination import CustomPageNumberPagination
from projects.models.choice_types import PaymentMethod
from projects.models import Incorporation
from projects.models.model_project import ModelProject
from leads.models.lead_types import ElevationChoice
from .models import Lead
from .serializers import (
    LeadListSerializer,
    LeadDetailSerializer,
    LeadCreateSerializer,
    LeadUpdateSerializer,
    LeadConversionSerializer,
    CountyChoiceSerializer
)
from .constants import ConversionStatus
from .services import LeadConversionService, LeadProcessingService
from .constants import VALID_MANAGEMENT_COMPANIES

from core.swagger_tags import API_TAGS


def get_status_ids_by_codes(codes):
    """Helper function to get StatusChoice IDs by codes"""
    from leads.models.lead_types import StatusChoice
    if isinstance(codes, str):
        codes = [codes]
    return list(StatusChoice.objects.filter(code__in=codes, is_active=True).values_list('id', flat=True))


def get_status_id_by_code(code):
    """Helper function to get single StatusChoice ID by code"""
    ids = get_status_ids_by_codes([code])
    return ids[0] if ids else None
# apps/leads/views.py

# apps/leads/views.py


class HasLeadConversionPermission(permissions.BasePermission):
    """
    Permissão customizada para conversão de leads

    Verifica se o usuário tem permissão para converter leads em contratos.
    Requer permissão específica 'leads.convert_lead' ou ser staff.
    """

    def has_permission(self, request, view):
        # Staff sempre pode converter
        if request.user.is_staff:
            return True

        # Verificar permissão específica
        return request.user.has_perm('leads.convert_lead')

    def has_object_permission(self, request, view, obj):
        # Verificar se o lead pode ser convertido
        if not obj.is_convertible:
            return False

        # Staff sempre pode converter
        if request.user.is_staff:
            return True

        # Verificar permissão específica
        return request.user.has_perm('leads.convert_lead')


class LeadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento completo de leads

    ENDPOINTS:
    - GET /api/leads/ - Lista leads com filtros
    - POST /api/leads/ - Criar novo lead (público)
    - GET /api/leads/{id}/ - Detalhes de lead
    - PATCH /api/leads/{id}/ - Atualizar lead
    - DELETE /api/leads/{id}/ - Remover lead
    - POST /api/leads/{id}/convert/ - Converter para contrato
    - GET /api/leads/form-data/ - Dados para formulário
    """

    queryset = Lead.objects.select_related('county', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination

    # Filtros disponíveis
    filterset_fields = {
        'status': ['exact', 'in'],
        'county': ['exact'],
        'house_model': ['exact'],
        'elevation': ['exact'],
        'has_hoa': ['exact'],
        'is_realtor': ['exact'],
        'contract_value': ['gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'client_full_name',
        'client_company_name',
        'client_email',
        'client_phone',
        'parcel_id',
    ]

    # Ordenação
    ordering_fields = [
        'created_at',
        'updated_at',
        'contract_value',
        'client_full_name',
        'status',
    ]
    ordering = ['-created_at']  # Default: mais recentes primeiro

    def get_permissions(self):
        """
        Permissões por ação:
        - create: Público (formulário web)
        - form-data: Público (dados para formulário)
        - Outras: Autenticado
        """
        if self.action in ['create', 'form_data']:
            return [AllowAny()]
        return [IsAuthenticated()]

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
        operation_summary="Detalhes do lead",
        operation_description="Retorna detalhes completos de um lead específico",
        responses={
            200: LeadDetailSerializer(),
            404: 'Lead não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Criar lead",
        operation_description="Cria um novo lead (formulário público)",
        request_body=LeadCreateSerializer,
        responses={
            201: LeadDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Atualizar lead",
        operation_description="Atualiza um lead existente",
        request_body=LeadUpdateSerializer,
        responses={
            200: LeadDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Lead não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Atualizar lead parcialmente",
        operation_description="Atualiza parcialmente um lead existente",
        request_body=LeadUpdateSerializer,
        responses={
            200: LeadDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Lead não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Excluir lead",
        operation_description="Exclui um lead existente",
        responses={
            204: 'Lead excluído com sucesso',
            400: 'Lead não pode ser excluído',
            404: 'Lead não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Serializer por ação"""
        if self.action == 'list':
            return LeadListSerializer
        elif self.action == 'create':
            return LeadCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LeadUpdateSerializer
        elif self.action == 'convert':
            return LeadConversionSerializer
        else:
            return LeadDetailSerializer

    def get_queryset(self):
        """Filtros customizados na queryset"""
        queryset = super().get_queryset()

        # Importar aqui para evitar circular imports
        from django.utils import timezone
        from datetime import timedelta

        # Filtro por convertible
        convertible = self.request.query_params.get('convertible')
        if convertible == 'true':
            convertible_ids = get_status_ids_by_codes(['PENDING', 'QUALIFIED'])
            queryset = queryset.filter(status__in=convertible_ids)
        elif convertible == 'false':
            convertible_ids = get_status_ids_by_codes(['PENDING', 'QUALIFIED'])
            queryset = queryset.exclude(status__in=convertible_ids)

        # Filtro por age (days)
        age_gte = self.request.query_params.get('age_gte')
        age_lte = self.request.query_params.get('age_lte')

        if age_gte:
            date_threshold = timezone.now() - timedelta(days=int(age_gte))
            queryset = queryset.filter(created_at__lte=date_threshold)

        if age_lte:
            date_threshold = timezone.now() - timedelta(days=int(age_lte))
            queryset = queryset.filter(created_at__gte=date_threshold)

        # NOVO: Filtro por período predefinido
        period = self.request.query_params.get('period')
        if period:
            today = timezone.now().date()

            if period == 'today':
                queryset = queryset.filter(created_at__date=today)
            elif period == 'yesterday':
                yesterday = today - timedelta(days=1)
                queryset = queryset.filter(created_at__date=yesterday)
            elif period == 'week':
                start_date = today - timedelta(days=7)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'month':
                start_date = today - timedelta(days=30)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'quarter':
                start_date = today - timedelta(days=90)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'year':
                start_date = today - timedelta(days=365)
                queryset = queryset.filter(created_at__date__gte=start_date)

        # NOVO: Filtro por campos customizados combinados
        has_realtor_and_hoa = self.request.query_params.get(
            'has_realtor_and_hoa')
        if has_realtor_and_hoa == 'true':
            queryset = queryset.filter(is_realtor=True, has_hoa=True)
        elif has_realtor_and_hoa == 'false':
            queryset = queryset.filter(Q(is_realtor=False) | Q(has_hoa=False))

        # NOVO: Filtro por valor de contrato em faixas
        value_range = self.request.query_params.get('value_range')
        if value_range:
            if value_range == 'low':  # Até 100k
                queryset = queryset.filter(contract_value__lte=100000)
            elif value_range == 'medium':  # 100k a 300k
                queryset = queryset.filter(
                    contract_value__gt=100000, contract_value__lte=300000)
            elif value_range == 'high':  # 300k a 500k
                queryset = queryset.filter(
                    contract_value__gt=300000, contract_value__lte=500000)
            elif value_range == 'premium':  # Acima de 500k
                queryset = queryset.filter(contract_value__gt=500000)

        # NOVO: Filtro por leads sem realtor atribuído
        needs_realtor = self.request.query_params.get('needs_realtor')
        if needs_realtor == 'true':
            queryset = queryset.filter(is_realtor=True, realtor__isnull=True)

        # NOVO: Filtro por leads que precisam de atenção (antigos e não convertidos)
        needs_attention = self.request.query_params.get('needs_attention')
        if needs_attention == 'true':
            old_threshold = timezone.now() - timedelta(days=7)
            attention_ids = get_status_ids_by_codes(['PENDING', 'QUALIFIED'])
            queryset = queryset.filter(
                status__in=attention_ids,
                created_at__lte=old_threshold
            )

        return queryset

    def perform_create(self, serializer):
        """
        Customizar criação - definir created_by

        LÓGICA:
        1. Se usuário autenticado, usar ele
        2. Se não autenticado, buscar usuário específico para leads públicos
        3. Se não encontrar, usar primeiro admin disponível
        4. Registrar origem do lead (web, api, etc.)
        """
        # Importar aqui para evitar circular imports
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Determinar o usuário criador
        if self.request.user.is_authenticated:
            # Caso 1: Usuário autenticado
            created_by = self.request.user
        else:
            # Caso 2: Buscar usuário específico para leads públicos
            try:
                # Buscar usuário específico para leads públicos (ex: 'public_leads_user')
                created_by = User.objects.get(username='public_leads_user')
            except User.DoesNotExist:
                try:
                    # Caso 3a: Buscar usuário com permissão específica
                    created_by = User.objects.filter(
                        is_staff=True,
                        groups__name='Lead Managers'
                    ).first()
                except:
                    # Caso 3b: Fallback para qualquer admin
                    created_by = User.objects.filter(is_staff=True).first()

        # Se ainda não tiver usuário (improvável), usar o primeiro usuário
        if not created_by:
            created_by = User.objects.first()

        # Determinar a origem do lead
        source = 'web'  # Default

        # Verificar se veio de API externa
        if self.request.META.get('HTTP_X_API_SOURCE'):
            source = self.request.META.get('HTTP_X_API_SOURCE')
        # Verificar se veio do formulário web
        elif self.request.META.get('HTTP_REFERER', '').endswith('/contact'):
            source = 'contact_form'

        # Adicionar dados extras ao lead
        extra_data = {
            'created_by': created_by,
        }

        # Salvar com os dados extras
        serializer.save(**extra_data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Dados para formulário",
        operation_description="Retorna dados necessários para o formulário de leads",
        responses={200: 'Dados para formulário'}
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def form_data(self, request):
        """
        Endpoint para obter dados necessários para formulário

        RETURNS:
        - Counties list
        - House models choices
        - Elevation choices
        - Realtors list
        - Example payload
        - hoa
        """
        data = {
            'counties': CountyChoiceSerializer(
                County.get_florida_counties(),
                many=True
            ).data,

            'house_models': [
                {'value': model.id, 'label': model.name}
                for model in ModelProject.objects.filter(is_active=True).order_by('name')
            ],

            'elevations': [
                {'value': elevation.id, 'label': elevation.name}
                for elevation in ElevationChoice.objects.filter(is_active=True).order_by('name')
            ],
            'hoas': [
                {
                    'value': hoa.id,
                    'label': hoa.name,
                    'county': hoa.county.id,
                    'county_name': hoa.county.name,
                    'has_special_rules': hoa.has_special_permit_rules
                }
                for hoa in HOA.objects.filter(is_active=True).select_related('county')
            ],

            'example_payload': {
                'client_company_name': 'ABC Construction LLC',
                'client_full_name': 'John Smith',
                'client_phone': '+15551234567',
                'client_email': 'john@example.com',
                'note': 'Client prefers contact via email',
                'is_realtor': True,
                'realtor_name': "string name",
                'realtor_phone': "phone",
                'realtor_email': "email",
                'realtor': 1,  # Será substituído por realtor real
                'has_hoa': True,
                'hoa': 1,  # Será substituído por HOA real se necessário
                'realtor': 1,  # Será substituído por realtor real
                'state': 'FL',
                'county': 1,  # Será substituído por county real
                'parcel_id': '12-123-123-12345-1234',
                'house_model': '1774',
                'other_model': '',
                'elevation': 'A',
                'contract_value': '250000.00'
            }
        }

        return Response(data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Choices para leads",
        operation_description="Retorna todas as opções de choices para formulários de leads",
        responses={200: 'Choices disponíveis para leads'}
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def choices(self, request):
        """
        Endpoint para obter todas as choices disponíveis para leads

        RETURNS:
        - Status choices (PENDING, QUALIFIED, CONVERTED, REJECTED)
        - Elevation choices (A, B, C, Contemporary, etc.)
        - House model choices (do ModelProject)
        - Counties choices
        - Realtors choices
        - HOAs choices
        """
        from leads.models.lead_types import StatusChoice, ElevationChoice
        from projects.models.model_project import ModelProject

        data = {
            'status_choices': [
                {
                    'id': status.id,
                    'code': status.code,
                    'name': status.name,
                    'description': status.description,
                    'is_active': status.is_active
                }
                for status in StatusChoice.objects.filter(is_active=True).order_by('name')
            ],

            'elevation_choices': [
                {
                    'id': elevation.id,
                    'code': elevation.code,
                    'name': elevation.name,
                    'locale_code': elevation.locale_code if hasattr(elevation, 'locale_code') else '',
                    'description': elevation.description,
                    'is_active': elevation.is_active
                }
                for elevation in ElevationChoice.objects.filter(is_active=True).order_by('name')
            ],

            'house_model_choices': [
                {
                    'id': model.id,
                    'name': model.name,
                    'code': model.code,
                    'project_type': model.project_type.name if model.project_type else '',
                    'county': model.county.name if model.county else '',
                    'specifications': model.especificacoes_padrao or '',
                    'is_active': model.is_active
                }
                for model in ModelProject.objects.filter(is_active=True).select_related('project_type', 'county').order_by('name')
            ],

            'counties': CountyChoiceSerializer(
                County.get_florida_counties(),
                many=True
            ).data,

            'realtors': [
                {
                    'id': realtor.id,
                    'name': realtor.name,
                    'phone': str(realtor.phone),
                    'email': realtor.email,
                    'is_active': realtor.is_active
                }
                for realtor in Realtor.get_active()
            ],

            'hoas': [
                {
                    'id': hoa.id,
                    'name': hoa.name,
                    'county_id': hoa.county.id,
                    'county_name': hoa.county.name,
                    'has_special_rules': hoa.has_special_permit_rules,
                    'is_active': hoa.is_active
                }
                for hoa in HOA.objects.filter(is_active=True).select_related('county').order_by('name')
            ],

            'constants': {
                'valid_management_companies': VALID_MANAGEMENT_COMPANIES,
                'convertible_statuses': ['PENDING', 'QUALIFIED'],
                'default_state': 'FL'
            }
        }

        return Response(data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Preview de conversão",
        operation_description="Retorna dados para preview de conversão de lead para contrato",
        responses={
            200: 'Dados para conversão',
            400: 'Lead não pode ser convertido',
            404: 'Lead não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def convert_preview(self, request, pk=None):
        """
        Preview de conversão de lead para contrato

        RETURNS:
        - Dados do lead
        - Incorporações disponíveis
        - Métodos de pagamento disponíveis
        - Empresas de gestão válidas
        """
        lead = self.get_object()

        # Verificar se lead pode ser convertido
        if not lead.is_convertible:
            return Response({
                'error': f"Lead with status '{lead.status.name}' cannot be converted",
                'detail': "Only leads with status PENDING or QUALIFIED can be converted to contracts."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Buscar dados para conversão
        incorporations = Incorporation.objects.filter(is_active=True)
        payment_methods = PaymentMethod.objects.filter(is_active=True)

        # Retornar dados para preview
        return Response({
            'lead': {
                'id': lead.id,
                'client_name': lead.client_full_name,
                'client_company': lead.client_company_name,
                'contract_value': float(lead.contract_value),
                'county': lead.county.name if lead.county else None,
                'house_model': lead.get_display_model(),
                'status': lead.status.name,
            },
            'available_incorporations': [
                {'id': inc.id, 'name': inc.name}
                for inc in incorporations
            ],
            'available_payment_methods': [
                {'id': pm.id, 'name': pm.name}
                for pm in payment_methods
            ],
            'management_companies': VALID_MANAGEMENT_COMPANIES,
            'example_payload': {
                'incorporation_id': incorporations.first().id if incorporations.exists() else None,
                'payment_method_id': payment_methods.first().id if payment_methods.exists() else None,
                'management_company': VALID_MANAGEMENT_COMPANIES[0] if VALID_MANAGEMENT_COMPANIES else 'L. Lira',
            }
        })

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Converter lead para contrato",
        operation_description="Converte um lead em contrato",
        request_body=LeadConversionSerializer,
        responses={
            201: 'Lead convertido com sucesso',
            400: 'Dados inválidos ou lead não pode ser convertido',
            404: 'Lead não encontrado'
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, HasLeadConversionPermission])
    def convert(self, request, pk=None):
        """
        Converter lead em contrato

        PAYLOAD:
        {
            "incorporation_id": 1,
            "management_company": "L. Lira",
            "payment_method_id": 1
        }
        """
        lead = self.get_object()

        # Extrair dados do payload
        incorporation_id = request.data.get('incorporation_id')
        management_company = request.data.get('management_company', 'L. Lira')
        payment_method_id = request.data.get('payment_method_id')

        # Validações adicionais
        if not incorporation_id:
            return Response({
                'error': 'incorporation_id is required',
                'detail': 'You must specify an incorporation for the contract.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not payment_method_id:
            return Response({
                'error': 'payment_method_id is required',
                'detail': 'You must specify a payment method for the contract.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if management_company not in VALID_MANAGEMENT_COMPANIES:
            return Response({
                'error': f'Invalid management company: {management_company}',
                'detail': f'Valid options are: {", ".join(VALID_MANAGEMENT_COMPANIES)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Chamar o service
        result = LeadConversionService.convert_lead_to_contract(
            lead=lead,
            incorporation_id=incorporation_id,
            management_company=management_company,
            payment_method_id=payment_method_id,
            user=request.user
        )

        # Processar resultado
        if result.success:
            # Registrar log de conversão
            from django.contrib.admin.models import LogEntry, CHANGE
            from django.contrib.contenttypes.models import ContentType

            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(Lead).pk,
                object_id=lead.pk,
                object_repr=str(lead),
                action_flag=CHANGE,
                change_message=f"Lead converted to contract #{result.contract.contract_number}"
            )

            return Response({
                'message': 'Lead converted successfully',
                'contract_id': result.contract.id,
                'contract_number': result.contract.contract_number,
                'lead_id': lead.id,
                'client_name': lead.client_full_name,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Conversion failed',
                'errors': result.errors,
                'warnings': result.warnings,
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Estatísticas de leads",
        operation_description="Retorna estatísticas de leads",
        responses={200: 'Estatísticas de leads'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de leads

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - county_id: ID do county para filtrar estatísticas

        RETURNS:
        - Contadores por status
        - Valor total em pipeline
        - Lead mais antigo
        - Conversão rate
        - Estatísticas por county
        - Estatísticas por período
        """
        # Aplicar filtros padrão da queryset
        queryset = self.get_queryset()

        # Filtrar por período específico para estatísticas
        period = request.query_params.get('period', 'all')

        if period != 'all':
            today = timezone.now().date()

            if period == 'today':
                queryset = queryset.filter(created_at__date=today)
            elif period == 'yesterday':
                yesterday = today - timedelta(days=1)
                queryset = queryset.filter(created_at__date=yesterday)
            elif period == 'week':
                start_date = today - timedelta(days=7)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'month':
                start_date = today - timedelta(days=30)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'quarter':
                start_date = today - timedelta(days=90)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'year':
                start_date = today - timedelta(days=365)
                queryset = queryset.filter(created_at__date__gte=start_date)

        # Filtrar por county específico
        county_id = request.query_params.get('county_id')
        if county_id:
            queryset = queryset.filter(county_id=county_id)

        # Contadores por status
        from leads.models.lead_types import StatusChoice
        status_counts = {}
        for status_choice in StatusChoice.objects.filter(is_active=True):
            status_counts[status_choice.code] = queryset.filter(
                status=status_choice.id).count()

        # Valor total em pipeline (não convertidos/rejeitados)
        pipeline_value = queryset.filter(
            status__in=['PENDING', 'QUALIFIED']
        ).aggregate(
            total=Sum('contract_value')
        )['total'] or 0

        # Lead mais antigo não convertido
        oldest_lead = queryset.filter(
            status__in=['PENDING', 'QUALIFIED']
        ).order_by('created_at').first()

        # Taxa de conversão (aproximada)
        total_leads = queryset.count()
        converted_id = get_status_id_by_code('CONVERTED')
        converted_leads = queryset.filter(
            status=converted_id).count() if converted_id else 0
        conversion_rate = (converted_leads / total_leads *
                           100) if total_leads > 0 else 0

        # Estatísticas por county
        county_stats = {}

        # Buscar todos os counties ou apenas o especificado
        counties = County.objects.all()
        if county_id:
            counties = counties.filter(id=county_id)

        for county in counties:
            county_leads = queryset.filter(county=county)
            county_total = county_leads.count()

            if county_total > 0:
                # Get status IDs for this county
                pending_id = get_status_id_by_code('PENDING')
                qualified_id = get_status_id_by_code('QUALIFIED')
                converted_id = get_status_id_by_code('CONVERTED')
                rejected_id = get_status_id_by_code('REJECTED')
                pipeline_ids = get_status_ids_by_codes(
                    ['PENDING', 'QUALIFIED'])

                county_stats[county.name] = {
                    'total': county_total,
                    'pending': county_leads.filter(status=pending_id).count() if pending_id else 0,
                    'qualified': county_leads.filter(status=qualified_id).count() if qualified_id else 0,
                    'converted': county_leads.filter(status=converted_id).count() if converted_id else 0,
                    'rejected': county_leads.filter(status=rejected_id).count() if rejected_id else 0,
                    'pipeline_value': float(county_leads.filter(
                        status__in=pipeline_ids
                    ).aggregate(total=Sum('contract_value'))['total'] or 0),
                    'conversion_rate': round(
                        (county_leads.filter(
                            status=converted_id).count() / county_total * 100)
                        if county_total > 0 and converted_id else 0,
                        2
                    )
                }

        # Estatísticas por período (tendência)
        trend_data = []

        if period != 'today' and period != 'yesterday':
            # Determinar intervalo de datas
            if period == 'all':
                # Se 'all', usar últimos 12 meses
                start_date = timezone.now().date() - timedelta(days=365)
            elif period == 'week':
                start_date = timezone.now().date() - timedelta(days=7)
            elif period == 'month':
                start_date = timezone.now().date() - timedelta(days=30)
            elif period == 'quarter':
                start_date = timezone.now().date() - timedelta(days=90)
            elif period == 'year':
                start_date = timezone.now().date() - timedelta(days=365)
            else:
                start_date = timezone.now().date() - timedelta(days=30)  # Default

            # Agrupar por data
            leads_by_date = Lead.objects.filter(
                created_at__date__gte=start_date
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')

            # Formatar para o frontend
            trend_data = [
                {
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'count': item['count']
                }
                for item in leads_by_date
            ]

        # Montar resposta
        response_data = {
            'status_counts': status_counts,
            'pipeline_value': float(pipeline_value),
            'oldest_lead_days': oldest_lead.days_since_created if oldest_lead else 0,
            'conversion_rate': round(conversion_rate, 2),
            'total_leads': total_leads,
            'county_stats': county_stats,
            'period': period,
        }

        # Adicionar trend_data se disponível
        if trend_data:
            response_data['trend_data'] = trend_data

        # Adicionar informações do filtro
        if county_id:
            county = County.objects.filter(id=county_id).first()
            if county:
                response_data['filtered_by_county'] = {
                    'id': county.id,
                    'name': county.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Excluir lead",
        operation_description="Sobrescrever método de remoção para adicionar validações",
        responses={
            204: 'Lead excluído com sucesso',
            400: 'Lead não pode ser excluído (convertido)',
            404: 'Lead não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Sobrescrever método de remoção para adicionar validações

        VALIDAÇÕES:
        1. Impedir remoção de leads convertidos
        2. Registrar log de remoção
        """
        lead = self.get_object()

        # Validar se lead está convertido
        if lead.status.code == 'CONVERTED':
            return Response(
                {
                    'error': 'Cannot delete converted leads',
                    'detail': 'Leads that have been converted to contracts cannot be deleted.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Registrar log de remoção (opcional)
        from django.contrib.admin.models import LogEntry, DELETION
        from django.contrib.contenttypes.models import ContentType

        if request.user.is_authenticated:
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(Lead).pk,
                object_id=lead.pk,
                object_repr=str(lead),
                action_flag=DELETION,
                change_message=f"Lead deleted by {request.user.username}"
            )

        # Prosseguir com a remoção
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Atualização em massa de status",
        operation_description="Atualiza o status de múltiplos leads de uma vez",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['lead_ids', 'new_status'],
            properties={
                'lead_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='Lista de IDs de leads'
                ),
                'new_status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Novo status para os leads'
                ),
                'reason': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Motivo da atualização'
                )
            }
        ),
        responses={
            200: 'Leads atualizados com sucesso',
            400: 'Dados inválidos'
        }
    )
    @action(detail=False, methods=['patch'])
    def bulk_update_status(self, request):
        """
        Endpoint para atualização em massa de status

        LIMITES:
        - Máximo de 100 leads por requisição

        PAYLOAD:
        {
            "lead_ids": [1, 2, 3],
            "new_status": "QUALIFIED",
            "reason": "Qualified after client meeting"
        }
        """
        lead_ids = request.data.get('lead_ids', [])
        new_status = request.data.get('new_status')
        reason = request.data.get('reason', 'Bulk update')

        # Validações básicas
        if not lead_ids or not new_status:
            return Response(
                {'error': 'lead_ids and new_status are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar limite de leads por requisição
        MAX_LEADS = 100
        if len(lead_ids) > MAX_LEADS:
            return Response(
                {
                    'error': f'Too many leads. Maximum allowed is {MAX_LEADS}',
                    'detail': f'You provided {len(lead_ids)} leads. Please split your request into smaller batches.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar status
        from leads.models.lead_types import StatusChoice
        valid_statuses = [
            status_obj.code for status_obj in StatusChoice.objects.filter(is_active=True)]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid options: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Atualizar leads
        queryset = self.get_queryset().filter(id__in=lead_ids)

        # Guardar IDs dos leads antes da filtragem para log
        original_ids = list(lead_ids)

        # Não permitir mudança de CONVERTED
        converted_ids = []
        converted_status_id = get_status_id_by_code('CONVERTED')
        if new_status != 'CONVERTED' and converted_status_id:
            # Identificar leads convertidos para log
            converted_leads = queryset.filter(status=converted_status_id)
            converted_ids = list(converted_leads.values_list('id', flat=True))

            # Excluir leads convertidos
            queryset = queryset.exclude(status=converted_status_id)

        # Atualizar status
        updated_count = queryset.update(status=new_status)

        # Registrar log de auditoria
        if updated_count > 0 and request.user.is_authenticated:
            from django.contrib.admin.models import LogEntry, CHANGE
            from django.contrib.contenttypes.models import ContentType

            # Criar log para cada lead atualizado
            updated_leads = Lead.objects.filter(
                id__in=lead_ids, status=new_status)
            content_type = ContentType.objects.get_for_model(Lead)

            # Log de resumo geral
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=content_type.pk,
                object_id=','.join(str(id) for id in lead_ids),
                object_repr=f'Bulk update of {updated_count} leads',
                action_flag=CHANGE,
                change_message=f'Changed status to {new_status}. Reason: {reason}'
            )

            # Logs individuais (opcional, pode ser comentado se gerar muitos logs)
            for lead in updated_leads:
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=content_type.pk,
                    object_id=lead.pk,
                    object_repr=str(lead),
                    action_flag=CHANGE,
                    change_message=f'Status changed to {new_status} in bulk update. Reason: {reason}'
                )

        # Preparar resposta
        response_data = {
            'message': f'{updated_count} leads updated to {new_status}',
            'updated_count': updated_count,
            'total_requested': len(original_ids),
        }

        # Adicionar informações sobre leads não atualizados
        if updated_count < len(original_ids):
            not_updated_count = len(original_ids) - updated_count
            response_data['not_updated_count'] = not_updated_count

            # Se houver leads convertidos que não foram atualizados
            if new_status != 'CONVERTED' and converted_ids:
                response_data['converted_leads_count'] = len(converted_ids)
                response_data['converted_leads'] = converted_ids
                response_data['warning'] = 'Converted leads cannot be updated to another status'

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Dashboard de leads",
        operation_description="Retorna dados para o dashboard de leads",
        responses={200: 'Dashboard de leads'}
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard com métricas e gráficos para leads

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - county_id: ID do county para filtrar estatísticas

        RETURNS:
        - Métricas gerais
        - Dados para gráficos
        - Tendências e comparações
        """
        # Aplicar filtros padrão da queryset
        queryset = self.get_queryset()

        # Filtrar por período
        period = request.query_params.get('period', 'month')
        start_date = None

        if period != 'all':
            today = timezone.now().date()

            if period == 'today':
                start_date = today
                queryset = queryset.filter(created_at__date=today)
            elif period == 'yesterday':
                start_date = today - timedelta(days=1)
                queryset = queryset.filter(created_at__date=start_date)
            elif period == 'week':
                start_date = today - timedelta(days=7)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'month':
                start_date = today - timedelta(days=30)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'quarter':
                start_date = today - timedelta(days=90)
                queryset = queryset.filter(created_at__date__gte=start_date)
            elif period == 'year':
                start_date = today - timedelta(days=365)
                queryset = queryset.filter(created_at__date__gte=start_date)

        # Filtrar por county
        county_id = request.query_params.get('county_id')
        if county_id:
            queryset = queryset.filter(county_id=county_id)

        # 1. Métricas gerais
        total_leads = queryset.count()
        total_value = queryset.aggregate(
            total=Sum('contract_value'))['total'] or 0

        # Contadores por status
        from leads.models.lead_types import StatusChoice
        status_counts = {}
        for status_choice in StatusChoice.objects.filter(is_active=True):
            status_counts[status_choice.code] = queryset.filter(
                status=status_choice.id).count()

        # Valor em pipeline
        pipeline_ids = get_status_ids_by_codes(['PENDING', 'QUALIFIED'])
        pipeline_value = queryset.filter(
            status__in=pipeline_ids
        ).aggregate(total=Sum('contract_value'))['total'] or 0

        # Taxa de conversão
        converted_id = get_status_id_by_code('CONVERTED')
        converted_leads = queryset.filter(
            status=converted_id).count() if converted_id else 0
        conversion_rate = (converted_leads / total_leads *
                           100) if total_leads > 0 else 0

        # 2. Dados para gráficos

        # 2.1 Leads por dia (tendência)
        if start_date:
            leads_by_date = Lead.objects.filter(
                created_at__date__gte=start_date
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id'),
                value=Sum('contract_value')
            ).order_by('date')

            trend_data = [
                {
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'count': item['count'],
                    'value': float(item['value'] or 0)
                }
                for item in leads_by_date
            ]
        else:
            # Se 'all', usar últimos 12 meses agrupados por mês
            from django.db.models.functions import TruncMonth

            leads_by_month = Lead.objects.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id'),
                value=Sum('contract_value')
            ).order_by('month')[:12]  # Últimos 12 meses

            trend_data = [
                {
                    'date': item['month'].strftime('%Y-%m'),
                    'count': item['count'],
                    'value': float(item['value'] or 0)
                }
                for item in leads_by_month
            ]

        # 2.2 Leads por county (distribuição geográfica)
        leads_by_county = queryset.values(
            'county__name'
        ).annotate(
            count=Count('id'),
            value=Sum('contract_value')
        ).order_by('-count')

        county_data = [
            {
                'county': item['county__name'],
                'count': item['count'],
                'value': float(item['value'] or 0)
            }
            for item in leads_by_county if item['county__name']
        ]

        # 2.3 Leads por valor de contrato (distribuição)
        value_ranges = [
            {'min': 0, 'max': 100000, 'label': 'Até $100k'},
            {'min': 100000, 'max': 200000, 'label': '$100k-$200k'},
            {'min': 200000, 'max': 300000, 'label': '$200k-$300k'},
            {'min': 300000, 'max': 500000, 'label': '$300k-$500k'},
            {'min': 500000, 'max': None, 'label': 'Acima de $500k'}
        ]

        value_distribution = []
        for range_info in value_ranges:
            min_value = range_info['min']
            max_value = range_info['max']

            if max_value:
                count = queryset.filter(
                    contract_value__gte=min_value,
                    contract_value__lt=max_value
                ).count()
            else:
                count = queryset.filter(
                    contract_value__gte=min_value
                ).count()

            value_distribution.append({
                'range': range_info['label'],
                'count': count,
                'percentage': round((count / total_leads * 100) if total_leads > 0 else 0, 1)
            })

        # 3. Comparações e insights

        # 3.1 Comparação com período anterior
        comparison_data = {}

        if period != 'all' and start_date:
            # Calcular duração do período atual
            if period == 'today' or period == 'yesterday':
                duration = 1
            elif period == 'week':
                duration = 7
            elif period == 'month':
                duration = 30
            elif period == 'quarter':
                duration = 90
            else:  # year
                duration = 365

            # Período anterior com mesma duração
            previous_end = start_date - timedelta(days=1)
            previous_start = previous_end - timedelta(days=duration-1)

            # Buscar leads do período anterior
            previous_leads = Lead.objects.filter(
                created_at__date__gte=previous_start,
                created_at__date__lte=previous_end
            )

            if county_id:
                previous_leads = previous_leads.filter(county_id=county_id)

            previous_count = previous_leads.count()
            previous_value = previous_leads.aggregate(
                total=Sum('contract_value'))['total'] or 0
            converted_id = get_status_id_by_code('CONVERTED')
            previous_converted = previous_leads.filter(
                status=converted_id).count() if converted_id else 0

            # Calcular variações
            count_change = total_leads - previous_count
            count_change_pct = (
                (total_leads / previous_count * 100) - 100) if previous_count > 0 else None

            value_change = total_value - previous_value
            value_change_pct = (
                (total_value / previous_value * 100) - 100) if previous_value > 0 else None

            conversion_change = conversion_rate - \
                ((previous_converted / previous_count * 100)
                 if previous_count > 0 else 0)

            comparison_data = {
                'previous_period': {
                    'start_date': previous_start.strftime('%Y-%m-%d'),
                    'end_date': previous_end.strftime('%Y-%m-%d'),
                    'total_leads': previous_count,
                    'total_value': float(previous_value),
                },
                'changes': {
                    'leads_count': count_change,
                    'leads_percentage': round(count_change_pct, 1) if count_change_pct is not None else None,
                    'value': float(value_change),
                    'value_percentage': round(value_change_pct, 1) if value_change_pct is not None else None,
                    'conversion_rate': round(conversion_change, 1),
                }
            }

        # Montar resposta final
        response_data = {
            'period': period,
            'metrics': {
                'total_leads': total_leads,
                'total_value': float(total_value),
                'pipeline_value': float(pipeline_value),
                'conversion_rate': round(conversion_rate, 1),
                'status_counts': status_counts,
                'average_value': round(float(total_value / total_leads) if total_leads > 0 else 0, 2),
            },
            'charts': {
                'trend': trend_data,
                'counties': county_data,
                'value_distribution': value_distribution,
            },
            'comparison': comparison_data
        }

        # Adicionar informações do filtro
        if county_id:
            county = County.objects.filter(id=county_id).first()
            if county:
                response_data['filtered_by_county'] = {
                    'id': county.id,
                    'name': county.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Leads relacionados",
        operation_description="Retorna leads relacionados ao lead atual",
        responses={
            200: 'Leads relacionados',
            404: 'Lead não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """
        Buscar leads relacionados ao lead atual

        RETURNS:
        - Leads com mesmo email, telefone ou endereço
        - Leads do mesmo cliente (nome)
        - Leads na mesma região (county)
        """
        lead = self.get_object()

        # Buscar por email, telefone ou nome do cliente
        related_by_contact = Lead.objects.filter(
            Q(client_email=lead.client_email) |
            Q(client_phone=lead.client_phone) |
            Q(client_full_name=lead.client_full_name)
        ).exclude(id=lead.id).distinct()

        # Buscar por parcel_id (mesmo endereço)
        related_by_address = Lead.objects.filter(
            parcel_id=lead.parcel_id
        ).exclude(id=lead.id).exclude(
            id__in=related_by_contact.values_list('id', flat=True)
        ).distinct()

        # Buscar por county e proximidade de valor de contrato
        # (leads similares na mesma região)
        min_value = lead.contract_value * 0.8  # 20% menor
        max_value = lead.contract_value * 1.2  # 20% maior

        related_by_region = Lead.objects.filter(
            county=lead.county,
            contract_value__gte=min_value,
            contract_value__lte=max_value
        ).exclude(id=lead.id).exclude(
            id__in=related_by_contact.values_list('id', flat=True)
        ).exclude(
            id__in=related_by_address.values_list('id', flat=True)
        ).distinct()[:5]  # Limitar a 5 resultados

        # Serializar resultados
        contact_serializer = LeadListSerializer(related_by_contact, many=True)
        address_serializer = LeadListSerializer(related_by_address, many=True)
        region_serializer = LeadListSerializer(related_by_region, many=True)

        return Response({
            'related_by_contact': {
                'count': related_by_contact.count(),
                'leads': contact_serializer.data
            },
            'related_by_address': {
                'count': related_by_address.count(),
                'leads': address_serializer.data
            },
            'related_by_region': {
                'count': related_by_region.count(),
                'leads': region_serializer.data
            },
            'total_related': related_by_contact.count() + related_by_address.count() + related_by_region.count()
        })

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Histórico do lead",
        operation_description="Retorna o histórico de alterações do lead",
        responses={
            200: 'Histórico do lead',
            404: 'Lead não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Histórico de alterações do lead

        RETURNS:
        - Lista de alterações com data, usuário e mudanças
        """
        lead = self.get_object()

        # Obter histórico do lead
        history_records = lead.history.all().order_by('-history_date')

        # Formatar dados para resposta
        history_data = []
        for record in history_records:
            # Determinar mudanças comparando com o registro anterior
            changes = {}

            # Se não for o primeiro registro, comparar com o anterior
            if record.prev_record:
                # Comparar campos relevantes
                for field in ['status', 'contract_value', 'client_full_name',
                              'client_email', 'client_phone', 'county',
                              'house_model', 'elevation', 'has_hoa', 'hoa']:
                    old_value = getattr(record.prev_record, field)
                    new_value = getattr(record, field)

                    # Formatação especial para alguns campos
                    if field == 'status' and old_value and new_value:
                        old_value = old_value.name
                        new_value = new_value.name
                    elif field == 'county' and old_value and new_value:
                        old_value = old_value.name
                        new_value = new_value.name
                    elif field == 'hoa' and old_value and new_value:
                        old_value = old_value.name
                        new_value = new_value.name

                    # Adicionar à lista de mudanças se houve alteração
                    if old_value != new_value:
                        changes[field] = {
                            'old': str(old_value) if old_value is not None else None,
                            'new': str(new_value) if new_value is not None else None
                        }

            # Para o primeiro registro, todas as informações são novas
            else:
                changes['created'] = True

            # Adicionar ao histórico
            history_data.append({
                'date': record.history_date,
                'user': record.history_user.get_full_name() if record.history_user else 'System',
                # '+' para criação, '~' para modificação, '-' para exclusão
                'action': record.history_type,
                'changes': changes,
                'reason': record.history_change_reason or '',
            })

        return Response(history_data)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Exportar leads",
        operation_description="""
        Exporta leads para CSV ou Excel
        
        PARÂMETROS DISPONÍVEIS:
        - format=csv|excel (default: csv)
        - include_all=true|false (default: false)
        - Todos os filtros da listagem também funcionam
        
        EXEMPLOS:
        - /api/leads/export/?format=csv&include_all=true
        - /api/leads/export/?format=csv&status=PENDING
        - /api/leads/export/?format=csv&county=1&include_all=true
        """,
        responses={
            200: 'Arquivo CSV/Excel para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export corrigido - tratando objetos relacionais"""
        try:
            # Aplicar filtros padrão da queryset
            queryset = self.filter_queryset(self.get_queryset())

            # Determinar formato
            export_format = request.query_params.get('format', 'csv').lower()
            if export_format not in ['csv', 'excel']:
                return Response(
                    {'error': 'Invalid format. Valid options: csv, excel'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determinar campos a incluir
            include_all = request.query_params.get(
                'include_all', 'true').lower() == 'true'

            # Campos básicos (seguros)
            basic_fields = [
                'id', 'client_full_name', 'client_company_name', 'client_email',
                'client_phone', 'parcel_id', 'contract_value', 'created_at'
            ]

            # Campos completos (incluindo relacionais)
            all_fields = [
                'id', 'client_full_name', 'client_company_name', 'client_email',
                'client_phone', 'note', 'is_realtor', 'state',
                'parcel_id', 'other_model', 'has_hoa', 'contract_value',
                'created_at', 'updated_at', 'converted_at'
            ]

            # Escolher campos
            fields = all_fields if include_all else basic_fields

            # Headers
            headers = {
                'id': 'ID',
                'client_full_name': 'Client Name',
                'client_company_name': 'Company Name',
                'client_email': 'Email',
                'client_phone': 'Phone',
                'note': 'Notes',
                'is_realtor': 'Has Realtor',
                'state': 'State',
                'parcel_id': 'Parcel ID',
                'other_model': 'Other Model',
                'has_hoa': 'Has HOA',
                'contract_value': 'Contract Value',
                'created_at': 'Created At',
                'updated_at': 'Updated At',
                'converted_at': 'Converted At'
            }

            # Exportar como CSV
            if export_format == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'

                writer = csv.writer(response)

                # Cabeçalho
                header_row = [headers.get(field, field) for field in fields]
                if include_all:
                    # Adicionar campos relacionais processados
                    header_row.extend(
                        ['County', 'Status', 'House Model', 'Realtor', 'HOA', 'Created By'])

                writer.writerow(header_row)

                # Dados
                for lead in queryset:
                    row = []

                    # Campos básicos
                    for field in fields:
                        value = getattr(lead, field, '')

                        # Formatação especial para datas
                        if field in ['created_at', 'updated_at', 'converted_at'] and value:
                            value = value.strftime('%Y-%m-%d %H:%M:%S')

                        row.append(str(value) if value is not None else '')

                    # Adicionar campos relacionais processados (se include_all)
                    if include_all:
                        # County
                        county_name = lead.county.name if lead.county else ''
                        row.append(county_name)

                        # Status
                        status_name = lead.status.name if lead.status else ''
                        row.append(status_name)

                        # House Model (usando método seguro)
                        try:
                            house_model = lead.get_display_model() if hasattr(
                                lead, 'get_display_model') else ''
                        except:
                            house_model = str(
                                lead.house_model) if lead.house_model else ''
                        row.append(house_model)

                        # Realtor
                        realtor_name = lead.realtor.name if lead.realtor else ''
                        row.append(realtor_name)

                        # HOA
                        hoa_name = lead.hoa.name if lead.hoa else ''
                        row.append(hoa_name)

                        # Created By
                        created_by = ''
                        if lead.created_by:
                            try:
                                created_by = lead.created_by.get_full_name() or lead.created_by.username
                            except:
                                created_by = str(lead.created_by)
                        row.append(created_by)

                    writer.writerow(row)

                return response

            # Excel (simplificado por enquanto)
            else:
                return Response({
                    'message': 'Excel export not implemented yet',
                    'total_leads': queryset.count()
                })

        except Exception as e:
            return Response({
                'error': f'Export failed: {str(e)}',
                'type': type(e).__name__
            }, status=500)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Qualificar lead",
        operation_description="Qualifica lead associando realtor e/ou HOA",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'realtor_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'hoa_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            200: 'Lead qualificado com sucesso',
            400: 'Dados inválidos'
        }
    )
    # NOVO METODO ADICIONADO PARA QUALIFICAR COM SEGURANÇA.
    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """Qualifica lead com validações de county"""
        lead = self.get_object()

        realtor_id = request.data.get('realtor_id')
        hoa_id = request.data.get('hoa_id')

        # Buscar objetos
        realtor_obj = None
        hoa_obj = None

        if realtor_id:
            try:
                realtor_obj = Realtor.objects.get(id=realtor_id)
            except Realtor.DoesNotExist:
                return Response({'error': 'Realtor not found'}, status=400)

        if hoa_id:
            try:
                hoa_obj = HOA.objects.get(id=hoa_id)
            except HOA.DoesNotExist:
                return Response({'error': 'HOA not found'}, status=400)

        # Qualificar com validações
        try:
            qualified_lead = LeadProcessingService.qualify_lead_with_associations(
                lead=lead,
                realtor_obj=realtor_obj,
                hoa_obj=hoa_obj,
                user=request.user
            )

            serializer = LeadDetailSerializer(qualified_lead)
            return Response({
                'message': 'Lead qualified successfully',
                'lead': serializer.data
            })

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="HOAs disponíveis",
        operation_description="Lista HOAs disponíveis para o county da lead",
        manual_parameters=[
            openapi.Parameter(
                'name', openapi.IN_QUERY,
                description="Filtrar por nome da HOA",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: 'Lista de HOAs disponíveis'}
    )
    @action(detail=True, methods=['get'])
    def available_hoas(self, request, pk=None):
        """Lista HOAs disponíveis para o county da lead"""
        lead = self.get_object()

        # Filtro opcional por nome
        name_filter = request.query_params.get('name')

        hoas = LeadProcessingService.find_hoas_by_county(
            county=lead.county,
            name_filter=name_filter
        )

        hoa_data = [
            {
                'id': hoa.id,
                'name': hoa.name,
                'county': hoa.county.name,
                'has_special_rules': hoa.has_special_permit_rules
            }
            for hoa in hoas
        ]

        return Response({
            'county': lead.county.name,
            'total_hoas': len(hoa_data),
            'hoas': hoa_data
        })

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Buscar realtors",
        operation_description="Busca realtors por nome, email ou telefone",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Termo de busca (nome, email ou telefone)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: 'Lista de realtors encontrados'}
    )
    @action(detail=False, methods=['get'])
    def search_realtors(self, request):
        """Busca realtors para associação com leads"""
        search_term = request.query_params.get('search', '').strip()

        if not search_term:
            return Response({
                'realtors': [],
                'message': 'Provide search term to find realtors'
            })

        from core.models import Realtor
        from django.db.models import Q

        realtors = Realtor.objects.filter(
            Q(name__icontains=search_term) |
            Q(email__icontains=search_term) |
            Q(phone__icontains=search_term),
            is_active=True
        ).order_by('name')[:10]  # Limitar a 10 resultados

        realtor_data = [
            {
                'id': realtor.id,
                'name': realtor.name,
                'phone': str(realtor.phone),
                'email': realtor.email,
            }
            for realtor in realtors
        ]

        return Response({
            'search_term': search_term,
            'total_found': len(realtor_data),
            'realtors': realtor_data
        })

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Criar realtor",
        operation_description="Cria novo realtor a partir dos dados textuais da lead",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            201: 'Realtor criado com sucesso',
            400: 'Dados inválidos'
        }
    )
    @action(detail=True, methods=['post'])
    def create_realtor_from_lead(self, request, pk=None):
        """Cria realtor a partir dos dados textuais da lead"""
        lead = self.get_object()

        # Usar dados da lead como padrão
        name = request.data.get('name', lead.realtor_name)
        phone = request.data.get('phone', lead.realtor_phone)
        email = request.data.get('email', lead.realtor_email)

        if not name:
            return Response({
                'error': 'Realtor name is required'
            }, status=400)

        try:
            from .services import LeadProcessingService

            realtor = LeadProcessingService.find_or_create_realtor(
                name=name,
                phone=phone,
                email=email
            )

            return Response({
                'message': 'Realtor created/found successfully',
                'realtor': {
                    'id': realtor.id,
                    'name': realtor.name,
                    'phone': str(realtor.phone),
                    'email': realtor.email,
                }
            }, status=201)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @swagger_auto_schema(
        tags=[API_TAGS['LEADS']],
        operation_summary="Validar dados para qualificação",
        operation_description="Valida se lead está pronto para ser qualificado",
        responses={200: 'Status de validação'}
    )
    @action(detail=True, methods=['get'])
    def validate_for_qualification(self, request, pk=None):
        """Verifica se lead está pronto para qualificação"""
        lead = self.get_object()

        from .services import LeadProcessingService

        validation_result = LeadProcessingService.validate_lead_readiness_for_qualification(
            lead)

        return Response({
            'lead_id': lead.id,
            'ready_for_qualification': validation_result['ready'],
            'errors': validation_result['errors'],
            'warnings': validation_result['warnings'],
            'next_steps': [
                'Associate realtor object' if lead.is_realtor and not lead.realtor else None,
                'Associate HOA object' if lead.has_hoa and not lead.hoa else None,
                'Fix validation errors' if validation_result['errors'] else None
            ]
        })
