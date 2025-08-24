# apps/projects/views.py
from .models.contact import Contact
import csv
import io
import xlsxwriter
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
from core.pagination import CustomPageNumberPagination
from core.models import County
from .models.incorporation import Incorporation
from ..contracts.models.contract import Contract
from .models.project import Project
from .models.phase_project import PhaseProject
from .models.task_project import TaskProject
from .models.choice_types import ProjectType, ProjectStatus, IncorporationType, IncorporationStatus, ProductionCell
from .models.model_project import ModelProject
from .models.model_phase import ModelPhase
from .models.model_task import ModelTask
from .models.cost_group import CostGroup
from .models.cost_subgroup import CostSubGroup
from .models.choice_types import ProductionCell
from ..contracts.models.contract_owner import ContractOwner
from .models.contract_project import ContractProject
from .models.choice_types import (
    ProjectType,
    ProjectStatus,
    IncorporationType,
    IncorporationStatus,
    StatusContract, PaymentMethod, OwnerType
)


from .serializers import (
    IncorporationListSerializer, IncorporationDetailSerializer, IncorporationCreateUpdateSerializer,
    ContractListSerializer, ContractDetailSerializer, ContractCreateUpdateSerializer,
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    PhaseProjectListSerializer, PhaseProjectDetailSerializer, PhaseProjectCreateUpdateSerializer,
    TaskProjectListSerializer, TaskProjectDetailSerializer, TaskProjectCreateUpdateSerializer,
    ContactListSerializer, ContactDetailSerializer, ContactCreateUpdateSerializer,
    ContractOwnerSerializer, ContractProjectSerializer,
    ModelProjectListSerializer,
    ModelProjectDetailSerializer,
    ModelProjectCreateUpdateSerializer,
    ModelPhaseListSerializer,
    ModelPhaseDetailSerializer,
    ModelPhaseCreateUpdateSerializer,
    ModelTaskListSerializer,
    ModelTaskDetailSerializer,
    ModelTaskCreateUpdateSerializer,
    CostGroupListSerializer,
    CostGroupDetailSerializer,
    CostGroupCreateUpdateSerializer,
    CostSubGroupListSerializer,
    CostSubGroupDetailSerializer,
    CostSubGroupCreateUpdateSerializer,
    ProductionCellListSerializer,
    ProductionCellDetailSerializer,
    ProductionCellCreateUpdateSerializer,
    # Choice Types Serializers
    ProjectTypeListSerializer, ProjectTypeDetailSerializer, ProjectTypeCreateUpdateSerializer,
    ProjectStatusListSerializer, ProjectStatusDetailSerializer, ProjectStatusCreateUpdateSerializer,
    IncorporationTypeListSerializer, IncorporationTypeDetailSerializer, IncorporationTypeCreateUpdateSerializer,
    IncorporationStatusListSerializer, IncorporationStatusDetailSerializer, IncorporationStatusCreateUpdateSerializer,
    StatusContractListSerializer, StatusContractDetailSerializer, StatusContractCreateUpdateSerializer,
    PaymentMethodListSerializer, PaymentMethodDetailSerializer, PaymentMethodCreateUpdateSerializer,
    OwnerTypeListSerializer, OwnerTypeDetailSerializer, OwnerTypeCreateUpdateSerializer,
    # Contract Management Serializers (melhorados)
    ContractOwnerListSerializer, ContractOwnerDetailSerializer, ContractOwnerCreateUpdateSerializer,
    ContractProjectListSerializer, ContractProjectDetailSerializer, ContractProjectCreateUpdateSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.swagger_tags import API_TAGS


class IncorporationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de incorporações (empreendimentos)

    ENDPOINTS:
    - GET /api/projects/incorporations/ - Lista incorporações com filtros
    - POST /api/projects/incorporations/ - Criar nova incorporação
    - GET /api/projects/incorporations/{id}/ - Detalhes de incorporação
    - PATCH /api/projects/incorporations/{id}/ - Atualizar incorporação
    - DELETE /api/projects/incorporations/{id}/ - Remover incorporação
    - GET /api/projects/incorporations/{id}/projects/ - Listar projetos da incorporação
    - GET /api/projects/incorporations/{id}/contracts/ - Listar contratos da incorporação
    - GET /api/projects/incorporations/stats/ - Estatísticas de incorporações
    - GET /api/projects/incorporations/dashboard/ - Dashboard de incorporações
    """

    queryset = Incorporation.objects.select_related(
        'county', 'created_by', 'incorporation_type', 'incorporation_status').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = IncorporationListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'incorporation_type': ['exact'],
        'incorporation_status': ['exact', 'in'],
        'county': ['exact'],
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'launch_date': ['exact', 'gte', 'lte'],
    }

    # Campos de busca
    search_fields = [
        'name',
        'project_description',
    ]

    # Ordenação
    ordering_fields = [
        'created_at',
        'updated_at',
        'name',
        'launch_date',
    ]
    ordering = ['-created_at']  # Default: mais recentes primeiro

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar incorporações",
        operation_description="Retorna uma lista paginada de incorporações com filtros",
        responses={200: IncorporationListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes da incorporação",
        operation_description="Retorna detalhes completos de uma incorporação específica",
        responses={
            200: IncorporationDetailSerializer(),
            404: 'Incorporação não encontrada'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar incorporação",
        operation_description="Cria uma nova incorporação",
        request_body=IncorporationCreateUpdateSerializer,
        responses={
            201: IncorporationDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar incorporação",
        operation_description="Atualiza uma incorporação existente",
        request_body=IncorporationCreateUpdateSerializer,
        responses={
            200: IncorporationDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Incorporação não encontrada'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar incorporação parcialmente",
        operation_description="Atualiza parcialmente uma incorporação existente",
        request_body=IncorporationCreateUpdateSerializer,
        responses={
            200: IncorporationDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Incorporação não encontrada'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir incorporação",
        operation_description="Exclui uma incorporação existente",
        responses={
            204: 'Incorporação excluída com sucesso',
            404: 'Incorporação não encontrada'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return IncorporationDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return IncorporationCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar projetos da incorporação",
        operation_description="Retorna uma lista de projetos da incorporação",
        responses={
            200: ProjectListSerializer(many=True),
            404: 'Incorporação não encontrada'
        }
    )
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """
        Listar projetos da incorporação
        """
        incorporation = self.get_object()
        projects = incorporation.projects.all()

        # Aplicar paginação
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar contratos da incorporação",
        operation_description="Retorna uma lista de contratos da incorporação",
        responses={
            200: ContractListSerializer(many=True),
            404: 'Incorporação não encontrada'
        }
    )
    @action(detail=True, methods=['get'])
    def contracts(self, request, pk=None):
        """
        Listar contratos da incorporação
        """
        incorporation = self.get_object()
        contracts = incorporation.contracts.all()

        # Aplicar paginação
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de incorporações",
        operation_description="Retorna estatísticas de incorporações",
        responses={200: 'Estatísticas de incorporações'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de incorporações

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - county_id: ID do county para filtrar estatísticas

        RETURNS:
        - Contadores por status
        - Total de incorporações
        - Total de projetos
        - Total de contratos
        - Estatísticas por county
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
        status_counts = {}
        for status in IncorporationStatus.objects.all():
            status_counts[status.code] = queryset.filter(
                incorporation_status=status).count()

        # Total de incorporações
        total_incorporations = queryset.count()

        # Total de projetos
        total_projects = sum(inc.total_projects for inc in queryset)

        # Total de projetos vendidos
        total_projects_sold = sum(inc.projects_sold for inc in queryset)

        # Percentual médio de vendas
        avg_sold_percentage = sum(inc.sold_percentage for inc in queryset) / \
            total_incorporations if total_incorporations > 0 else 0

        # Estatísticas por county
        county_stats = {}

        # Buscar todos os counties ou apenas o especificado
        counties = County.objects.all()
        if county_id:
            counties = counties.filter(id=county_id)

        for county in counties:
            county_incorporations = queryset.filter(county=county)
            county_total = county_incorporations.count()

            if county_total > 0:
                county_projects = sum(
                    inc.total_projects for inc in county_incorporations)
                county_projects_sold = sum(
                    inc.projects_sold for inc in county_incorporations)

                county_stats[county.name] = {
                    'total_incorporations': county_total,
                    'total_projects': county_projects,
                    'projects_sold': county_projects_sold,
                    'sold_percentage': (county_projects_sold / county_projects * 100) if county_projects > 0 else 0,
                }

        # Montar resposta
        response_data = {
            'status_counts': status_counts,
            'total_incorporations': total_incorporations,
            'total_projects': total_projects,
            'total_projects_sold': total_projects_sold,
            'avg_sold_percentage': round(avg_sold_percentage, 2),
            'county_stats': county_stats,
            'period': period,
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
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Dashboard de incorporações",
        operation_description="Retorna dados para o dashboard de incorporações",
        responses={200: 'Dashboard de incorporações'}
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard com métricas e gráficos para incorporações

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
        total_incorporations = queryset.count()
        total_projects = sum(inc.total_projects for inc in queryset)
        total_projects_sold = sum(inc.projects_sold for inc in queryset)
        avg_sold_percentage = sum(inc.sold_percentage for inc in queryset) / \
            total_incorporations if total_incorporations > 0 else 0

        # Contadores por status
        status_counts = {}
        for status in IncorporationStatus.objects.all():
            status_counts[status.code] = queryset.filter(
                incorporation_status=status).count()

        # 2. Dados para gráficos

        # 2.1 Incorporações por dia (tendência)
        if start_date:
            incorporations_by_date = Incorporation.objects.filter(
                created_at__date__gte=start_date
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')

            trend_data = [
                {
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'count': item['count']
                }
                for item in incorporations_by_date
            ]
        else:
            # Se 'all', usar últimos 12 meses agrupados por mês
            from django.db.models.functions import TruncMonth

            incorporations_by_month = Incorporation.objects.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')[:12]  # Últimos 12 meses

            trend_data = [
                {
                    'date': item['month'].strftime('%Y-%m'),
                    'count': item['count']
                }
                for item in incorporations_by_month
            ]

        # 2.2 Incorporações por county (distribuição geográfica)
        incorporations_by_county = queryset.values(
            'county__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        county_data = [
            {
                'county': item['county__name'],
                'count': item['count']
            }
            for item in incorporations_by_county if item['county__name']
        ]

        # 2.3 Incorporações por tipo
        incorporations_by_type = queryset.values(
            'incorporation_type__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        type_data = [
            {
                'type': item['incorporation_type__name'],
                'count': item['count']
            }
            for item in incorporations_by_type if item['incorporation_type__name']
        ]

        # Montar resposta final
        response_data = {
            'period': period,
            'metrics': {
                'total_incorporations': total_incorporations,
                'total_projects': total_projects,
                'total_projects_sold': total_projects_sold,
                'avg_sold_percentage': round(avg_sold_percentage, 2),
                'status_counts': status_counts,
            },
            'charts': {
                'trend': trend_data,
                'counties': county_data,
                'types': type_data,
            }
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
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar incorporações",
        operation_description="Exporta incorporações para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar incorporações para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com incorporações filtradas
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'name', 'incorporation_type', 'county', 'incorporation_status',
            'launch_date', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'name', 'incorporation_type', 'county', 'project_description',
            'launch_date', 'incorporation_status', 'is_active', 'created_at',
            'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'name': 'Name',
            'incorporation_type': 'Type',
            'county': 'County',
            'project_description': 'Description',
            'launch_date': 'Launch Date',
            'incorporation_status': 'Status',
            'is_active': 'Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="incorporations_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for incorporation in queryset:
                row = []
                for field in fields:
                    value = getattr(incorporation, field)

                    # Formatação especial para alguns campos
                    if field == 'county' and value:
                        value = value.name
                    elif field == 'incorporation_type' and value:
                        value = value.name
                    elif field == 'incorporation_status' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at', 'launch_date'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Incorporations')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, incorporation in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(incorporation, field)

                    # Formatação especial para alguns campos
                    if field == 'county' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'incorporation_type' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'incorporation_status' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['created_at', 'updated_at', 'launch_date'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="incorporations_export.xlsx"'

            return response


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de contratos

    ENDPOINTS:
    - GET /api/projects/contracts/ - Lista contratos com filtros
    - POST /api/projects/contracts/ - Criar novo contrato
    - GET /api/projects/contracts/{id}/ - Detalhes de contrato
    - PATCH /api/projects/contracts/{id}/ - Atualizar contrato
    - DELETE /api/projects/contracts/{id}/ - Remover contrato
    - GET /api/projects/contracts/{id}/projects/ - Listar projetos do contrato
    - GET /api/projects/contracts/{id}/owners/ - Listar proprietários do contrato
    - GET /api/projects/contracts/stats/ - Estatísticas de contratos
    - GET /api/projects/contracts/dashboard/ - Dashboard de contratos
    """

    queryset = Contract.objects.select_related(
        'lead', 'incorporation', 'created_by', 'status_contract', 'payment_method').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ContractListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'status_contract': ['exact', 'in'],
        'incorporation': ['exact'],
        'lead': ['exact'],
        'payment_method': ['exact'],
        'management_company': ['exact'],
        'sign_date': ['exact', 'gte', 'lte'],
        'payment_date': ['exact', 'gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'contract_value': ['gte', 'lte'],
    }

    # Campos de busca
    search_fields = [
        'contract_number',
        'lead__client_full_name',
        'lead__client_email',
        'lead__client_phone',
    ]

    # Ordenação
    ordering_fields = [
        'created_at',
        'updated_at',
        'sign_date',
        'contract_value',
        'contract_number',
    ]
    ordering = ['-sign_date']  # Default: mais recentes primeiro

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar contratos",
        operation_description="Retorna uma lista paginada de contratos com filtros",
        responses={200: ContractListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes do contrato",
        operation_description="Retorna detalhes completos de um contrato específico",
        responses={
            200: ContractDetailSerializer(),
            404: 'Contrato não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar contrato",
        operation_description="Cria um novo contrato",
        request_body=ContractCreateUpdateSerializer,
        responses={
            201: ContractDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar contrato",
        operation_description="Atualiza um contrato existente",
        request_body=ContractCreateUpdateSerializer,
        responses={
            200: ContractDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Contrato não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar contrato parcialmente",
        operation_description="Atualiza parcialmente um contrato existente",
        request_body=ContractCreateUpdateSerializer,
        responses={
            200: ContractDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Contrato não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir contrato",
        operation_description="Exclui um contrato existente",
        responses={
            204: 'Contrato excluído com sucesso',
            404: 'Contrato não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ContractDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ContractCreateUpdateSerializer
        elif self.action == 'owners':
            return ContractOwnerSerializer
        elif self.action == 'projects':
            return ContractProjectSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar projetos do contrato",
        operation_description="Retorna uma lista de projetos do contrato",
        responses={
            200: ProjectListSerializer(many=True),
            404: 'Contrato não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """
        Listar projetos do contrato
        """
        contract = self.get_object()
        projects = contract.contract_projects.all()

        # Aplicar paginação
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar proprietários do contrato",
        operation_description="Retorna uma lista de proprietários do contrato",
        responses={
            200: ContractOwnerSerializer(many=True),
            404: 'Contrato não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def owners(self, request, pk=None):
        """
        Listar proprietários do contrato
        """
        contract = self.get_object()
        owners = contract.owners.all()

        # Aplicar paginação
        page = self.paginate_queryset(owners)
        if page is not None:
            serializer = ContractOwnerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ContractOwnerSerializer(owners, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de contratos",
        operation_description="Retorna estatísticas de contratos",
        responses={200: 'Estatísticas de contratos'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de contratos

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - incorporation_id: ID da incorporação para filtrar estatísticas

        RETURNS:
        - Contadores por status
        - Valor total dos contratos
        - Estatísticas por incorporação
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

        # Filtrar por incorporação específica
        incorporation_id = request.query_params.get('incorporation_id')
        if incorporation_id:
            queryset = queryset.filter(incorporation_id=incorporation_id)

        # Contadores por status
        status_counts = {}
        for status in queryset.values('status_contract__code', 'status_contract__name').distinct():
            status_counts[status['status_contract__code']] = queryset.filter(
                status_contract__code=status['status_contract__code']).count()

        # Valor total dos contratos
        total_value = queryset.aggregate(
            total=Sum('contract_value'))['total'] or 0

        # Total de contratos
        total_contracts = queryset.count()

        # Estatísticas por incorporação
        incorporation_stats = {}

        # Buscar todas as incorporações ou apenas a especificada
        incorporations = Incorporation.objects.all()
        if incorporation_id:
            incorporations = incorporations.filter(id=incorporation_id)

        for incorporation in incorporations:
            incorporation_contracts = queryset.filter(
                incorporation=incorporation)
            incorporation_total = incorporation_contracts.count()

            if incorporation_total > 0:
                incorporation_value = incorporation_contracts.aggregate(
                    total=Sum('contract_value'))['total'] or 0

                incorporation_stats[incorporation.name] = {
                    'total_contracts': incorporation_total,
                    'total_value': float(incorporation_value),
                    'avg_value': float(incorporation_value / incorporation_total),
                }

        # Montar resposta
        response_data = {
            'status_counts': status_counts,
            'total_contracts': total_contracts,
            'total_value': float(total_value),
            'avg_value': float(total_value / total_contracts) if total_contracts > 0 else 0,
            'incorporation_stats': incorporation_stats,
            'period': period,
        }

        # Adicionar informações do filtro
        if incorporation_id:
            incorporation = Incorporation.objects.filter(
                id=incorporation_id).first()
            if incorporation:
                response_data['filtered_by_incorporation'] = {
                    'id': incorporation.id,
                    'name': incorporation.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Dashboard de contratos",
        operation_description="Retorna dados para o dashboard de contratos",
        responses={200: 'Dashboard de contratos'}
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard com métricas e gráficos para contratos

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - incorporation_id: ID da incorporação para filtrar estatísticas

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

        # Filtrar por incorporação
        incorporation_id = request.query_params.get('incorporation_id')
        if incorporation_id:
            queryset = queryset.filter(incorporation_id=incorporation_id)

        # 1. Métricas gerais
        total_contracts = queryset.count()
        total_value = queryset.aggregate(
            total=Sum('contract_value'))['total'] or 0

        # Contadores por status
        status_counts = {}
        for status in queryset.values('status_contract__code', 'status_contract__name').distinct():
            status_counts[status['status_contract__code']] = queryset.filter(
                status_contract__code=status['status_contract__code']).count()

        # 2. Dados para gráficos

        # 2.1 Contratos por dia (tendência)
        if start_date:
            contracts_by_date = Contract.objects.filter(
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
                for item in contracts_by_date
            ]

        # 2.2 Contratos por incorporação
        contracts_by_incorporation = queryset.values(
            'incorporation__name'
        ).annotate(
            count=Count('id'),
            value=Sum('contract_value')
        ).order_by('-count')

        incorporation_data = [
            {
                'incorporation': item['incorporation__name'],
                'count': item['count'],
                'value': float(item['value'] or 0)
            }
            for item in contracts_by_incorporation if item['incorporation__name']
        ]

        # 2.3 Contratos por valor (distribuição)
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
                'percentage': round((count / total_contracts * 100) if total_contracts > 0 else 0, 1)
            })

        # Montar resposta final
        response_data = {
            'period': period,
            'metrics': {
                'total_contracts': total_contracts,
                'total_value': float(total_value),
                'avg_value': round(float(total_value / total_contracts) if total_contracts > 0 else 0, 2),
                'status_counts': status_counts,
            },
            'charts': {
                'trend': trend_data,
                'incorporations': incorporation_data,
                'value_distribution': value_distribution,
            }
        }

        # Adicionar informações do filtro
        if incorporation_id:
            incorporation = Incorporation.objects.filter(
                id=incorporation_id).first()
            if incorporation:
                response_data['filtered_by_incorporation'] = {
                    'id': incorporation.id,
                    'name': incorporation.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar contratos",
        operation_description="Exporta contratos para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar contratos para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com contratos filtrados
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'contract_number', 'lead', 'incorporation', 'contract_value',
            'management_company', 'status_contract', 'sign_date', 'created_at'
        ]

        all_fields = [
            'id', 'contract_number', 'lead', 'incorporation', 'contract_value',
            'management_company', 'payment_method', 'sign_date', 'payment_date',
            'status_contract', 'created_at', 'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'contract_number': 'Contract Number',
            'lead': 'Lead',
            'incorporation': 'Incorporation',
            'contract_value': 'Contract Value',
            'management_company': 'Management Company',
            'payment_method': 'Payment Method',
            'sign_date': 'Sign Date',
            'payment_date': 'Payment Date',
            'status_contract': 'Status',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="contracts_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for contract in queryset:
                row = []
                for field in fields:
                    value = getattr(contract, field)

                    # Formatação especial para alguns campos
                    if field == 'lead' and value:
                        value = value.client_full_name
                    elif field == 'incorporation' and value:
                        value = value.name
                    elif field == 'status_contract' and value:
                        value = value.name
                    elif field == 'payment_method' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at', 'sign_date', 'payment_date'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Contracts')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, contract in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(contract, field)

                    # Formatação especial para alguns campos
                    if field == 'lead' and value:
                        worksheet.write(row, col, value.client_full_name)
                    elif field == 'incorporation' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'status_contract' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'payment_method' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'contract_value' and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field in ['created_at', 'updated_at', 'sign_date', 'payment_date'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="contracts_export.xlsx"'

            return response


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de projetos

    ENDPOINTS:
    - GET /api/projects/projects/ - Lista projetos com filtros
    - POST /api/projects/projects/ - Criar novo projeto
    - GET /api/projects/projects/{id}/ - Detalhes de projeto
    - PATCH /api/projects/projects/{id}/ - Atualizar projeto
    - DELETE /api/projects/projects/{id}/ - Remover projeto
    - GET /api/projects/projects/{id}/phases/ - Listar fases do projeto
    - GET /api/projects/projects/{id}/tasks/ - Listar tarefas do projeto
    - GET /api/projects/projects/stats/ - Estatísticas de projetos
    - GET /api/projects/projects/dashboard/ - Dashboard de projetos
    """

    queryset = Project.objects.select_related(
        'incorporation', 'model_project', 'status_project', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'incorporation': ['exact'],
        'model_project': ['exact'],
        'status_project': ['exact', 'in'],
        'production_cell': ['exact'],
        'completion_percentage': ['gte', 'lte'],
        'expected_delivery_date': ['exact', 'gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'sale_value': ['gte', 'lte'],
    }

    # Campos de busca
    search_fields = [
        'project_name',
        'address',
    ]

    # Ordenação
    ordering_fields = [
        'created_at',
        'updated_at',
        'project_name',
        'expected_delivery_date',
        'completion_percentage',
        'sale_value',
    ]
    ordering = ['-created_at']  # Default: mais recentes primeiro

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

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

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        elif self.action == 'phases':
            return PhaseProjectListSerializer
        elif self.action == 'tasks':
            return TaskProjectListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

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
        """
        Listar fases do projeto
        """
        project = self.get_object()
        phases = project.phases.all().order_by('execution_order')

        # Aplicar paginação
        page = self.paginate_queryset(phases)
        if page is not None:
            serializer = PhaseProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PhaseProjectListSerializer(phases, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar tarefas do projeto",
        operation_description="Retorna uma lista de tarefas do projeto",
        responses={
            200: TaskProjectListSerializer(many=True),
            404: 'Projeto não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Listar todas as tarefas do projeto (de todas as fases)
        """
        project = self.get_object()
        tasks = TaskProject.objects.filter(
            phase_project__project=project).select_related('phase_project')

        # Aplicar paginação
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskProjectListSerializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de projetos",
        operation_description="Retorna estatísticas de projetos",
        responses={200: 'Estatísticas de projetos'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de projetos

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - incorporation_id: ID da incorporação para filtrar estatísticas

        RETURNS:
        - Contadores por status
        - Valor total dos projetos
        - Percentual médio de conclusão
        - Estatísticas por incorporação
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

        # Filtrar por incorporação específica
        incorporation_id = request.query_params.get('incorporation_id')
        if incorporation_id:
            queryset = queryset.filter(incorporation_id=incorporation_id)

        # Contadores por status
        status_counts = {}
        for status in queryset.values('status_project__code', 'status_project__name').distinct():
            status_counts[status['status_project__code']] = queryset.filter(
                status_project__code=status['status_project__code']).count()

        # Valor total dos projetos
        total_value = queryset.aggregate(total=Sum('sale_value'))['total'] or 0

        # Total de projetos
        total_projects = queryset.count()

        # Percentual médio de conclusão
        from django.db.models import Avg
        avg_completion = queryset.aggregate(
            avg=Avg('completion_percentage'))['avg'] or 0

        # Estatísticas por incorporação
        incorporation_stats = {}

        # Buscar todas as incorporações ou apenas a especificada
        incorporations = Incorporation.objects.all()
        if incorporation_id:
            incorporations = incorporations.filter(id=incorporation_id)

        for incorporation in incorporations:
            incorporation_projects = queryset.filter(
                incorporation=incorporation)
            incorporation_total = incorporation_projects.count()

            if incorporation_total > 0:
                incorporation_value = incorporation_projects.aggregate(
                    total=Sum('sale_value'))['total'] or 0
                incorporation_completion = incorporation_projects.aggregate(
                    avg=Avg('completion_percentage'))['avg'] or 0

                incorporation_stats[incorporation.name] = {
                    'total_projects': incorporation_total,
                    'total_value': float(incorporation_value),
                    'avg_value': float(incorporation_value / incorporation_total),
                    'avg_completion': float(incorporation_completion),
                }

        # Montar resposta
        response_data = {
            'status_counts': status_counts,
            'total_projects': total_projects,
            'total_value': float(total_value),
            'avg_value': float(total_value / total_projects) if total_projects > 0 else 0,
            'avg_completion': float(avg_completion),
            'incorporation_stats': incorporation_stats,
            'period': period,
        }

        # Adicionar informações do filtro
        if incorporation_id:
            incorporation = Incorporation.objects.filter(
                id=incorporation_id).first()
            if incorporation:
                response_data['filtered_by_incorporation'] = {
                    'id': incorporation.id,
                    'name': incorporation.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Dashboard de projetos",
        operation_description="Retorna dados para o dashboard de projetos",
        responses={200: 'Dashboard de projetos'}
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard com métricas e gráficos para projetos

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - incorporation_id: ID da incorporação para filtrar estatísticas

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

        # Filtrar por incorporação
        incorporation_id = request.query_params.get('incorporation_id')
        if incorporation_id:
            queryset = queryset.filter(incorporation_id=incorporation_id)

        # 1. Métricas gerais
        from django.db.models import Avg
        total_projects = queryset.count()
        total_value = queryset.aggregate(total=Sum('sale_value'))['total'] or 0
        avg_completion = queryset.aggregate(
            avg=Avg('completion_percentage'))['avg'] or 0

        # Contadores por status
        status_counts = {}
        for status in queryset.values('status_project__code', 'status_project__name').distinct():
            status_counts[status['status_project__code']] = queryset.filter(
                status_project__code=status['status_project__code']).count()

        # 2. Dados para gráficos

        # 2.1 Projetos por dia (tendência)
        if start_date:
            projects_by_date = Project.objects.filter(
                created_at__date__gte=start_date
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id'),
                value=Sum('sale_value')
            ).order_by('date')

            trend_data = [
                {
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'count': item['count'],
                    'value': float(item['value'] or 0)
                }
                for item in projects_by_date
            ]
        else:
            # Se 'all', usar últimos 12 meses agrupados por mês
            from django.db.models.functions import TruncMonth

            projects_by_month = Project.objects.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id'),
                value=Sum('sale_value')
            ).order_by('month')[:12]  # Últimos 12 meses

            trend_data = [
                {
                    'date': item['month'].strftime('%Y-%m'),
                    'count': item['count'],
                    'value': float(item['value'] or 0)
                }
                for item in projects_by_month
            ]

        # 2.2 Projetos por incorporação
        projects_by_incorporation = queryset.values(
            'incorporation__name'
        ).annotate(
            count=Count('id'),
            value=Sum('sale_value'),
            avg_completion=Avg('completion_percentage')
        ).order_by('-count')

        incorporation_data = [
            {
                'incorporation': item['incorporation__name'],
                'count': item['count'],
                'value': float(item['value'] or 0),
                'avg_completion': float(item['avg_completion'] or 0)
            }
            for item in projects_by_incorporation if item['incorporation__name']
        ]

        # 2.3 Projetos por percentual de conclusão (distribuição)
        completion_ranges = [
            {'min': 0, 'max': 20, 'label': '0-20%'},
            {'min': 20, 'max': 40, 'label': '20-40%'},
            {'min': 40, 'max': 60, 'label': '40-60%'},
            {'min': 60, 'max': 80, 'label': '60-80%'},
            {'min': 80, 'max': 100, 'label': '80-100%'},
            {'min': 100, 'max': 100.01, 'label': 'Concluído (100%)'}
        ]

        completion_distribution = []
        for range_info in completion_ranges:
            min_value = range_info['min']
            max_value = range_info['max']

            if min_value == 100 and max_value == 100.01:
                count = queryset.filter(completion_percentage=100).count()
            else:
                count = queryset.filter(
                    completion_percentage__gte=min_value,
                    completion_percentage__lt=max_value
                ).count()

            completion_distribution.append({
                'range': range_info['label'],
                'count': count,
                'percentage': round((count / total_projects * 100) if total_projects > 0 else 0, 1)
            })

        # Montar resposta final
        response_data = {
            'period': period,
            'metrics': {
                'total_projects': total_projects,
                'total_value': float(total_value),
                'avg_value': round(float(total_value / total_projects) if total_projects > 0 else 0, 2),
                'avg_completion': round(float(avg_completion), 2),
                'status_counts': status_counts,
            },
            'charts': {
                'trend': trend_data,
                'incorporations': incorporation_data,
                'completion_distribution': completion_distribution,
            }
        }

        # Adicionar informações do filtro
        if incorporation_id:
            incorporation = Incorporation.objects.filter(
                id=incorporation_id).first()
            if incorporation:
                response_data['filtered_by_incorporation'] = {
                    'id': incorporation.id,
                    'name': incorporation.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar projetos",
        operation_description="Exporta projetos para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar projetos para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com projetos filtrados
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'project_name', 'incorporation', 'model_project', 'status_project',
            'address', 'area_total', 'sale_value', 'completion_percentage',
            'expected_delivery_date', 'created_at'
        ]

        all_fields = [
            'id', 'project_name', 'incorporation', 'model_project', 'status_project',
            'production_cell', 'address', 'area_total', 'construction_cost',
            'sale_value', 'project_value', 'roi', 'completion_percentage',
            'observations', 'expected_delivery_date', 'created_at', 'updated_at',
            'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'project_name': 'Project Name',
            'incorporation': 'Incorporation',
            'model_project': 'Model Project',
            'status_project': 'Status',
            'production_cell': 'Production Cell',
            'address': 'Address',
            'area_total': 'Area Total (m²)',
            'construction_cost': 'Construction Cost',
            'sale_value': 'Sale Value',
            'project_value': 'Project Value',
            'roi': 'ROI (%)',
            'completion_percentage': 'Completion (%)',
            'observations': 'Observations',
            'expected_delivery_date': 'Expected Delivery Date',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for project in queryset:
                row = []
                for field in fields:
                    value = getattr(project, field)

                    # Formatação especial para alguns campos
                    if field == 'incorporation' and value:
                        value = value.name
                    elif field == 'model_project' and value:
                        value = value.project_name
                    elif field == 'status_project' and value:
                        value = value.name
                    elif field == 'production_cell' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at', 'expected_delivery_date'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Projects')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            percentage_format = workbook.add_format({'num_format': '0.00%'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, project in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(project, field)

                    # Formatação especial para alguns campos
                    if field == 'incorporation' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'model_project' and value:
                        worksheet.write(row, col, value.project_name)
                    elif field == 'status_project' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'production_cell' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['sale_value', 'construction_cost', 'project_value'] and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field == 'completion_percentage' and value:
                        worksheet.write(row, col, float(
                            value) / 100, percentage_format)
                    elif field == 'roi' and value:
                        worksheet.write(row, col, float(
                            value) / 100, percentage_format)
                    elif field in ['created_at', 'updated_at', 'expected_delivery_date'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="projects_export.xlsx"'

            return response


class PhaseProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de fases de projeto

    ENDPOINTS:
    - GET /api/projects/phases/ - Lista fases com filtros
    - POST /api/projects/phases/ - Criar nova fase
    - GET /api/projects/phases/{id}/ - Detalhes de fase
    - PATCH /api/projects/phases/{id}/ - Atualizar fase
    - DELETE /api/projects/phases/{id}/ - Remover fase
    - GET /api/projects/phases/{id}/tasks/ - Listar tarefas da fase
    - POST /api/projects/phases/{id}/start/ - Iniciar fase
    - POST /api/projects/phases/{id}/complete/ - Completar fase
    - POST /api/projects/phases/{id}/schedule-inspection/ - Agendar inspeção
    """

    queryset = PhaseProject.objects.select_related(
        'project', 'model_phase', 'technical_responsible', 'supervisor', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = PhaseProjectListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'project': ['exact'],
        'model_phase': ['exact'],
        'phase_status': ['exact', 'in'],
        'priority': ['exact'],
        'execution_order': ['exact', 'gte', 'lte'],
        'completion_percentage': ['gte', 'lte'],
        'requires_inspection': ['exact'],
        'technical_responsible': ['exact'],
        'supervisor': ['exact'],
        'planned_start_date': ['exact', 'gte', 'lte'],
        'planned_end_date': ['exact', 'gte', 'lte'],
        'actual_start_date': ['exact', 'gte', 'lte'],
        'actual_end_date': ['exact', 'gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'phase_name',
        'phase_code',
        'notes',
    ]

    # Ordenação
    ordering_fields = [
        'execution_order',
        'phase_name',
        'phase_status',
        'priority',
        'completion_percentage',
        'planned_start_date',
        'planned_end_date',
        'actual_start_date',
        'actual_end_date',
        'created_at',
    ]
    ordering = ['project', 'execution_order']  # Default: ordem de execução

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar fases de projeto",
        operation_description="Retorna uma lista paginada de fases de projeto com filtros",
        responses={200: PhaseProjectListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes da fase de projeto",
        operation_description="Retorna detalhes completos de uma fase de projeto específica",
        responses={
            200: PhaseProjectDetailSerializer(),
            404: 'Fase de projeto não encontrada'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar fase de projeto",
        operation_description="Cria uma nova fase de projeto",
        request_body=PhaseProjectCreateUpdateSerializer,
        responses={
            201: PhaseProjectDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar fase de projeto",
        operation_description="Atualiza uma fase de projeto existente",
        request_body=PhaseProjectCreateUpdateSerializer,
        responses={
            200: PhaseProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Fase de projeto não encontrada'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar fase de projeto parcialmente",
        operation_description="Atualiza parcialmente uma fase de projeto existente",
        request_body=PhaseProjectCreateUpdateSerializer,
        responses={
            200: PhaseProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Fase de projeto não encontrada'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir fase de projeto",
        operation_description="Exclui uma fase de projeto existente",
        responses={
            204: 'Fase de projeto excluída com sucesso',
            404: 'Fase de projeto não encontrada'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return PhaseProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PhaseProjectCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar tarefas da fase",
        operation_description="Retorna uma lista de tarefas da fase de projeto",
        responses={
            200: TaskProjectListSerializer(many=True),
            404: 'Fase de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Listar tarefas da fase
        """
        phase = self.get_object()
        tasks = phase.tasks.all().order_by('execution_order')

        # Aplicar paginação
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskProjectListSerializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Iniciar fase de projeto",
        operation_description="Inicia a execução de uma fase de projeto",
        responses={
            200: 'Fase iniciada com sucesso',
            400: 'Fase não pode ser iniciada',
            404: 'Fase de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Iniciar fase
        """
        phase = self.get_object()

        # Verificar se fase pode ser iniciada
        if not phase.can_start():
            return Response({
                'error': 'Phase cannot be started',
                'detail': 'This phase cannot be started. Check if all prerequisites are completed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Iniciar fase
        success = phase.start_phase(user=request.user)

        if success:
            return Response({
                'message': 'Phase started successfully',
                'phase_id': phase.id,
                'phase_name': phase.phase_name,
                'phase_status': phase.phase_status,
                'actual_start_date': phase.actual_start_date,
            })
        else:
            return Response({
                'error': 'Failed to start phase',
                'detail': 'An error occurred while starting the phase.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Completar fase de projeto",
        operation_description="Marca uma fase de projeto como concluída",
        responses={
            200: 'Fase completada com sucesso',
            400: 'Fase não pode ser completada',
            404: 'Fase de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Completar fase
        """
        phase = self.get_object()

        # Verificar se fase pode ser completada
        if phase.tasks_completion_percentage < 100:
            return Response({
                'error': 'Phase cannot be completed',
                'detail': 'All tasks must be completed before completing the phase.',
                'tasks_completion_percentage': phase.tasks_completion_percentage
            }, status=status.HTTP_400_BAD_REQUEST)

        # Completar fase
        success = phase.complete_phase(user=request.user)

        if success:
            return Response({
                'message': 'Phase completed successfully',
                'phase_id': phase.id,
                'phase_name': phase.phase_name,
                'phase_status': phase.phase_status,
                'actual_end_date': phase.actual_end_date,
            })
        else:
            return Response({
                'error': 'Failed to complete phase',
                'detail': 'An error occurred while completing the phase.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Agendar inspeção de fase",
        operation_description="Agenda uma inspeção para uma fase de projeto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['inspection_date'],
            properties={
                'inspection_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description='Data da inspeção (formato YYYY-MM-DD)'
                )
            }
        ),
        responses={
            200: 'Inspeção agendada com sucesso',
            400: 'Dados inválidos ou fase não requer inspeção',
            404: 'Fase de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def schedule_inspection(self, request, pk=None):
        """
        Agendar inspeção para fase
        """
        phase = self.get_object()

        # Verificar se fase requer inspeção
        if not phase.requires_inspection:
            return Response({
                'error': 'Inspection not required',
                'detail': 'This phase does not require inspection.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Obter data da inspeção
        inspection_date = request.data.get('inspection_date')
        if not inspection_date:
            return Response({
                'error': 'Inspection date is required',
                'detail': 'You must provide an inspection date.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Atualizar fase
        from django.utils.dateparse import parse_date
        phase.inspection_scheduled_date = parse_date(inspection_date)
        phase.phase_status = 'WAITING_INSPECTION'
        phase.save()

        return Response({
            'message': 'Inspection scheduled successfully',
            'phase_id': phase.id,
            'phase_name': phase.phase_name,
            'phase_status': phase.phase_status,
            'inspection_scheduled_date': phase.inspection_scheduled_date,
        })

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar fases de projeto",
        operation_description="Exporta fases de projeto para CSV ou Excel",
        manual_parameters=[
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Formato de exportação (csv, excel)",
                type=openapi.TYPE_STRING,
                default="csv"
            ),
            openapi.Parameter(
                'include_all',
                openapi.IN_QUERY,
                description="Incluir todos os campos (true, false)",
                type=openapi.TYPE_BOOLEAN,
                default=False
            )
        ],
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar fases de projeto para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com fases filtradas
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'phase_name', 'phase_code', 'project', 'phase_status',
            'priority', 'execution_order', 'completion_percentage',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'technical_responsible', 'created_at'
        ]

        all_fields = [
            'id', 'phase_name', 'phase_code', 'project', 'model_phase',
            'phase_status', 'priority', 'execution_order', 'completion_percentage',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'technical_responsible', 'supervisor',
            'estimated_cost', 'actual_cost', 'requires_inspection',
            'inspection_result', 'inspection_notes', 'inspection_scheduled_date',
            'created_at', 'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'phase_name': 'Phase Name',
            'phase_code': 'Phase Code',
            'project': 'Project',
            'model_phase': 'Model Phase',
            'phase_status': 'Status',
            'priority': 'Priority',
            'execution_order': 'Execution Order',
            'completion_percentage': 'Completion (%)',
            'planned_start_date': 'Planned Start',
            'planned_end_date': 'Planned End',
            'actual_start_date': 'Actual Start',
            'actual_end_date': 'Actual End',
            'technical_responsible': 'Technical Responsible',
            'supervisor': 'Supervisor',
            'estimated_cost': 'Estimated Cost',
            'actual_cost': 'Actual Cost',
            'requires_inspection': 'Requires Inspection',
            'inspection_result': 'Inspection Result',
            'inspection_notes': 'Inspection Notes',
            'inspection_scheduled_date': 'Inspection Date',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="phases_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for phase in queryset:
                row = []
                for field in fields:
                    value = getattr(phase, field)

                    # Formatação especial para alguns campos
                    if field == 'project' and value:
                        value = value.project_name
                    elif field == 'model_phase' and value:
                        value = value.phase_name
                    elif field == 'technical_responsible' and value:
                        value = value.get_full_name() or value.username
                    elif field == 'supervisor' and value:
                        value = value.get_full_name() or value.username
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at', 'planned_start_date',
                                   'planned_end_date', 'actual_start_date',
                                   'actual_end_date', 'inspection_scheduled_date'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Phases')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            percentage_format = workbook.add_format({'num_format': '0.00%'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, phase in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(phase, field)

                    # Formatação especial para alguns campos
                    if field == 'project' and value:
                        worksheet.write(row, col, value.project_name)
                    elif field == 'model_phase' and value:
                        worksheet.write(row, col, value.phase_name)
                    elif field == 'technical_responsible' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'supervisor' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['estimated_cost', 'actual_cost'] and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field == 'completion_percentage' and value:
                        worksheet.write(row, col, float(
                            value) / 100, percentage_format)
                    elif field in ['created_at', 'updated_at', 'planned_start_date',
                                   'planned_end_date', 'actual_start_date',
                                   'actual_end_date', 'inspection_scheduled_date'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="phases_export.xlsx"'

            return response


class TaskProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de tarefas de projeto

    ENDPOINTS:
    - GET /api/projects/tasks/ - Lista tarefas com filtros
    - POST /api/projects/tasks/ - Criar nova tarefa
    - GET /api/projects/tasks/{id}/ - Detalhes de tarefa
    - PATCH /api/projects/tasks/{id}/ - Atualizar tarefa
    - DELETE /api/projects/tasks/{id}/ - Remover tarefa
    - POST /api/projects/tasks/{id}/start/ - Iniciar tarefa
    - POST /api/projects/tasks/{id}/pause/ - Pausar tarefa
    - POST /api/projects/tasks/{id}/resume/ - Retomar tarefa
    - POST /api/projects/tasks/{id}/complete/ - Completar tarefa
    - GET /api/projects/tasks/stats/ - Estatísticas de tarefas
    - GET /api/projects/tasks/export/ - Exportar tarefas (CSV/Excel)
    """

    queryset = TaskProject.objects.select_related(
        'phase_project', 'model_task', 'assigned_to', 'supervisor', 'created_by'
    ).all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = TaskProjectListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'phase_project': ['exact'],
        'model_task': ['exact'],
        'task_status': ['exact', 'in'],
        'priority': ['exact'],
        'execution_order': ['exact', 'gte', 'lte'],
        'completion_percentage': ['gte', 'lte'],
        'assigned_to': ['exact'],
        'supervisor': ['exact'],
        'requires_approval': ['exact'],
        'planned_start_date': ['exact', 'gte', 'lte'],
        'planned_end_date': ['exact', 'gte', 'lte'],
        'actual_start_date': ['exact', 'gte', 'lte'],
        'actual_end_date': ['exact', 'gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'task_name',
        'task_code',
        'task_description',
        'notes',
        'issues_found',
    ]

    # Ordenação
    ordering_fields = [
        'execution_order',
        'task_name',
        'task_status',
        'priority',
        'completion_percentage',
        'planned_start_date',
        'planned_end_date',
        'actual_start_date',
        'actual_end_date',
        'created_at',
    ]
    # Default: ordem de execução
    ordering = ['phase_project', 'execution_order']

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar tarefas de projeto",
        operation_description="Retorna uma lista paginada de tarefas de projeto com filtros",
        responses={200: TaskProjectListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes da tarefa de projeto",
        operation_description="Retorna detalhes completos de uma tarefa de projeto específica",
        responses={
            200: TaskProjectDetailSerializer(),
            404: 'Tarefa de projeto não encontrada'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar tarefa de projeto",
        operation_description="Cria uma nova tarefa de projeto",
        request_body=TaskProjectCreateUpdateSerializer,
        responses={
            201: TaskProjectDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar tarefa de projeto",
        operation_description="Atualiza uma tarefa de projeto existente",
        request_body=TaskProjectCreateUpdateSerializer,
        responses={
            200: TaskProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar tarefa de projeto parcialmente",
        operation_description="Atualiza parcialmente uma tarefa de projeto existente",
        request_body=TaskProjectCreateUpdateSerializer,
        responses={
            200: TaskProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir tarefa de projeto",
        operation_description="Exclui uma tarefa de projeto existente",
        responses={
            204: 'Tarefa de projeto excluída com sucesso',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return TaskProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskProjectCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Iniciar tarefa de projeto",
        operation_description="Inicia a execução de uma tarefa de projeto",
        responses={
            200: 'Tarefa iniciada com sucesso',
            400: 'Tarefa não pode ser iniciada',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Iniciar tarefa
        """
        task = self.get_object()

        # Verificar se tarefa pode ser iniciada
        if not task.can_start():
            return Response({
                'error': 'Task cannot be started',
                'detail': 'This task cannot be started. Check if all prerequisites are completed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Iniciar tarefa
        success = task.start_task(user=request.user)

        if success:
            return Response({
                'message': 'Task started successfully',
                'task_id': task.id,
                'task_name': task.task_name,
                'task_status': task.task_status,
                'actual_start_date': task.actual_start_date,
            })
        else:
            return Response({
                'error': 'Failed to start task',
                'detail': 'An error occurred while starting the task.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Pausar tarefa de projeto",
        operation_description="Pausa a execução de uma tarefa de projeto em andamento",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Motivo da pausa'
                )
            }
        ),
        responses={
            200: 'Tarefa pausada com sucesso',
            400: 'Tarefa não pode ser pausada',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """
        Pausar tarefa
        """
        task = self.get_object()
        reason = request.data.get('reason', '')

        # Verificar se tarefa pode ser pausada
        if task.task_status != 'IN_PROGRESS':
            return Response({
                'error': 'Task cannot be paused',
                'detail': 'Only tasks in progress can be paused.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Pausar tarefa
        success = task.pause_task(reason=reason, user=request.user)

        if success:
            return Response({
                'message': 'Task paused successfully',
                'task_id': task.id,
                'task_name': task.task_name,
                'task_status': task.task_status,
            })
        else:
            return Response({
                'error': 'Failed to pause task',
                'detail': 'An error occurred while pausing the task.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Retomar tarefa de projeto",
        operation_description="Retoma a execução de uma tarefa de projeto pausada",
        responses={
            200: 'Tarefa retomada com sucesso',
            400: 'Tarefa não pode ser retomada',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """
        Retomar tarefa
        """
        task = self.get_object()

        # Verificar se tarefa pode ser retomada
        if task.task_status != 'PAUSED':
            return Response({
                'error': 'Task cannot be resumed',
                'detail': 'Only paused tasks can be resumed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Retomar tarefa
        success = task.resume_task(user=request.user)

        if success:
            return Response({
                'message': 'Task resumed successfully',
                'task_id': task.id,
                'task_name': task.task_name,
                'task_status': task.task_status,
            })
        else:
            return Response({
                'error': 'Failed to resume task',
                'detail': 'An error occurred while resuming the task.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Completar tarefa de projeto",
        operation_description="Marca uma tarefa de projeto como concluída",
        responses={
            200: 'Tarefa completada com sucesso',
            400: 'Tarefa não pode ser completada',
            404: 'Tarefa de projeto não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Completar tarefa
        """
        task = self.get_object()

        # Verificar se tarefa pode ser completada
        if task.task_status not in ['IN_PROGRESS', 'PAUSED']:
            return Response({
                'error': 'Task cannot be completed',
                'detail': 'Only tasks in progress or paused can be completed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Completar tarefa
        success = task.complete_task(user=request.user)

        if success:
            return Response({
                'message': 'Task completed successfully',
                'task_id': task.id,
                'task_name': task.task_name,
                'task_status': task.task_status,
                'actual_end_date': task.actual_end_date,
                'actual_duration_hours': float(task.actual_duration_hours),
            })
        else:
            return Response({
                'error': 'Failed to complete task',
                'detail': 'An error occurred while completing the task.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de tarefas de projeto",
        operation_description="Retorna estatísticas de tarefas de projeto",
        manual_parameters=[
            openapi.Parameter(
                'period',
                openapi.IN_QUERY,
                description="Período para filtrar estatísticas (today, week, month, quarter, year, all)",
                type=openapi.TYPE_STRING,
                default="all"
            ),
            openapi.Parameter(
                'phase_id',
                openapi.IN_QUERY,
                description="ID da fase para filtrar estatísticas",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'project_id',
                openapi.IN_QUERY,
                description="ID do projeto para filtrar estatísticas",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: 'Estatísticas de tarefas de projeto'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de tarefas

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - phase_id: ID da fase para filtrar estatísticas
        - project_id: ID do projeto para filtrar estatísticas

        RETURNS:
        - Contadores por status
        - Contadores por prioridade
        - Tempo médio de execução
        - Estatísticas por fase
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

        # Filtrar por fase específica
        phase_id = request.query_params.get('phase_id')
        if phase_id:
            queryset = queryset.filter(phase_project_id=phase_id)

        # Filtrar por projeto específico
        project_id = request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(phase_project__project_id=project_id)

        # Contadores por status
        status_counts = {}
        for status_choice in TaskProject.STATUS_CHOICES:
            status_code = status_choice[0]
            status_counts[status_code] = queryset.filter(
                task_status=status_code).count()

        # Contadores por prioridade
        priority_counts = {}
        for priority_choice in TaskProject.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_counts[priority_code] = queryset.filter(
                priority=priority_code).count()

        # Total de tarefas
        total_tasks = queryset.count()

        # Tempo médio de execução (para tarefas completadas)
        from django.db.models import Avg
        avg_duration = queryset.filter(
            task_status='COMPLETED',
            actual_duration_hours__gt=0
        ).aggregate(avg=Avg('actual_duration_hours'))['avg'] or 0

        # Percentual médio de conclusão
        avg_completion = queryset.aggregate(
            avg=Avg('completion_percentage'))['avg'] or 0

        # Estatísticas por fase
        phase_stats = {}

        # Buscar todas as fases ou apenas a especificada
        phases = PhaseProject.objects.all()
        if phase_id:
            phases = phases.filter(id=phase_id)
        elif project_id:
            phases = phases.filter(project_id=project_id)

        for phase in phases:
            phase_tasks = queryset.filter(phase_project=phase)
            phase_total = phase_tasks.count()

            if phase_total > 0:
                completed_tasks = phase_tasks.filter(
                    task_status='COMPLETED').count()
                in_progress_tasks = phase_tasks.filter(
                    task_status='IN_PROGRESS').count()
                pending_tasks = phase_tasks.filter(
                    task_status__in=['PENDING', 'READY_TO_START']).count()

                phase_completion = phase_tasks.aggregate(
                    avg=Avg('completion_percentage'))['avg'] or 0

                phase_stats[phase.phase_name] = {
                    'total_tasks': phase_total,
                    'completed_tasks': completed_tasks,
                    'in_progress_tasks': in_progress_tasks,
                    'pending_tasks': pending_tasks,
                    'completion_percentage': float(phase_completion),
                }

        # Montar resposta
        response_data = {
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'total_tasks': total_tasks,
            'avg_duration_hours': float(avg_duration),
            'avg_completion_percentage': float(avg_completion),
            'phase_stats': phase_stats,
            'period': period,
        }

        # Adicionar informações do filtro
        if phase_id:
            phase = PhaseProject.objects.filter(id=phase_id).first()
            if phase:
                response_data['filtered_by_phase'] = {
                    'id': phase.id,
                    'name': phase.phase_name
                }

        if project_id:
            project = Project.objects.filter(id=project_id).first()
            if project:
                response_data['filtered_by_project'] = {
                    'id': project.id,
                    'name': project.project_name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar tarefas de projeto",
        operation_description="Exporta tarefas de projeto para CSV ou Excel",
        manual_parameters=[
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Formato de exportação (csv, excel)",
                type=openapi.TYPE_STRING,
                default="csv"
            ),
            openapi.Parameter(
                'include_all',
                openapi.IN_QUERY,
                description="Incluir todos os campos (true, false)",
                type=openapi.TYPE_BOOLEAN,
                default=False
            )
        ],
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar tarefas para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com tarefas filtradas
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'task_name', 'phase_project', 'task_status', 'priority',
            'assigned_to', 'completion_percentage', 'planned_start_date',
            'planned_end_date', 'actual_start_date', 'actual_end_date'
        ]

        all_fields = [
            'id', 'task_name', 'task_code', 'phase_project', 'model_task',
            'task_status', 'priority', 'execution_order', 'assigned_to',
            'supervisor', 'completion_percentage', 'quality_rating',
            'estimated_cost', 'actual_cost', 'estimated_duration_hours',
            'actual_duration_hours', 'planned_start_date', 'planned_end_date',
            'actual_start_date', 'actual_end_date', 'requires_approval',
            'approved_by', 'approval_date', 'created_at', 'updated_at',
            'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'task_name': 'Task Name',
            'task_code': 'Task Code',
            'phase_project': 'Phase',
            'model_task': 'Model Task',
            'task_status': 'Status',
            'priority': 'Priority',
            'execution_order': 'Execution Order',
            'assigned_to': 'Assigned To',
            'supervisor': 'Supervisor',
            'completion_percentage': 'Completion (%)',
            'quality_rating': 'Quality Rating',
            'estimated_cost': 'Estimated Cost',
            'actual_cost': 'Actual Cost',
            'estimated_duration_hours': 'Estimated Duration (h)',
            'actual_duration_hours': 'Actual Duration (h)',
            'planned_start_date': 'Planned Start',
            'planned_end_date': 'Planned End',
            'actual_start_date': 'Actual Start',
            'actual_end_date': 'Actual End',
            'requires_approval': 'Requires Approval',
            'approved_by': 'Approved By',
            'approval_date': 'Approval Date',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="tasks_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for task in queryset:
                row = []
                for field in fields:
                    value = getattr(task, field)

                    # Formatação especial para alguns campos
                    if field == 'phase_project' and value:
                        value = value.phase_name
                    elif field == 'model_task' and value:
                        value = value.task_name
                    elif field == 'assigned_to' and value:
                        value = value.get_full_name() or value.username
                    elif field == 'supervisor' and value:
                        value = value.get_full_name() or value.username
                    elif field == 'approved_by' and value:
                        value = value.get_full_name() or value.username
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at', 'planned_start_date',
                                   'planned_end_date', 'actual_start_date',
                                   'actual_end_date', 'approval_date'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Tasks')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            percentage_format = workbook.add_format({'num_format': '0.00%'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, task in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(task, field)

                    # Formatação especial para alguns campos
                    if field == 'phase_project' and value:
                        worksheet.write(row, col, value.phase_name)
                    elif field == 'model_task' and value:
                        worksheet.write(row, col, value.task_name)
                    elif field == 'assigned_to' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'supervisor' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'approved_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['estimated_cost', 'actual_cost'] and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field == 'completion_percentage' and value:
                        worksheet.write(row, col, float(
                            value) / 100, percentage_format)
                    elif field in ['created_at', 'updated_at', 'planned_start_date',
                                   'planned_end_date', 'actual_start_date',
                                   'actual_end_date', 'approval_date'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="tasks_export.xlsx"'

            return response


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de contatos de projeto

    ENDPOINTS:
    - GET /api/projects/contacts/ - Lista contatos com filtros
    - POST /api/projects/contacts/ - Criar novo contato
    - GET /api/projects/contacts/{id}/ - Detalhes de contato
    - PATCH /api/projects/contacts/{id}/ - Atualizar contato
    - DELETE /api/projects/contacts/{id}/ - Remover contato
    - GET /api/projects/contacts/by-project/{project_id}/ - Listar contatos por projeto
    - GET /api/projects/contacts/by-owner/{owner_id}/ - Listar contatos por proprietário
    - GET /api/projects/contacts/by-user/{user_id}/ - Listar contatos por usuário
    """

    queryset = Contact.objects.select_related(
        'contact', 'project', 'owner', 'created_by'
    ).all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ContactListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'contact': ['exact'],
        'project': ['exact'],
        'owner': ['exact'],
        'contact_role': ['exact', 'in'],
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'contact__first_name',
        'contact__last_name',
        'contact__email',
        'project__project_name',
        'owner__client__first_name',
        'owner__client__last_name',
    ]

    # Ordenação
    ordering_fields = [
        'created_at',
        'updated_at',
        'contact__first_name',
        'contact__last_name',
        'project__project_name',
        'contact_role',
    ]
    ordering = ['-created_at']  # Default: mais recentes primeiro

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar contatos",
        operation_description="Retorna uma lista paginada de contatos com filtros",
        responses={200: ContactListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes do contato",
        operation_description="Retorna detalhes completos de um contato específico",
        responses={
            200: ContactDetailSerializer(),
            404: 'Contato não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar contato",
        operation_description="Cria um novo contato",
        request_body=ContactCreateUpdateSerializer,
        responses={
            201: ContactDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar contato",
        operation_description="Atualiza um contato existente",
        request_body=ContactCreateUpdateSerializer,
        responses={
            200: ContactDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Contato não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar contato parcialmente",
        operation_description="Atualiza parcialmente um contato existente",
        request_body=ContactCreateUpdateSerializer,
        responses={
            200: ContactDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Contato não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir contato",
        operation_description="Exclui um contato existente",
        responses={
            204: 'Contato excluído com sucesso',
            404: 'Contato não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ContactDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ContactCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar contatos por projeto",
        operation_description="Retorna uma lista de contatos associados a um projeto específico",
        responses={
            200: ContactListSerializer(many=True),
            404: 'Projeto não encontrado'
        }
    )
    @action(detail=False, methods=['get'], url_path='by-project/(?P<project_id>[^/.]+)')
    def by_project(self, request, project_id=None):
        """
        Listar contatos por projeto
        """
        contacts = self.get_queryset().filter(project_id=project_id)

        # Aplicar paginação
        page = self.paginate_queryset(contacts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar contatos por proprietário",
        operation_description="Retorna uma lista de contatos associados a um proprietário específico",
        responses={
            200: ContactListSerializer(many=True),
            404: 'Proprietário não encontrado'
        }
    )
    @action(detail=False, methods=['get'], url_path='by-owner/(?P<owner_id>[^/.]+)')
    def by_owner(self, request, owner_id=None):
        """
        Listar contatos por proprietário
        """
        contacts = self.get_queryset().filter(owner_id=owner_id)

        # Aplicar paginação
        page = self.paginate_queryset(contacts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar contatos por usuário",
        operation_description="Retorna uma lista de contatos associados a um usuário específico",
        responses={
            200: ContactListSerializer(many=True),
            404: 'Usuário não encontrado'
        }
    )
    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """
        Listar contatos por usuário
        """
        contacts = self.get_queryset().filter(contact_id=user_id)

        # Aplicar paginação
        page = self.paginate_queryset(contacts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar contatos",
        operation_description="Exporta contatos para CSV ou Excel",
        manual_parameters=[
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Formato de exportação (csv, excel)",
                type=openapi.TYPE_STRING,
                default="csv"
            ),
            openapi.Parameter(
                'include_all',
                openapi.IN_QUERY,
                description="Incluir todos os campos (true, false)",
                type=openapi.TYPE_BOOLEAN,
                default=False
            )
        ],
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar contatos para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com contatos filtrados
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'contact_name', 'contact_email', 'project_name',
            'owner_name', 'contact_role', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'contact_name', 'contact_email', 'project_name',
            'owner_name', 'contact_role', 'is_active', 'created_at',
            'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'contact_name': 'Contact Name',
            'contact_email': 'Contact Email',
            'project_name': 'Project',
            'owner_name': 'Owner',
            'contact_role': 'Role',
            'is_active': 'Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="contacts_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for contact in queryset:
                row = []
                for field in fields:
                    # Campos personalizados
                    if field == 'contact_name':
                        value = contact.contact.get_full_name() if contact.contact else ''
                    elif field == 'contact_email':
                        value = contact.contact.email if contact.contact else ''
                    elif field == 'project_name':
                        value = contact.project.project_name if contact.project else ''
                    elif field == 'owner_name':
                        value = contact.owner.client.get_full_name(
                        ) if contact.owner and contact.owner.client else ''
                    elif field == 'contact_role':
                        value = contact.get_contact_role_display()
                    elif field == 'created_by' and contact.created_by:
                        value = contact.created_by.get_full_name() or contact.created_by.username
                    elif field in ['created_at', 'updated_at'] and getattr(contact, field):
                        value = getattr(contact, field).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    else:
                        value = getattr(contact, field)

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Contacts')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, contact in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    # Campos personalizados
                    if field == 'contact_name':
                        value = contact.contact.get_full_name() if contact.contact else ''
                        worksheet.write(row, col, value)
                    elif field == 'contact_email':
                        value = contact.contact.email if contact.contact else ''
                        worksheet.write(row, col, value)
                    elif field == 'project_name':
                        value = contact.project.project_name if contact.project else ''
                        worksheet.write(row, col, value)
                    elif field == 'owner_name':
                        value = contact.owner.client.get_full_name(
                        ) if contact.owner and contact.owner.client else ''
                        worksheet.write(row, col, value)
                    elif field == 'contact_role':
                        value = contact.get_contact_role_display()
                        worksheet.write(row, col, value)
                    elif field == 'created_by' and contact.created_by:
                        value = contact.created_by.get_full_name() or contact.created_by.username
                        worksheet.write(row, col, value)
                    elif field in ['created_at', 'updated_at'] and getattr(contact, field):
                        value = getattr(contact, field)
                        worksheet.write_datetime(row, col, value, date_format)
                    elif field == 'is_active':
                        value = getattr(contact, field)
                        worksheet.write(row, col, 'Yes' if value else 'No')
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        value = getattr(contact, field)
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="contacts_export.xlsx"'

            return response


class ModelProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de modelos de projeto (templates)

    ENDPOINTS:
    - GET /api/projects/model-projects/ - Lista modelos com filtros
    - POST /api/projects/model-projects/ - Criar novo modelo
    - GET /api/projects/model-projects/{id}/ - Detalhes de modelo
    - PATCH /api/projects/model-projects/{id}/ - Atualizar modelo
    - DELETE /api/projects/model-projects/{id}/ - Remover modelo
    - GET /api/projects/model-projects/{id}/phases/ - Listar fases do modelo
    - POST /api/projects/model-projects/{id}/duplicate/ - Duplicar modelo
    - GET /api/projects/model-projects/stats/ - Estatísticas de modelos
    - GET /api/projects/model-projects/dashboard/ - Dashboard de modelos
    """

    queryset = ModelProject.objects.select_related(
        'project_type', 'county', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ModelProjectListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'project_type': ['exact'],
        'county': ['exact'],
        'is_active': ['exact'],
        'builders_fee': ['gte', 'lte'],
        'area_construida_padrao': ['gte', 'lte'],
        'custo_base_estimado': ['gte', 'lte'],
        'custo_por_m2': ['gte', 'lte'],
        'duracao_construcao_dias': ['gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'versao': ['exact'],
    }

    # Campos de busca
    search_fields = [
        'name',
        'code',
        'especificacoes_padrao',
        'requisitos_especiais',
        'regulamentacoes_county',
    ]

    # Ordenação
    ordering_fields = [
        'created_at',
        'updated_at',
        'name',
        'code',
        'custo_base_estimado',
        'area_construida_padrao',
        'duracao_construcao_dias',
        'builders_fee',
    ]
    ordering = ['-created_at']  # Default: mais recentes primeiro

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar modelos de projeto",
        operation_description="Retorna uma lista paginada de modelos de projeto com filtros",
        responses={200: ModelProjectListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes do modelo de projeto",
        operation_description="Retorna detalhes completos de um modelo de projeto específico",
        responses={
            200: ModelProjectDetailSerializer(),
            404: 'Modelo de projeto não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar modelo de projeto",
        operation_description="Cria um novo modelo de projeto",
        request_body=ModelProjectCreateUpdateSerializer,
        responses={
            201: ModelProjectDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar modelo de projeto",
        operation_description="Atualiza um modelo de projeto existente",
        request_body=ModelProjectCreateUpdateSerializer,
        responses={
            200: ModelProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Modelo de projeto não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar modelo de projeto parcialmente",
        operation_description="Atualiza parcialmente um modelo de projeto existente",
        request_body=ModelProjectCreateUpdateSerializer,
        responses={
            200: ModelProjectDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Modelo de projeto não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir modelo de projeto",
        operation_description="Exclui um modelo de projeto existente",
        responses={
            204: 'Modelo de projeto excluído com sucesso',
            404: 'Modelo de projeto não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ModelProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ModelProjectCreateUpdateSerializer
        elif self.action == 'phases':
            return ModelPhaseListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar fases do modelo",
        operation_description="Retorna uma lista de fases do modelo de projeto",
        responses={
            200: ModelPhaseListSerializer(many=True),
            404: 'Modelo de projeto não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def phases(self, request, pk=None):
        """
        Listar fases do modelo
        """
        model_project = self.get_object()
        phases = model_project.phases.all().order_by('execution_order')

        # Aplicar paginação
        page = self.paginate_queryset(phases)
        if page is not None:
            serializer = ModelPhaseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ModelPhaseListSerializer(phases, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Duplicar modelo de projeto",
        operation_description="Cria uma cópia de um modelo de projeto para outro county ou versão",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_name'],
            properties={
                'new_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Nome do novo modelo'
                ),
                'new_county_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID do novo county (opcional)'
                )
            }
        ),
        responses={
            200: 'Modelo duplicado com sucesso',
            400: 'Dados inválidos',
            404: 'Modelo de projeto não encontrado'
        }
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicar modelo para outro county ou criar nova versão
        """
        model_project = self.get_object()

        # Obter dados da requisição
        new_name = request.data.get('new_name')
        new_county_id = request.data.get('new_county_id')

        if not new_name:
            return Response({
                'error': 'New name is required',
                'detail': 'You must provide a name for the new model.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se county existe
        new_county = None
        if new_county_id:
            try:
                new_county = County.objects.get(id=new_county_id)
            except County.DoesNotExist:
                return Response({
                    'error': 'County not found',
                    'detail': f'County with id {new_county_id} does not exist.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Duplicar modelo
        try:
            new_model = model_project.duplicate_model(
                new_name=new_name,
                new_county=new_county
            )
            new_model.created_by = request.user
            new_model.save()

            return Response({
                'message': 'Model duplicated successfully',
                'original_model_id': model_project.id,
                'new_model_id': new_model.id,
                'new_model_name': new_model.name,
                'new_model_code': new_model.code,
                'total_phases': new_model.total_fases,
                'total_tasks': new_model.total_tasks,
            })
        except Exception as e:
            return Response({
                'error': 'Failed to duplicate model',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de modelos de projeto",
        operation_description="Retorna estatísticas de modelos de projeto",
        responses={200: 'Estatísticas de modelos de projeto'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de modelos de projeto

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - county_id: ID do county para filtrar estatísticas

        RETURNS:
        - Contadores por tipo de projeto
        - Estatísticas de custo e área
        - Estatísticas por county
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

        # Contadores por tipo de projeto
        type_counts = {}
        for project_type in ProjectType.objects.all():
            type_counts[project_type.code] = queryset.filter(
                project_type=project_type).count()

        # Total de modelos
        total_models = queryset.count()
        active_models = queryset.filter(is_active=True).count()

        # Estatísticas de custo e área
        from django.db.models import Avg, Min, Max
        cost_stats = queryset.aggregate(
            avg_cost=Avg('custo_base_estimado'),
            min_cost=Min('custo_base_estimado'),
            max_cost=Max('custo_base_estimado'),
            avg_area=Avg('area_construida_padrao'),
            min_area=Min('area_construida_padrao'),
            max_area=Max('area_construida_padrao'),
            avg_duration=Avg('duracao_construcao_dias'),
            min_duration=Min('duracao_construcao_dias'),
            max_duration=Max('duracao_construcao_dias'),
        )

        # Estatísticas por county
        county_stats = {}
        counties = County.objects.all()
        if county_id:
            counties = counties.filter(id=county_id)

        for county in counties:
            county_models = queryset.filter(county=county)
            county_total = county_models.count()

            if county_total > 0:
                county_cost_avg = county_models.aggregate(
                    avg=Avg('custo_base_estimado'))['avg'] or 0

                county_stats[county.name] = {
                    'total_models': county_total,
                    'active_models': county_models.filter(is_active=True).count(),
                    'avg_cost': float(county_cost_avg),
                }

        # Montar resposta
        response_data = {
            'type_counts': type_counts,
            'total_models': total_models,
            'active_models': active_models,
            'inactive_models': total_models - active_models,
            'cost_stats': {
                'avg_cost': float(cost_stats['avg_cost'] or 0),
                'min_cost': float(cost_stats['min_cost'] or 0),
                'max_cost': float(cost_stats['max_cost'] or 0),
            },
            'area_stats': {
                'avg_area': float(cost_stats['avg_area'] or 0),
                'min_area': float(cost_stats['min_area'] or 0),
                'max_area': float(cost_stats['max_area'] or 0),
            },
            'duration_stats': {
                'avg_duration': float(cost_stats['avg_duration'] or 0),
                'min_duration': int(cost_stats['min_duration'] or 0),
                'max_duration': int(cost_stats['max_duration'] or 0),
            },
            'county_stats': county_stats,
            'period': period,
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
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar modelos de projeto",
        operation_description="Exporta modelos de projeto para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar modelos de projeto para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com modelos filtrados
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'name', 'code', 'project_type', 'county',
            'builders_fee', 'area_construida_padrao', 'custo_base_estimado',
            'duracao_construcao_dias', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'name', 'code', 'project_type', 'county',
            'builders_fee', 'area_construida_padrao', 'especificacoes_padrao',
            'custo_base_estimado', 'custo_por_m2', 'duracao_construcao_dias',
            'requisitos_especiais', 'regulamentacoes_county', 'versao',
            'is_active', 'created_at', 'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'name': 'Name',
            'code': 'Code',
            'project_type': 'Project Type',
            'county': 'County',
            'builders_fee': 'Builders Fee',
            'area_construida_padrao': 'Standard Area (m²)',
            'especificacoes_padrao': 'Standard Specifications',
            'custo_base_estimado': 'Estimated Base Cost',
            'custo_por_m2': 'Cost per m²',
            'duracao_construcao_dias': 'Construction Duration (days)',
            'requisitos_especiais': 'Special Requirements',
            'regulamentacoes_county': 'County Regulations',
            'versao': 'Version',
            'is_active': 'Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="model_projects_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for model in queryset:
                row = []
                for field in fields:
                    value = getattr(model, field)

                    # Formatação especial para alguns campos
                    if field == 'project_type' and value:
                        value = value.name
                    elif field == 'county' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Model Projects')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, model in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(model, field)

                    # Formatação especial para alguns campos
                    if field == 'project_type' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'county' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['builders_fee', 'custo_base_estimado', 'custo_por_m2'] and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field in ['created_at', 'updated_at'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="model_projects_export.xlsx"'

            return response


class ModelPhaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de fases de modelo (templates)

    ENDPOINTS:
    - GET /api/projects/model-phases/ - Lista fases de modelo com filtros
    - POST /api/projects/model-phases/ - Criar nova fase de modelo
    - GET /api/projects/model-phases/{id}/ - Detalhes de fase de modelo
    - PATCH /api/projects/model-phases/{id}/ - Atualizar fase de modelo
    - DELETE /api/projects/model-phases/{id}/ - Remover fase de modelo
    - GET /api/projects/model-phases/{id}/tasks/ - Listar tarefas da fase
    - POST /api/projects/model-phases/{id}/duplicate/ - Duplicar fase para outro modelo
    - GET /api/projects/model-phases/stats/ - Estatísticas de fases
    """

    queryset = ModelPhase.objects.select_related(
        'project_model', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ModelPhaseListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'project_model': ['exact'],
        'execution_order': ['exact', 'gte', 'lte'],
        'estimated_duration_days': ['gte', 'lte'],
        'is_mandatory': ['exact'],
        'allows_parallel': ['exact'],
        'requires_inspection': ['exact'],
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'version': ['exact'],
    }

    # Campos de busca
    search_fields = [
        'phase_name',
        'phase_code',
        'phase_description',
        'phase_objectives',
        'initial_requirements',
        'completion_criteria',
        'deliverables',
    ]

    # Ordenação
    ordering_fields = [
        'project_model',
        'execution_order',
        'phase_name',
        'estimated_duration_days',
        'created_at',
        'updated_at',
    ]
    # Default: ordem de execução
    ordering = ['project_model', 'execution_order']

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar fases de modelo",
        operation_description="Retorna uma lista paginada de fases de modelo com filtros",
        responses={200: ModelPhaseListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes da fase de modelo",
        operation_description="Retorna detalhes completos de uma fase de modelo específica",
        responses={
            200: ModelPhaseDetailSerializer(),
            404: 'Fase de modelo não encontrada'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar fase de modelo",
        operation_description="Cria uma nova fase de modelo",
        request_body=ModelPhaseCreateUpdateSerializer,
        responses={
            201: ModelPhaseDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar fase de modelo",
        operation_description="Atualiza uma fase de modelo existente",
        request_body=ModelPhaseCreateUpdateSerializer,
        responses={
            200: ModelPhaseDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Fase de modelo não encontrada'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar fase de modelo parcialmente",
        operation_description="Atualiza parcialmente uma fase de modelo existente",
        request_body=ModelPhaseCreateUpdateSerializer,
        responses={
            200: ModelPhaseDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Fase de modelo não encontrada'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir fase de modelo",
        operation_description="Exclui uma fase de modelo existente",
        responses={
            204: 'Fase de modelo excluída com sucesso',
            404: 'Fase de modelo não encontrada'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ModelPhaseDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ModelPhaseCreateUpdateSerializer
        elif self.action == 'tasks':
            return ModelTaskListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar tarefas da fase",
        operation_description="Retorna uma lista de tarefas da fase de modelo",
        responses={
            200: ModelTaskListSerializer(many=True),
            404: 'Fase de modelo não encontrada'
        }
    )
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Listar tarefas da fase
        """
        model_phase = self.get_object()
        tasks = model_phase.tasks.all().order_by('execution_order')

        # Aplicar paginação
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = ModelTaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ModelTaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Duplicar fase para outro modelo",
        operation_description="Duplica uma fase de modelo para outro modelo de projeto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['target_model_id'],
            properties={
                'target_model_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID do modelo de projeto de destino'
                )
            }
        ),
        responses={
            200: 'Fase duplicada com sucesso',
            400: 'Dados inválidos',
            404: 'Fase de modelo não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicar fase para outro modelo
        """
        model_phase = self.get_object()

        # Obter dados da requisição
        target_model_id = request.data.get('target_model_id')

        if not target_model_id:
            return Response({
                'error': 'Target model ID is required',
                'detail': 'You must provide the ID of the target model project.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se modelo de destino existe
        try:
            target_model = ModelProject.objects.get(id=target_model_id)
        except ModelProject.DoesNotExist:
            return Response({
                'error': 'Target model not found',
                'detail': f'Model project with id {target_model_id} does not exist.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Duplicar fase
        try:
            new_phase = model_phase.duplicate_to_model(target_model)
            new_phase.created_by = request.user
            new_phase.save()

            return Response({
                'message': 'Phase duplicated successfully',
                'original_phase_id': model_phase.id,
                'new_phase_id': new_phase.id,
                'target_model_id': target_model.id,
                'target_model_name': target_model.name,
                'total_tasks': new_phase.total_tasks,
            })
        except Exception as e:
            return Response({
                'error': 'Failed to duplicate phase',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de fases de modelo",
        operation_description="Retorna estatísticas de fases de modelo",
        responses={200: 'Estatísticas de fases de modelo'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de fases de modelo

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - model_id: ID do modelo para filtrar estatísticas

        RETURNS:
        - Estatísticas gerais de fases
        - Distribuição por duração
        - Fases que requerem inspeção
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

        # Filtrar por modelo específico
        model_id = request.query_params.get('model_id')
        if model_id:
            queryset = queryset.filter(project_model_id=model_id)

        # Total de fases
        total_phases = queryset.count()
        active_phases = queryset.filter(is_active=True).count()
        mandatory_phases = queryset.filter(is_mandatory=True).count()
        inspection_phases = queryset.filter(requires_inspection=True).count()
        parallel_phases = queryset.filter(allows_parallel=True).count()

        # Estatísticas de duração
        from django.db.models import Avg, Min, Max
        duration_stats = queryset.aggregate(
            avg_duration=Avg('estimated_duration_days'),
            min_duration=Min('estimated_duration_days'),
            max_duration=Max('estimated_duration_days'),
        )

        # Distribuição por duração
        duration_ranges = [
            {'min': 1, 'max': 7, 'label': '1-7 days'},
            {'min': 8, 'max': 14, 'label': '8-14 days'},
            {'min': 15, 'max': 30, 'label': '15-30 days'},
            {'min': 31, 'max': 60, 'label': '31-60 days'},
            {'min': 61, 'max': None, 'label': '60+ days'}
        ]

        duration_distribution = []
        for range_info in duration_ranges:
            min_value = range_info['min']
            max_value = range_info['max']

            if max_value:
                count = queryset.filter(
                    estimated_duration_days__gte=min_value,
                    estimated_duration_days__lte=max_value
                ).count()
            else:
                count = queryset.filter(
                    estimated_duration_days__gte=min_value
                ).count()

            duration_distribution.append({
                'range': range_info['label'],
                'count': count,
                'percentage': round((count / total_phases * 100) if total_phases > 0 else 0, 1)
            })

        # Estatísticas por modelo
        model_stats = {}
        models = ModelProject.objects.all()
        if model_id:
            models = models.filter(id=model_id)

        for model in models:
            model_phases = queryset.filter(project_model=model)
            model_total = model_phases.count()

            if model_total > 0:
                model_duration_avg = model_phases.aggregate(
                    avg=Avg('estimated_duration_days'))['avg'] or 0

                model_stats[model.name] = {
                    'total_phases': model_total,
                    'mandatory_phases': model_phases.filter(is_mandatory=True).count(),
                    'inspection_phases': model_phases.filter(requires_inspection=True).count(),
                    'avg_duration': float(model_duration_avg),
                }

        # Montar resposta
        response_data = {
            'total_phases': total_phases,
            'active_phases': active_phases,
            'inactive_phases': total_phases - active_phases,
            'mandatory_phases': mandatory_phases,
            'optional_phases': total_phases - mandatory_phases,
            'inspection_phases': inspection_phases,
            'parallel_phases': parallel_phases,
            'duration_stats': {
                'avg_duration': float(duration_stats['avg_duration'] or 0),
                'min_duration': int(duration_stats['min_duration'] or 0),
                'max_duration': int(duration_stats['max_duration'] or 0),
            },
            'duration_distribution': duration_distribution,
            'model_stats': model_stats,
            'period': period,
        }

        # Adicionar informações do filtro
        if model_id:
            model = ModelProject.objects.filter(id=model_id).first()
            if model:
                response_data['filtered_by_model'] = {
                    'id': model.id,
                    'name': model.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar fases de modelo",
        operation_description="Exporta fases de modelo para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar fases de modelo para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com fases filtradas
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'phase_name', 'phase_code', 'project_model',
            'execution_order', 'estimated_duration_days', 'is_mandatory',
            'allows_parallel', 'requires_inspection', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'phase_name', 'phase_code', 'project_model',
            'phase_description', 'phase_objectives', 'execution_order',
            'estimated_duration_days', 'is_mandatory', 'allows_parallel',
            'requires_inspection', 'initial_requirements', 'completion_criteria',
            'deliverables', 'is_active', 'version', 'created_at', 'updated_at',
            'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'phase_name': 'Phase Name',
            'phase_code': 'Phase Code',
            'project_model': 'Project Model',
            'phase_description': 'Description',
            'phase_objectives': 'Objectives',
            'execution_order': 'Execution Order',
            'estimated_duration_days': 'Duration (days)',
            'is_mandatory': 'Mandatory',
            'allows_parallel': 'Allows Parallel',
            'requires_inspection': 'Requires Inspection',
            'initial_requirements': 'Initial Requirements',
            'completion_criteria': 'Completion Criteria',
            'deliverables': 'Deliverables',
            'is_active': 'Active',
            'version': 'Version',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="model_phases_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for phase in queryset:
                row = []
                for field in fields:
                    value = getattr(phase, field)

                    # Formatação especial para alguns campos
                    if field == 'project_model' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Model Phases')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, phase in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(phase, field)

                    # Formatação especial para alguns campos
                    if field == 'project_model' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['created_at', 'updated_at'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif field in ['is_mandatory', 'allows_parallel', 'requires_inspection', 'is_active']:
                        worksheet.write(row, col, 'Yes' if value else 'No')
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="model_phases_export.xlsx"'

            return response


class ModelTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de tarefas de modelo (templates)

    ENDPOINTS:
    - GET /api/projects/model-tasks/ - Lista tarefas de modelo com filtros
    - POST /api/projects/model-tasks/ - Criar nova tarefa de modelo
    - GET /api/projects/model-tasks/{id}/ - Detalhes de tarefa de modelo
    - PATCH /api/projects/model-tasks/{id}/ - Atualizar tarefa de modelo
    - DELETE /api/projects/model-tasks/{id}/ - Remover tarefa de modelo
    - POST /api/projects/model-tasks/{id}/duplicate/ - Duplicar tarefa para outra fase
    - GET /api/projects/model-tasks/stats/ - Estatísticas de tarefas
    """

    queryset = ModelTask.objects.select_related(
        'model_phase', 'cost_subgroup', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ModelTaskListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'model_phase': ['exact'],
        'task_type': ['exact', 'in'],
        'execution_order': ['exact', 'gte', 'lte'],
        'estimated_duration_hours': ['gte', 'lte'],
        'is_mandatory': ['exact'],
        'allows_parallel': ['exact'],
        'requires_specialization': ['exact'],
        'skill_category': ['exact', 'in'],
        'required_people': ['exact', 'gte', 'lte'],
        'estimated_labor_cost': ['gte', 'lte'],
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'version': ['exact'],
        'cost_subgroup': ['exact'],
    }

    # Campos de busca
    search_fields = [
        'task_name',
        'task_code',
        'detailed_description',
        'task_objective',
        'required_skills',
        'special_requirements',
        'execution_conditions',
        'required_equipment',
        'acceptance_criteria',
        'identified_risks',
        'safety_measures',
        'required_ppe',
    ]

    # Ordenação
    ordering_fields = [
        'model_phase',
        'execution_order',
        'task_name',
        'task_type',
        'estimated_duration_hours',
        'required_people',
        'estimated_labor_cost',
        'created_at',
        'updated_at',
    ]
    ordering = ['model_phase', 'execution_order']  # Default: ordem de execução

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar tarefas de modelo",
        operation_description="Retorna uma lista paginada de tarefas de modelo com filtros",
        responses={200: ModelTaskListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes da tarefa de modelo",
        operation_description="Retorna detalhes completos de uma tarefa de modelo específica",
        responses={
            200: ModelTaskDetailSerializer(),
            404: 'Tarefa de modelo não encontrada'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar tarefa de modelo",
        operation_description="Cria uma nova tarefa de modelo",
        request_body=ModelTaskCreateUpdateSerializer,
        responses={
            201: ModelTaskDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar tarefa de modelo",
        operation_description="Atualiza uma tarefa de modelo existente",
        request_body=ModelTaskCreateUpdateSerializer,
        responses={
            200: ModelTaskDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Tarefa de modelo não encontrada'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar tarefa de modelo parcialmente",
        operation_description="Atualiza parcialmente uma tarefa de modelo existente",
        request_body=ModelTaskCreateUpdateSerializer,
        responses={
            200: ModelTaskDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Tarefa de modelo não encontrada'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir tarefa de modelo",
        operation_description="Exclui uma tarefa de modelo existente",
        responses={
            204: 'Tarefa de modelo excluída com sucesso',
            404: 'Tarefa de modelo não encontrada'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ModelTaskDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ModelTaskCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Duplicar tarefa para outra fase",
        operation_description="Duplica uma tarefa de modelo para outra fase de modelo",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['target_phase_id'],
            properties={
                'target_phase_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID da fase de modelo de destino'
                )
            }
        ),
        responses={
            200: 'Tarefa duplicada com sucesso',
            400: 'Dados inválidos',
            404: 'Tarefa de modelo não encontrada'
        }
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicar tarefa para outra fase
        """
        model_task = self.get_object()

        # Obter dados da requisição
        target_phase_id = request.data.get('target_phase_id')

        if not target_phase_id:
            return Response({
                'error': 'Target phase ID is required',
                'detail': 'You must provide the ID of the target model phase.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se fase de destino existe
        try:
            target_phase = ModelPhase.objects.get(id=target_phase_id)
        except ModelPhase.DoesNotExist:
            return Response({
                'error': 'Target phase not found',
                'detail': f'Model phase with id {target_phase_id} does not exist.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Duplicar tarefa
        try:
            new_task = model_task.duplicate_to_phase(target_phase)
            new_task.created_by = request.user
            new_task.save()

            return Response({
                'message': 'Task duplicated successfully',
                'original_task_id': model_task.id,
                'new_task_id': new_task.id,
                'target_phase_id': target_phase.id,
                'target_phase_name': target_phase.phase_name,
                'total_resources': new_task.total_resources,
            })
        except Exception as e:
            return Response({
                'error': 'Failed to duplicate task',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de tarefas de modelo",
        operation_description="Retorna estatísticas de tarefas de modelo",
        responses={200: 'Estatísticas de tarefas de modelo'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de tarefas de modelo

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - phase_id: ID da fase para filtrar estatísticas
        - model_id: ID do modelo para filtrar estatísticas

        RETURNS:
        - Estatísticas gerais de tarefas
        - Distribuição por tipo e categoria
        - Estatísticas de duração e custo
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

        # Filtrar por fase específica
        phase_id = request.query_params.get('phase_id')
        if phase_id:
            queryset = queryset.filter(model_phase_id=phase_id)

        # Filtrar por modelo específico
        model_id = request.query_params.get('model_id')
        if model_id:
            queryset = queryset.filter(model_phase__project_model_id=model_id)

        # Total de tarefas
        total_tasks = queryset.count()
        active_tasks = queryset.filter(is_active=True).count()
        mandatory_tasks = queryset.filter(is_mandatory=True).count()
        specialized_tasks = queryset.filter(
            requires_specialization=True).count()
        parallel_tasks = queryset.filter(allows_parallel=True).count()

        # Contadores por tipo
        type_counts = {}
        for task_type in ModelTask.TASK_TYPE_CHOICES:
            type_code = task_type[0]
            type_counts[type_code] = queryset.filter(
                task_type=type_code).count()

        # Contadores por categoria de habilidade
        skill_counts = {}
        for skill_category in ModelTask.SKILL_CATEGORY_CHOICES:
            skill_code = skill_category[0]
            skill_counts[skill_code] = queryset.filter(
                skill_category=skill_code).count()

        # Estatísticas de duração e custo
        from django.db.models import Avg, Min, Max, Sum
        duration_cost_stats = queryset.aggregate(
            avg_duration=Avg('estimated_duration_hours'),
            min_duration=Min('estimated_duration_hours'),
            max_duration=Max('estimated_duration_hours'),
            total_duration=Sum('estimated_duration_hours'),
            avg_cost=Avg('estimated_labor_cost'),
            min_cost=Min('estimated_labor_cost'),
            max_cost=Max('estimated_labor_cost'),
            total_cost=Sum('estimated_labor_cost'),
            avg_people=Avg('required_people'),
            min_people=Min('required_people'),
            max_people=Max('required_people'),
        )

        # Distribuição por duração
        duration_ranges = [
            {'min': 0.1, 'max': 4, 'label': '0.1-4 hours'},
            {'min': 4.1, 'max': 8, 'label': '4-8 hours'},
            {'min': 8.1, 'max': 16, 'label': '8-16 hours'},
            {'min': 16.1, 'max': 40, 'label': '16-40 hours'},
            {'min': 40.1, 'max': None, 'label': '40+ hours'}
        ]

        duration_distribution = []
        for range_info in duration_ranges:
            min_value = range_info['min']
            max_value = range_info['max']

            if max_value:
                count = queryset.filter(
                    estimated_duration_hours__gte=min_value,
                    estimated_duration_hours__lte=max_value
                ).count()
            else:
                count = queryset.filter(
                    estimated_duration_hours__gte=min_value
                ).count()

            duration_distribution.append({
                'range': range_info['label'],
                'count': count,
                'percentage': round((count / total_tasks * 100) if total_tasks > 0 else 0, 1)
            })

        # Estatísticas por fase
        phase_stats = {}
        phases = ModelPhase.objects.all()
        if phase_id:
            phases = phases.filter(id=phase_id)
        elif model_id:
            phases = phases.filter(project_model_id=model_id)

        for phase in phases:
            phase_tasks = queryset.filter(model_phase=phase)
            phase_total = phase_tasks.count()

            if phase_total > 0:
                phase_duration_total = phase_tasks.aggregate(
                    total=Sum('estimated_duration_hours'))['total'] or 0
                phase_cost_total = phase_tasks.aggregate(
                    total=Sum('estimated_labor_cost'))['total'] or 0

                phase_stats[phase.phase_name] = {
                    'total_tasks': phase_total,
                    'mandatory_tasks': phase_tasks.filter(is_mandatory=True).count(),
                    'specialized_tasks': phase_tasks.filter(requires_specialization=True).count(),
                    'total_duration': float(phase_duration_total),
                    'total_cost': float(phase_cost_total),
                }

        # Montar resposta
        response_data = {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'inactive_tasks': total_tasks - active_tasks,
            'mandatory_tasks': mandatory_tasks,
            'optional_tasks': total_tasks - mandatory_tasks,
            'specialized_tasks': specialized_tasks,
            'parallel_tasks': parallel_tasks,
            'type_counts': type_counts,
            'skill_counts': skill_counts,
            'duration_stats': {
                'avg_duration': float(duration_cost_stats['avg_duration'] or 0),
                'min_duration': float(duration_cost_stats['min_duration'] or 0),
                'max_duration': float(duration_cost_stats['max_duration'] or 0),
                'total_duration': float(duration_cost_stats['total_duration'] or 0),
            },
            'cost_stats': {
                'avg_cost': float(duration_cost_stats['avg_cost'] or 0),
                'min_cost': float(duration_cost_stats['min_cost'] or 0),
                'max_cost': float(duration_cost_stats['max_cost'] or 0),
                'total_cost': float(duration_cost_stats['total_cost'] or 0),
            },
            'people_stats': {
                'avg_people': float(duration_cost_stats['avg_people'] or 0),
                'min_people': int(duration_cost_stats['min_people'] or 0),
                'max_people': int(duration_cost_stats['max_people'] or 0),
            },
            'duration_distribution': duration_distribution,
            'phase_stats': phase_stats,
            'period': period,
        }

        # Adicionar informações do filtro
        if phase_id:
            phase = ModelPhase.objects.filter(id=phase_id).first()
            if phase:
                response_data['filtered_by_phase'] = {
                    'id': phase.id,
                    'name': phase.phase_name
                }

        if model_id:
            model = ModelProject.objects.filter(id=model_id).first()
            if model:
                response_data['filtered_by_model'] = {
                    'id': model.id,
                    'name': model.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar tarefas de modelo",
        operation_description="Exporta tarefas de modelo para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar tarefas de modelo para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com tarefas filtradas
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'task_name', 'task_code', 'model_phase', 'task_type',
            'estimated_duration_hours', 'execution_order', 'is_mandatory',
            'requires_specialization', 'skill_category', 'required_people',
            'estimated_labor_cost', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'task_name', 'task_code', 'model_phase', 'task_type',
            'detailed_description', 'task_objective', 'estimated_duration_hours',
            'execution_order', 'is_mandatory', 'allows_parallel',
            'requires_specialization', 'skill_category', 'required_people',
            'required_skills', 'special_requirements', 'execution_conditions',
            'required_equipment', 'acceptance_criteria', 'identified_risks',
            'safety_measures', 'required_ppe', 'cost_subgroup',
            'estimated_labor_cost', 'is_active', 'version', 'created_at',
            'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'task_name': 'Task Name',
            'task_code': 'Task Code',
            'model_phase': 'Model Phase',
            'task_type': 'Task Type',
            'detailed_description': 'Description',
            'task_objective': 'Objective',
            'estimated_duration_hours': 'Duration (hours)',
            'execution_order': 'Execution Order',
            'is_mandatory': 'Mandatory',
            'allows_parallel': 'Allows Parallel',
            'requires_specialization': 'Requires Specialization',
            'skill_category': 'Skill Category',
            'required_people': 'Required People',
            'required_skills': 'Required Skills',
            'special_requirements': 'Special Requirements',
            'execution_conditions': 'Execution Conditions',
            'required_equipment': 'Required Equipment',
            'acceptance_criteria': 'Acceptance Criteria',
            'identified_risks': 'Identified Risks',
            'safety_measures': 'Safety Measures',
            'required_ppe': 'Required PPE',
            'cost_subgroup': 'Cost SubGroup',
            'estimated_labor_cost': 'Labor Cost',
            'is_active': 'Active',
            'version': 'Version',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="model_tasks_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for task in queryset:
                row = []
                for field in fields:
                    value = getattr(task, field)

                    # Formatação especial para alguns campos
                    if field == 'model_phase' and value:
                        value = value.phase_name
                    elif field == 'cost_subgroup' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Model Tasks')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, task in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(task, field)

                    # Formatação especial para alguns campos
                    if field == 'model_phase' and value:
                        worksheet.write(row, col, value.phase_name)
                    elif field == 'cost_subgroup' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'estimated_labor_cost' and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field in ['created_at', 'updated_at'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif field in ['is_mandatory', 'allows_parallel', 'requires_specialization', 'is_active']:
                        worksheet.write(row, col, 'Yes' if value else 'No')
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="model_tasks_export.xlsx"'

            return response

# Adicionar estas ViewSets ao final do arquivo apps/projects/views.py


class CostGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de grupos de custo

    ENDPOINTS:
    - GET /api/projects/cost-groups/ - Lista grupos de custo com filtros
    - POST /api/projects/cost-groups/ - Criar novo grupo de custo
    - GET /api/projects/cost-groups/{id}/ - Detalhes de grupo de custo
    - PATCH /api/projects/cost-groups/{id}/ - Atualizar grupo de custo
    - DELETE /api/projects/cost-groups/{id}/ - Remover grupo de custo
    - GET /api/projects/cost-groups/{id}/subgroups/ - Listar subgrupos do grupo
    - GET /api/projects/cost-groups/stats/ - Estatísticas de grupos de custo
    """

    queryset = CostGroup.objects.select_related('created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = CostGroupListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'name',
        'description',
    ]

    # Ordenação
    ordering_fields = [
        'name',
        'created_at',
        'updated_at',
    ]
    ordering = ['name']  # Default: ordem alfabética

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar grupos de custo",
        operation_description="Retorna uma lista paginada de grupos de custo com filtros",
        responses={200: CostGroupListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes do grupo de custo",
        operation_description="Retorna detalhes completos de um grupo de custo específico",
        responses={
            200: CostGroupDetailSerializer(),
            404: 'Grupo de custo não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar grupo de custo",
        operation_description="Cria um novo grupo de custo",
        request_body=CostGroupCreateUpdateSerializer,
        responses={
            201: CostGroupDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar grupo de custo",
        operation_description="Atualiza um grupo de custo existente",
        request_body=CostGroupCreateUpdateSerializer,
        responses={
            200: CostGroupDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Grupo de custo não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar grupo de custo parcialmente",
        operation_description="Atualiza parcialmente um grupo de custo existente",
        request_body=CostGroupCreateUpdateSerializer,
        responses={
            200: CostGroupDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Grupo de custo não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir grupo de custo",
        operation_description="Exclui um grupo de custo existente",
        responses={
            204: 'Grupo de custo excluído com sucesso',
            404: 'Grupo de custo não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return CostGroupDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CostGroupCreateUpdateSerializer
        elif self.action == 'subgroups':
            return CostSubGroupListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar subgrupos do grupo",
        operation_description="Retorna uma lista de subgrupos do grupo de custo",
        responses={
            200: CostSubGroupListSerializer(many=True),
            404: 'Grupo de custo não encontrado'
        }
    )
    @action(detail=True, methods=['get'])
    def subgroups(self, request, pk=None):
        """
        Listar subgrupos do grupo
        """
        cost_group = self.get_object()
        subgroups = cost_group.subgroups.all().order_by('name')

        # Aplicar paginação
        page = self.paginate_queryset(subgroups)
        if page is not None:
            serializer = CostSubGroupListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CostSubGroupListSerializer(subgroups, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de grupos de custo",
        operation_description="Retorna estatísticas de grupos de custo",
        responses={200: 'Estatísticas de grupos de custo'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de grupos de custo

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)

        RETURNS:
        - Total de grupos ativos/inativos
        - Grupos com mais subgrupos
        - Estatísticas de valores estimados
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

        # Total de grupos
        total_groups = queryset.count()
        active_groups = queryset.filter(is_active=True).count()

        # Estatísticas de subgrupos
        from django.db.models import Count, Sum
        groups_with_subgroups = queryset.annotate(
            subgroups_count=Count('subgroups'),
            total_estimated_value=Sum('subgroups__value_stimated')
        )

        # Top grupos por número de subgrupos
        top_groups_by_subgroups = groups_with_subgroups.order_by(
            '-subgroups_count')[:5]
        top_groups_data = []
        for group in top_groups_by_subgroups:
            top_groups_data.append({
                'name': group.name,
                'subgroups_count': group.subgroups_count,
                'total_estimated_value': float(group.total_estimated_value or 0)
            })

        # Estatísticas de valores estimados
        total_estimated_value = groups_with_subgroups.aggregate(
            total=Sum('total_estimated_value'))['total'] or 0

        # Montar resposta
        response_data = {
            'total_groups': total_groups,
            'active_groups': active_groups,
            'inactive_groups': total_groups - active_groups,
            'total_subgroups': sum(g.subgroups_count for g in groups_with_subgroups),
            'total_estimated_value': float(total_estimated_value),
            'avg_subgroups_per_group': round(
                sum(g.subgroups_count for g in groups_with_subgroups) / total_groups
                if total_groups > 0 else 0, 2
            ),
            'top_groups_by_subgroups': top_groups_data,
            'period': period,
        }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar grupos de custo",
        operation_description="Exporta grupos de custo para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar grupos de custo para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com grupos filtrados
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'name', 'description', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'name', 'description', 'is_active', 'created_at',
            'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'name': 'Name',
            'description': 'Description',
            'is_active': 'Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="cost_groups_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for group in queryset:
                row = []
                for field in fields:
                    value = getattr(group, field)

                    # Formatação especial para alguns campos
                    if field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Cost Groups')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, group in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(group, field)

                    # Formatação especial para alguns campos
                    if field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field in ['created_at', 'updated_at'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif field == 'is_active':
                        worksheet.write(row, col, 'Yes' if value else 'No')
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="cost_groups_export.xlsx"'

            return response


class CostSubGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de subgrupos de custo

    ENDPOINTS:
    - GET /api/projects/cost-subgroups/ - Lista subgrupos de custo com filtros
    - POST /api/projects/cost-subgroups/ - Criar novo subgrupo de custo
    - GET /api/projects/cost-subgroups/{id}/ - Detalhes de subgrupo de custo
    - PATCH /api/projects/cost-subgroups/{id}/ - Atualizar subgrupo de custo
    - DELETE /api/projects/cost-subgroups/{id}/ - Remover subgrupo de custo
    - GET /api/projects/cost-subgroups/stats/ - Estatísticas de subgrupos de custo
    """

    queryset = CostSubGroup.objects.select_related(
        'cost_group', 'created_by').all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = CostSubGroupListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'cost_group': ['exact'],
        'value_stimated': ['gte', 'lte'],
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'name',
        'description',
        'cost_group__name',
    ]

    # Ordenação
    ordering_fields = [
        'cost_group',
        'name',
        'value_stimated',
        'created_at',
        'updated_at',
    ]
    ordering = ['cost_group', 'name']  # Default: agrupado por grupo de custo

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar subgrupos de custo",
        operation_description="Retorna uma lista paginada de subgrupos de custo com filtros",
        responses={200: CostSubGroupListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes do subgrupo de custo",
        operation_description="Retorna detalhes completos de um subgrupo de custo específico",
        responses={
            200: CostSubGroupDetailSerializer(),
            404: 'Subgrupo de custo não encontrado'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar subgrupo de custo",
        operation_description="Cria um novo subgrupo de custo",
        request_body=CostSubGroupCreateUpdateSerializer,
        responses={
            201: CostSubGroupDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar subgrupo de custo",
        operation_description="Atualiza um subgrupo de custo existente",
        request_body=CostSubGroupCreateUpdateSerializer,
        responses={
            200: CostSubGroupDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Subgrupo de custo não encontrado'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar subgrupo de custo parcialmente",
        operation_description="Atualiza parcialmente um subgrupo de custo existente",
        request_body=CostSubGroupCreateUpdateSerializer,
        responses={
            200: CostSubGroupDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Subgrupo de custo não encontrado'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir subgrupo de custo",
        operation_description="Exclui um subgrupo de custo existente",
        responses={
            204: 'Subgrupo de custo excluído com sucesso',
            404: 'Subgrupo de custo não encontrado'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return CostSubGroupDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CostSubGroupCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Customizar criação - definir created_by"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de subgrupos de custo",
        operation_description="Retorna estatísticas de subgrupos de custo",
        responses={200: 'Estatísticas de subgrupos de custo'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de subgrupos de custo

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)
        - cost_group_id: ID do grupo de custo para filtrar estatísticas

        RETURNS:
        - Total de subgrupos ativos/inativos
        - Estatísticas de valores estimados
        - Distribuição por grupo de custo
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

        # Filtrar por grupo de custo específico
        cost_group_id = request.query_params.get('cost_group_id')
        if cost_group_id:
            queryset = queryset.filter(cost_group_id=cost_group_id)

        # Total de subgrupos
        total_subgroups = queryset.count()
        active_subgroups = queryset.filter(is_active=True).count()

        # Estatísticas de valores
        from django.db.models import Avg, Min, Max, Sum
        value_stats = queryset.aggregate(
            avg_value=Avg('value_stimated'),
            min_value=Min('value_stimated'),
            max_value=Max('value_stimated'),
            total_value=Sum('value_stimated'),
        )

        # Distribuição por faixas de valor
        value_ranges = [
            {'min': 0, 'max': 1000, 'label': '$0-$1,000'},
            {'min': 1000, 'max': 5000, 'label': '$1,000-$5,000'},
            {'min': 5000, 'max': 10000, 'label': '$5,000-$10,000'},
            {'min': 10000, 'max': 50000, 'label': '$10,000-$50,000'},
            {'min': 50000, 'max': None, 'label': '$50,000+'}
        ]

        value_distribution = []
        for range_info in value_ranges:
            min_value = range_info['min']
            max_value = range_info['max']

            if max_value:
                count = queryset.filter(
                    value_stimated__gte=min_value,
                    value_stimated__lt=max_value
                ).count()
            else:
                count = queryset.filter(
                    value_stimated__gte=min_value
                ).count()

            value_distribution.append({
                'range': range_info['label'],
                'count': count,
                'percentage': round((count / total_subgroups * 100) if total_subgroups > 0 else 0, 1)
            })

        # Estatísticas por grupo de custo
        cost_group_stats = {}
        cost_groups = CostGroup.objects.all()
        if cost_group_id:
            cost_groups = cost_groups.filter(id=cost_group_id)

        for cost_group in cost_groups:
            group_subgroups = queryset.filter(cost_group=cost_group)
            group_total = group_subgroups.count()

            if group_total > 0:
                group_value_total = group_subgroups.aggregate(
                    total=Sum('value_stimated'))['total'] or 0

                cost_group_stats[cost_group.name] = {
                    'total_subgroups': group_total,
                    'active_subgroups': group_subgroups.filter(is_active=True).count(),
                    'total_estimated_value': float(group_value_total),
                    'avg_estimated_value': float(group_value_total / group_total),
                }

        # Montar resposta
        response_data = {
            'total_subgroups': total_subgroups,
            'active_subgroups': active_subgroups,
            'inactive_subgroups': total_subgroups - active_subgroups,
            'value_stats': {
                'avg_value': float(value_stats['avg_value'] or 0),
                'min_value': float(value_stats['min_value'] or 0),
                'max_value': float(value_stats['max_value'] or 0),
                'total_value': float(value_stats['total_value'] or 0),
            },
            'value_distribution': value_distribution,
            'cost_group_stats': cost_group_stats,
            'period': period,
        }

        # Adicionar informações do filtro
        if cost_group_id:
            cost_group = CostGroup.objects.filter(id=cost_group_id).first()
            if cost_group:
                response_data['filtered_by_cost_group'] = {
                    'id': cost_group.id,
                    'name': cost_group.name
                }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar subgrupos de custo",
        operation_description="Exporta subgrupos de custo para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar subgrupos de custo para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com subgrupos filtrados
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'name', 'cost_group', 'value_stimated', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'name', 'cost_group', 'description', 'value_stimated',
            'is_active', 'created_at', 'updated_at', 'created_by'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'name': 'Name',
            'cost_group': 'Cost Group',
            'description': 'Description',
            'value_stimated': 'Estimated Value',
            'is_active': 'Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'created_by': 'Created By'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="cost_subgroups_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for subgroup in queryset:
                row = []
                for field in fields:
                    value = getattr(subgroup, field)

                    # Formatação especial para alguns campos
                    if field == 'cost_group' and value:
                        value = value.name
                    elif field == 'created_by' and value:
                        value = value.get_full_name() or value.username
                    elif field in ['created_at', 'updated_at'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Cost SubGroups')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, subgroup in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(subgroup, field)

                    # Formatação especial para alguns campos
                    if field == 'cost_group' and value:
                        worksheet.write(row, col, value.name)
                    elif field == 'created_by' and value:
                        worksheet.write(
                            row, col, value.get_full_name() or value.username)
                    elif field == 'value_stimated' and value:
                        worksheet.write(row, col, float(
                            value), currency_format)
                    elif field in ['created_at', 'updated_at'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif field == 'is_active':
                        worksheet.write(row, col, 'Yes' if value else 'No')
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="cost_subgroups_export.xlsx"'

            return response


class ProductionCellViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de células de produção

    ENDPOINTS:
    - GET /api/projects/production-cells/ - Lista células de produção com filtros
    - POST /api/projects/production-cells/ - Criar nova célula de produção
    - GET /api/projects/production-cells/{id}/ - Detalhes de célula de produção
    - PATCH /api/projects/production-cells/{id}/ - Atualizar célula de produção
    - DELETE /api/projects/production-cells/{id}/ - Remover célula de produção
    - GET /api/projects/production-cells/stats/ - Estatísticas de células de produção
    """

    queryset = ProductionCell.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ProductionCellListSerializer

    # Filtros disponíveis
    filterset_fields = {
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    # Campos de busca
    search_fields = [
        'name',
        'code',
        'description',
    ]

    # Ordenação
    ordering_fields = [
        'name',
        'code',
        'order',
        'created_at',
        'updated_at',
    ]
    ordering = ['order', 'name']  # Default: por ordem definida

    def get_permissions(self):
        """Permissões por ação"""
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar células de produção",
        operation_description="Retorna uma lista paginada de células de produção com filtros",
        responses={200: ProductionCellListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Detalhes da célula de produção",
        operation_description="Retorna detalhes completos de uma célula de produção específica",
        responses={
            200: ProductionCellDetailSerializer(),
            404: 'Célula de produção não encontrada'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Criar célula de produção",
        operation_description="Cria uma nova célula de produção",
        request_body=ProductionCellCreateUpdateSerializer,
        responses={
            201: ProductionCellDetailSerializer(),
            400: 'Dados inválidos'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar célula de produção",
        operation_description="Atualiza uma célula de produção existente",
        request_body=ProductionCellCreateUpdateSerializer,
        responses={
            200: ProductionCellDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Célula de produção não encontrada'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Atualizar célula de produção parcialmente",
        operation_description="Atualiza parcialmente uma célula de produção existente",
        request_body=ProductionCellCreateUpdateSerializer,
        responses={
            200: ProductionCellDetailSerializer(),
            400: 'Dados inválidos',
            404: 'Célula de produção não encontrada'
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Excluir célula de produção",
        operation_description="Exclui uma célula de produção existente",
        responses={
            204: 'Célula de produção excluída com sucesso',
            404: 'Célula de produção não encontrada'
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna o serializer apropriado com base na ação"""
        if self.action == 'retrieve':
            return ProductionCellDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductionCellCreateUpdateSerializer
        return self.serializer_class

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de células de produção",
        operation_description="Retorna estatísticas de células de produção",
        responses={200: 'Estatísticas de células de produção'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas de células de produção

        QUERY PARAMS:
        - period: Período para filtrar estatísticas (today, week, month, quarter, year, all)

        RETURNS:
        - Total de células ativas/inativas
        - Células mais utilizadas em projetos
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

        # Total de células
        total_cells = queryset.count()
        active_cells = queryset.filter(is_active=True).count()

        # Células mais utilizadas (assumindo que há projetos relacionados)
        from django.db.models import Count
        try:
            cells_with_projects = queryset.annotate(
                projects_count=Count('projects')
            ).order_by('-projects_count')

            most_used_cells = []
            for cell in cells_with_projects[:5]:
                most_used_cells.append({
                    'name': cell.name,
                    'code': cell.code,
                    'projects_count': cell.projects_count
                })
        except:
            # Se não houver relacionamento com projetos ainda
            most_used_cells = []

        # Montar resposta
        response_data = {
            'total_cells': total_cells,
            'active_cells': active_cells,
            'inactive_cells': total_cells - active_cells,
            'most_used_cells': most_used_cells,
            'period': period,
        }

        return Response(response_data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Exportar células de produção",
        operation_description="Exporta células de produção para CSV ou Excel",
        responses={
            200: 'Arquivo para download',
            400: 'Formato inválido'
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar células de produção para CSV ou Excel

        QUERY PARAMS:
        - format: Formato de exportação (csv, excel) - default: csv
        - include_all: Incluir todos os campos (true, false) - default: false
        - Todos os filtros disponíveis na listagem normal

        RETURNS:
        - Arquivo para download com células filtradas
        """
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
            'include_all', 'false').lower() == 'true'

        # Definir campos básicos e completos
        basic_fields = [
            'id', 'name', 'code', 'order', 'is_active', 'created_at'
        ]

        all_fields = [
            'id', 'name', 'code', 'description', 'color', 'icon',
            'order', 'is_active', 'created_at', 'updated_at'
        ]

        # Escolher campos com base no parâmetro
        fields = all_fields if include_all else basic_fields

        # Preparar cabeçalhos para exibição
        headers = {
            'id': 'ID',
            'name': 'Name',
            'code': 'Code',
            'description': 'Description',
            'color': 'Color',
            'icon': 'Icon',
            'order': 'Order',
            'is_active': 'Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At'
        }

        # Exportar como CSV
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="production_cells_export.csv"'

            writer = csv.writer(response)

            # Escrever cabeçalho
            writer.writerow([headers[field] for field in fields])

            # Escrever dados
            for cell in queryset:
                row = []
                for field in fields:
                    value = getattr(cell, field)

                    # Formatação especial para alguns campos
                    if field in ['created_at', 'updated_at'] and value:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')

                    row.append(str(value) if value is not None else '')

                writer.writerow(row)

            return response

        # Exportar como Excel
        elif export_format == 'excel':
            # Criar buffer para o arquivo Excel
            output = io.BytesIO()

            # Criar workbook e worksheet
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Production Cells')

            # Adicionar formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F7F7F7',
                'border': 1
            })

            date_format = workbook.add_format(
                {'num_format': 'yyyy-mm-dd hh:mm:ss'})

            # Escrever cabeçalho
            for col, field in enumerate(fields):
                worksheet.write(0, col, headers[field], header_format)

            # Escrever dados
            for row, cell in enumerate(queryset, start=1):
                for col, field in enumerate(fields):
                    value = getattr(cell, field)

                    # Formatação especial para alguns campos
                    if field in ['created_at', 'updated_at'] and value:
                        worksheet.write_datetime(row, col, value, date_format)
                    elif field == 'is_active':
                        worksheet.write(row, col, 'Yes' if value else 'No')
                    elif value is None:
                        worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, value)

            # Ajustar largura das colunas
            for col, field in enumerate(fields):
                worksheet.set_column(col, col, 15)  # Largura padrão

            # Fechar workbook
            workbook.close()

            # Preparar resposta
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="production_cells_export.xlsx"'

            return response


# =====================================================
# CHOICE TYPES VIEWSETS
# =====================================================

class ProjectTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de tipos de projeto

    ENDPOINTS:
    - GET /api/projects/project-types/ - Lista tipos de projeto
    - POST /api/projects/project-types/ - Criar novo tipo
    - GET /api/projects/project-types/{id}/ - Detalhes do tipo
    - PATCH /api/projects/project-types/{id}/ - Atualizar tipo
    - DELETE /api/projects/project-types/{id}/ - Remover tipo
    - GET /api/projects/project-types/stats/ - Estatísticas
    """

    queryset = ProjectType.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTypeListSerializer

    filterset_fields = {
        'is_active': ['exact'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order', 'created_at']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar tipos de projeto",
        responses={200: ProjectTypeListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectTypeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectTypeCreateUpdateSerializer
        return self.serializer_class

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de tipos de projeto",
        responses={200: 'Estatísticas de tipos de projeto'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()

        total_types = queryset.count()
        active_types = queryset.filter(is_active=True).count()

        # Tipos mais utilizados em projetos
        from django.db.models import Count
        most_used = queryset.annotate(
            projects_count=Count('model_projects')
        ).order_by('-projects_count')[:5]

        most_used_data = [
            {
                'name': pt.name,
                'code': pt.code,
                'projects_count': pt.projects_count
            }
            for pt in most_used
        ]

        return Response({
            'total_types': total_types,
            'active_types': active_types,
            'inactive_types': total_types - active_types,
            'most_used_types': most_used_data,
        })


class ProjectStatusViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de status de projeto"""

    queryset = ProjectStatus.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectStatusListSerializer

    filterset_fields = {'is_active': ['exact']}
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectStatusDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectStatusCreateUpdateSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()

        total_status = queryset.count()
        active_status = queryset.filter(is_active=True).count()

        # Status mais utilizados
        from django.db.models import Count
        most_used = queryset.annotate(
            projects_count=Count('projects')
        ).order_by('-projects_count')[:5]

        most_used_data = [
            {
                'name': ps.name,
                'code': ps.code,
                'projects_count': ps.projects_count
            }
            for ps in most_used
        ]

        return Response({
            'total_status': total_status,
            'active_status': active_status,
            'most_used_status': most_used_data,
        })


class IncorporationTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de tipos de incorporação"""

    queryset = IncorporationType.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = IncorporationTypeListSerializer

    filterset_fields = {'is_active': ['exact']}
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IncorporationTypeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return IncorporationTypeCreateUpdateSerializer
        return self.serializer_class


class IncorporationStatusViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de status de incorporação"""

    queryset = IncorporationStatus.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = IncorporationStatusListSerializer

    filterset_fields = {'is_active': ['exact']}
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IncorporationStatusDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return IncorporationStatusCreateUpdateSerializer
        return self.serializer_class


class StatusContractViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de status de contrato"""

    queryset = StatusContract.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = StatusContractListSerializer

    filterset_fields = {'is_active': ['exact']}
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StatusContractDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return StatusContractCreateUpdateSerializer
        return self.serializer_class


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de métodos de pagamento"""

    queryset = PaymentMethod.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = PaymentMethodListSerializer

    filterset_fields = {'is_active': ['exact']}
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PaymentMethodDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PaymentMethodCreateUpdateSerializer
        return self.serializer_class


class OwnerTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de tipos de proprietário"""

    queryset = OwnerType.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = OwnerTypeListSerializer

    filterset_fields = {'is_active': ['exact']}
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'order']
    ordering = ['order', 'name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OwnerTypeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OwnerTypeCreateUpdateSerializer
        return self.serializer_class


# =====================================================
# CONTRACT MANAGEMENT VIEWSETS
# =====================================================

class ContractOwnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de proprietários de contratos

    ENDPOINTS:
    - GET /api/projects/contract-owners/ - Lista proprietários com filtros
    - POST /api/projects/contract-owners/ - Criar novo proprietário
    - GET /api/projects/contract-owners/{id}/ - Detalhes de proprietário
    - PATCH /api/projects/contract-owners/{id}/ - Atualizar proprietário
    - DELETE /api/projects/contract-owners/{id}/ - Remover proprietário
    - GET /api/projects/contract-owners/by-contract/{contract_id}/ - Por contrato
    - GET /api/projects/contract-owners/by-client/{client_id}/ - Por cliente
    - GET /api/projects/contract-owners/stats/ - Estatísticas
    """

    queryset = ContractOwner.objects.select_related(
        'contract', 'client', 'owner_type', 'created_by'
    ).all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ContractOwnerListSerializer

    filterset_fields = {
        'contract': ['exact'],
        'client': ['exact'],
        'owner_type': ['exact'],
        'percentual_propriedade': ['gte', 'lte'],
        'valor_participacao': ['gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    search_fields = [
        'client__first_name',
        'client__last_name',
        'client__email',
        'contract__contract_number',
        'observations',
    ]

    ordering_fields = [
        'created_at',
        'percentual_propriedade',
        'valor_participacao',
        'client__first_name',
        'contract__contract_number',
    ]
    ordering = ['-created_at']

    def get_permissions(self):
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar proprietários de contratos",
        responses={200: ContractOwnerListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContractOwnerDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ContractOwnerCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar proprietários por contrato",
        responses={200: ContractOwnerListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-contract/(?P<contract_id>[^/.]+)')
    def by_contract(self, request, contract_id=None):
        owners = self.get_queryset().filter(contract_id=contract_id)

        page = self.paginate_queryset(owners)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(owners, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Listar proprietários por cliente",
        responses={200: ContractOwnerListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-client/(?P<client_id>[^/.]+)')
    def by_client(self, request, client_id=None):
        owners = self.get_queryset().filter(client_id=client_id)

        page = self.paginate_queryset(owners)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(owners, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['PROJECTS']],
        operation_summary="Estatísticas de proprietários",
        responses={200: 'Estatísticas de proprietários'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()

        total_owners = queryset.count()

        # Contadores por tipo
        type_counts = {}
        for owner_type in OwnerType.objects.all():
            type_counts[owner_type.code] = queryset.filter(
                owner_type=owner_type
            ).count()

        # Estatísticas de valores
        from django.db.models import Avg, Sum
        value_stats = queryset.aggregate(
            avg_participation=Avg('valor_participacao'),
            total_participation=Sum('valor_participacao'),
            avg_percentage=Avg('percentual_propriedade'),
        )

        # Top clientes por número de contratos
        from django.db.models import Count
        top_clients = queryset.values(
            'client__first_name', 'client__last_name', 'client__email'
        ).annotate(
            contracts_count=Count('contract', distinct=True)
        ).order_by('-contracts_count')[:5]

        return Response({
            'total_owners': total_owners,
            'type_counts': type_counts,
            'value_stats': {
                'avg_participation': float(value_stats['avg_participation'] or 0),
                'total_participation': float(value_stats['total_participation'] or 0),
                'avg_percentage': float(value_stats['avg_percentage'] or 0),
            },
            'top_clients': list(top_clients),
        })


class ContractProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de projetos de contratos

    ENDPOINTS:
    - GET /api/projects/contract-projects/ - Lista projetos de contratos
    - POST /api/projects/contract-projects/ - Vincular projeto a contrato
    - GET /api/projects/contract-projects/{id}/ - Detalhes da vinculação
    - PATCH /api/projects/contract-projects/{id}/ - Atualizar vinculação
    - DELETE /api/projects/contract-projects/{id}/ - Remover vinculação
    - GET /api/projects/contract-projects/by-contract/{contract_id}/ - Por contrato
    - GET /api/projects/contract-projects/by-project/{project_id}/ - Por projeto
    - GET /api/projects/contract-projects/stats/ - Estatísticas
    """

    queryset = ContractProject.objects.select_related(
        'contract', 'project', 'created_by'
    ).all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = ContractProjectListSerializer

    filterset_fields = {
        'contract': ['exact'],
        'project': ['exact'],
        'preco_venda_unidade': ['gte', 'lte'],
        'data_vinculacao': ['exact', 'gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
    }

    search_fields = [
        'contract__contract_number',
        'project__project_name',
        'observacoes_especificas',
        'condicoes_especiais',
    ]

    ordering_fields = [
        'data_vinculacao',
        'preco_venda_unidade',
        'created_at',
        'contract__contract_number',
        'project__project_name',
    ]
    ordering = ['-data_vinculacao']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContractProjectDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ContractProjectCreateUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # serializer.save(created_by=self.request.user) #removido, nao tem createdby
        serializer.save()

    @action(detail=False, methods=['get'], url_path='by-contract/(?P<contract_id>[^/.]+)')
    def by_contract(self, request, contract_id=None):
        contract_projects = self.get_queryset().filter(contract_id=contract_id)

        page = self.paginate_queryset(contract_projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(contract_projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-project/(?P<project_id>[^/.]+)')
    def by_project(self, request, project_id=None):
        contract_projects = self.get_queryset().filter(project_id=project_id)

        page = self.paginate_queryset(contract_projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(contract_projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()

        total_links = queryset.count()

        # Estatísticas de valores
        from django.db.models import Avg, Sum, Min, Max
        value_stats = queryset.aggregate(
            avg_price=Avg('preco_venda_unidade'),
            total_value=Sum('preco_venda_unidade'),
            min_price=Min('preco_venda_unidade'),
            max_price=Max('preco_venda_unidade'),
        )

        # Contratos com mais projetos
        from django.db.models import Count
        top_contracts = queryset.values(
            'contract__contract_number', 'contract__id'
        ).annotate(
            projects_count=Count('project')
        ).order_by('-projects_count')[:5]

        return Response({
            'total_links': total_links,
            'value_stats': {
                'avg_price': float(value_stats['avg_price'] or 0),
                'total_value': float(value_stats['total_value'] or 0),
                'min_price': float(value_stats['min_price'] or 0),
                'max_price': float(value_stats['max_price'] or 0),
            },
            'top_contracts': list(top_contracts),
        })


# =====================================================
# TASK RESOURCES VIEWSET
# =====================================================

class TaskResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de recursos de tarefas

    ENDPOINTS:
    - GET /api/projects/task-resources/ - Lista recursos com filtros
    - POST /api/projects/task-resources/ - Criar novo recurso
    - GET /api/projects/task-resources/{id}/ - Detalhes de recurso
    - PATCH /api/projects/task-resources/{id}/ - Atualizar recurso
    - DELETE /api/projects/task-resources/{id}/ - Remover recurso
    - GET /api/projects/task-resources/by-task/{task_id}/ - Por tarefa
    - GET /api/projects/task-resources/stats/ - Estatísticas
    """

    # Assumindo que TaskResource será criado como modelo
    queryset = None  # Será definido quando o modelo for criado
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPageNumberPagination
    serializer_class = None  # Será definido no serializers.py

    def get_permissions(self):
        return [IsAuthenticated()]


__all__ = [
    'IncorporationViewSet',
    'ContractViewSet',
    'ProjectViewSet',
    'PhaseProjectViewSet',
    'TaskProjectViewSet',
    'ContactViewSet',
    'ModelProjectViewSet',    # NOVO
    'ModelPhaseViewSet',      # NOVO
    'ModelTaskViewSet',       # NOVO
    'CostGroupViewSet',      # NOVO
    'CostSubGroupViewSet',   # NOVO
    'ProductionCellViewSet'  # NOVO
    # NOVAS VIEWSETS
    'ProjectTypeViewSet',
    'ProjectStatusViewSet',
    'IncorporationTypeViewSet',
    'IncorporationStatusViewSet',
    'StatusContractViewSet',
    'PaymentMethodViewSet',
    'OwnerTypeViewSet',
    'ContractOwnerViewSet',
    'ContractProjectViewSet'  # ,
    # 'TaskResourceViewSet',
]
