# apps/projects/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models.incorporation import Incorporation
from ..contracts.models.contract import Contract
from .models.project import Project
from .models.phase_project import PhaseProject
from .models.task_project import TaskProject
from .models.contact import Contact
from ..contracts.models.contract_owner import ContractOwner
from .models.contract_project import ContractProject
from .models.model_project import ModelProject
from .models.model_phase import ModelPhase
from .models.model_task import ModelTask
from .models.choice_types import (
    ProjectType, ProjectStatus, IncorporationType, IncorporationStatus,
    StatusContract, PaymentMethod, ProductionCell, OwnerType
)
from .models.cost_group import CostGroup
from .models.cost_subgroup import CostSubGroup
from .models.choice_types import ProductionCell

from django.db.models import Sum  # Para validações de percentual

User = get_user_model()


# Serializers para Choice Types
class ChoiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'code', 'name', 'color', 'icon', 'order', 'is_active']


class ProjectTypeSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = ProjectType


class ProjectStatusSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = ProjectStatus


class IncorporationTypeSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = IncorporationType


class IncorporationStatusSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = IncorporationStatus


class StatusContractSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = StatusContract


class PaymentMethodSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = PaymentMethod


class ProductionCellSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = ProductionCell


class OwnerTypeSerializer(ChoiceTypeSerializer):
    class Meta(ChoiceTypeSerializer.Meta):
        model = OwnerType


# User Serializer (simplificado)
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'is_active']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


# Serializers para Incorporation
class IncorporationListSerializer(serializers.ModelSerializer):
    incorporation_type_name = serializers.CharField(
        source='incorporation_type.name', read_only=True)
    incorporation_status_name = serializers.CharField(
        source='incorporation_status.name', read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Incorporation
        fields = [
            'id', 'name', 'incorporation_type', 'incorporation_type_name',
            'incorporation_status', 'incorporation_status_name',
            'county', 'county_name', 'launch_date', 'is_active',
            'total_projects', 'projects_sold', 'sold_percentage',
            'created_by', 'created_by_name', 'created_at'
        ]


class IncorporationDetailSerializer(serializers.ModelSerializer):
    incorporation_type = IncorporationTypeSerializer(read_only=True)
    incorporation_status = IncorporationStatusSerializer(read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Incorporation
        fields = [
            'id', 'name', 'incorporation_type', 'incorporation_status',
            'county', 'county_name', 'project_description', 'launch_date',
            'is_active', 'total_projects', 'projects_sold', 'sold_percentage',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at',
                            'total_projects', 'projects_sold', 'sold_percentage']


class IncorporationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incorporation
        fields = [
            'name', 'incorporation_type', 'incorporation_status',
            'county', 'project_description', 'launch_date', 'is_active'
        ]


# Serializers para Contract
class ContractListSerializer(serializers.ModelSerializer):
    incorporation_name = serializers.CharField(
        source='incorporation.name', read_only=True)
    status_contract_name = serializers.CharField(
        source='status_contract.name', read_only=True)
    payment_method_name = serializers.CharField(
        source='payment_method.name', read_only=True)
    lead_name = serializers.CharField(
        source='lead.client_full_name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'incorporation', 'incorporation_name',
            'lead', 'lead_name', 'contract_value', 'status_contract',
            'status_contract_name', 'payment_method', 'payment_method_name',
            'sign_date', 'payment_date', 'management_company',
            'total_owners', 'total_projects', 'created_by', 'created_by_name',
            'created_at'
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    incorporation = IncorporationListSerializer(read_only=True)
    status_contract = StatusContractSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'incorporation', 'lead',
            'contract_value', 'status_contract', 'payment_method',
            'sign_date', 'payment_date', 'management_company',
            'total_owners', 'total_projects', 'valor_medio_projeto',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at',
                            'total_owners', 'total_projects', 'valor_medio_projeto', 'contract_value']


class ContractCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'incorporation', 'lead',
            'status_contract', 'payment_method',
            'sign_date', 'payment_date', 'management_company'
        ]


# Serializers para ContractOwner
class ContractOwnerSerializer(serializers.ModelSerializer):
    owner_type_name = serializers.CharField(
        source='owner_type.name', read_only=True)
    client_name = serializers.CharField(
        source='client.get_full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    contract_number = serializers.CharField(
        source='contract.contract_number', read_only=True)

    class Meta:
        model = ContractOwner
        fields = [
            'id', 'contract', 'contract_number', 'client', 'client_name',
            'client_email', 'owner_type', 'owner_type_name',
            'percentual_propriedade', 'valor_participacao',
            'observations', 'created_at'
        ]
        read_only_fields = ['created_at', 'valor_participacao']


# Serializers para ContractProject
class ContractProjectSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source='project.project_name', read_only=True)
    contract_number = serializers.CharField(
        source='contract.contract_number', read_only=True)

    class Meta:
        model = ContractProject
        fields = [
            'id', 'contract', 'contract_number', 'project', 'project_name',
            'preco_venda_unidade', 'data_vinculacao',
            'observacoes_especificas', 'condicoes_especiais'
        ]
        read_only_fields = ['data_vinculacao']


# Serializers para Project
class ProjectListSerializer(serializers.ModelSerializer):
    incorporation_name = serializers.CharField(
        source='incorporation.name', read_only=True)
    model_project_name = serializers.CharField(
        source='model_project.name', read_only=True)
    status_project_name = serializers.CharField(
        source='status_project.name', read_only=True)
    production_cell_name = serializers.CharField(
        source='production_cell.name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'incorporation', 'incorporation_name',
            'model_project', 'model_project_name', 'status_project',
            'status_project_name', 'production_cell', 'production_cell_name',
            'address', 'area_total', 'completion_percentage',
            'expected_delivery_date', 'is_sold', 'is_delayed',
            'sale_value', 'created_by', 'created_by_name', 'created_at'
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    incorporation = IncorporationListSerializer(read_only=True)
    status_project = ProjectStatusSerializer(read_only=True)
    production_cell = ProductionCellSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'incorporation', 'model_project',
            'status_project', 'production_cell', 'address', 'area_total',
            'completion_percentage', 'expected_delivery_date', 'is_delayed',
            'construction_cost', 'project_value', 'sale_value', 'cost_variance',
            'observations', 'is_sold', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at',
                            'updated_at', 'is_sold', 'is_delayed', 'cost_variance']


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_name', 'incorporation', 'model_project',
            'status_project', 'production_cell', 'address', 'area_total',
            'completion_percentage', 'expected_delivery_date',
            'construction_cost', 'project_value', 'sale_value',
            'observations'
        ]


# Serializers para PhaseProject
class PhaseProjectListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source='project.project_name', read_only=True)
    model_phase_name = serializers.CharField(
        source='model_phase.phase_name', read_only=True)
    technical_responsible_name = serializers.CharField(
        source='technical_responsible.get_full_name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PhaseProject
        fields = [
            'id', 'phase_name', 'phase_code', 'project', 'project_name',
            'model_phase', 'model_phase_name', 'phase_status', 'priority',
            'execution_order', 'completion_percentage', 'planned_start_date',
            'planned_end_date', 'actual_start_date', 'actual_end_date',
            'technical_responsible', 'technical_responsible_name',
            'is_delayed', 'total_tasks', 'completed_tasks',
            'created_by', 'created_by_name', 'created_at'
        ]


class PhaseProjectDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    technical_responsible = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = PhaseProject
        fields = [
            'id', 'phase_name', 'phase_code', 'project', 'model_phase',
            'phase_status', 'priority', 'execution_order', 'completion_percentage',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'technical_responsible', 'supervisor',
            'estimated_cost', 'actual_cost', 'requires_inspection',
            'inspection_result', 'inspection_notes', 'inspection_scheduled_date',
            'is_delayed', 'total_tasks', 'completed_tasks',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at',
                            'is_delayed', 'total_tasks', 'completed_tasks']


class PhaseProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhaseProject
        fields = [
            'phase_name', 'phase_code', 'project', 'model_phase',
            'phase_status', 'priority', 'execution_order', 'completion_percentage',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'technical_responsible', 'supervisor',
            'estimated_cost', 'actual_cost', 'requires_inspection',
            'inspection_result', 'inspection_notes', 'inspection_scheduled_date'
        ]


# Serializers para TaskProject
class TaskProjectListSerializer(serializers.ModelSerializer):
    phase_project_name = serializers.CharField(
        source='phase_project.phase_name', read_only=True)
    model_task_name = serializers.CharField(
        source='model_task.task_name', read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TaskProject
        fields = [
            'id', 'task_name', 'task_code', 'phase_project', 'phase_project_name',
            'model_task', 'model_task_name', 'task_status', 'priority',
            'execution_order', 'completion_percentage', 'planned_start_date',
            'planned_end_date', 'actual_start_date', 'actual_end_date',
            'assigned_to', 'assigned_to_name', 'is_delayed',
            'created_by', 'created_by_name', 'created_at'
        ]


class TaskProjectDetailSerializer(serializers.ModelSerializer):
    phase_project = PhaseProjectListSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    supervisor = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = TaskProject
        fields = [
            'id', 'task_name', 'task_code', 'phase_project', 'model_task',
            'task_description', 'task_status', 'priority', 'execution_order',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'estimated_duration_hours', 'actual_duration_hours',
            'assigned_to', 'supervisor', 'team_members', 'completion_percentage',
            'quality_rating', 'estimated_cost', 'actual_cost', 'cost_variance',
            'notes', 'issues_found', 'solutions_applied', 'lessons_learned',
            'requires_approval', 'approved_by', 'approval_date', 'approval_notes',
            'specific_location', 'weather_conditions', 'is_delayed',
            'total_specifications', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_by', 'created_at', 'updated_at', 'is_delayed',
            'cost_variance', 'total_specifications'
        ]


class TaskProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskProject
        fields = [
            'task_name', 'task_code', 'phase_project', 'model_task',
            'task_description', 'task_status', 'priority', 'execution_order',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'estimated_duration_hours', 'actual_duration_hours',
            'assigned_to', 'supervisor', 'team_members', 'completion_percentage',
            'quality_rating', 'estimated_cost', 'actual_cost',
            'notes', 'issues_found', 'solutions_applied', 'lessons_learned',
            'requires_approval', 'approved_by', 'approval_date', 'approval_notes',
            'specific_location', 'weather_conditions'
        ]


# Serializers para Contact
class ContactListSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(
        source='contact.get_full_name', read_only=True)
    contact_email = serializers.CharField(
        source='contact.email', read_only=True)
    project_name = serializers.CharField(
        source='project.project_name', read_only=True)
    owner_name = serializers.SerializerMethodField()
    contact_role_display = serializers.CharField(
        source='get_contact_role_display', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'contact', 'contact_name', 'contact_email',
            'project', 'project_name', 'owner', 'owner_name',
            'contact_role', 'contact_role_display', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]

    def get_owner_name(self, obj):
        if obj.owner and obj.owner.client:
            return obj.owner.client.get_full_name()
        return ''


class ContactDetailSerializer(serializers.ModelSerializer):
    contact = UserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    owner = ContractOwnerSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    contact_role_display = serializers.CharField(
        source='get_contact_role_display', read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'contact', 'project', 'owner',
            'contact_role', 'contact_role_display', 'is_active',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ContactCreateUpdateSerializer(serializers.ModelSerializer):
    id_client = serializers.IntegerField(source='contact', write_only=True)

    class Meta:
        model = Contact
        fields = [
            'id_client',  # ← Usar o nome amigável
            'project', 'owner',
            'contact_role', 'is_active'
        ]
        extra_kwargs = {
            'id_client': {
                'help_text': 'ID do cliente/usuário que será o contato do projeto',
                'required': True
            }
        }


# Serializers para ModelProject
class ModelProjectListSerializer(serializers.ModelSerializer):
    project_type_name = serializers.CharField(
        source='project_type.name', read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ModelProject
        fields = [
            'id', 'name', 'code', 'project_type', 'project_type_name',
            'county', 'county_name', 'builders_fee', 'area_construida_padrao',
            'custo_base_estimado', 'custo_por_m2', 'duracao_construcao_dias',
            'versao', 'is_active', 'created_by', 'created_by_name', 'created_at'
        ]


class ModelProjectDetailSerializer(serializers.ModelSerializer):
    project_type = ProjectTypeSerializer(read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ModelProject
        fields = [
            'id', 'name', 'code', 'project_type', 'county', 'county_name',
            'builders_fee', 'area_construida_padrao', 'especificacoes_padrao',
            'custo_base_estimado', 'custo_por_m2', 'duracao_construcao_dias',
            'requisitos_especiais', 'regulamentacoes_county', 'versao',
            'is_active', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ModelProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelProject
        fields = [
            'name', 'code', 'project_type', 'county', 'builders_fee',
            'area_construida_padrao', 'especificacoes_padrao',
            'custo_base_estimado', 'custo_por_m2', 'duracao_construcao_dias',
            'requisitos_especiais', 'regulamentacoes_county', 'versao',
            'is_active'
        ]


# Serializers para ModelPhase
class ModelPhaseListSerializer(serializers.ModelSerializer):
    project_model_name = serializers.CharField(
        source='project_model.name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ModelPhase
        fields = [
            'id', 'phase_name', 'phase_code', 'project_model', 'project_model_name',
            'execution_order', 'estimated_duration_days', 'is_mandatory',
            'allows_parallel', 'requires_inspection', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]


class ModelPhaseDetailSerializer(serializers.ModelSerializer):
    project_model = ModelProjectListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ModelPhase
        fields = [
            'id', 'phase_name', 'phase_code', 'project_model',
            'phase_description', 'phase_objectives', 'execution_order',
            'estimated_duration_days', 'is_mandatory', 'allows_parallel',
            'requires_inspection', 'initial_requirements', 'completion_criteria',
            'deliverables', 'is_active', 'version', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ModelPhaseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPhase
        fields = [
            'phase_name', 'phase_code', 'project_model', 'phase_description',
            'phase_objectives', 'execution_order', 'estimated_duration_days',
            'is_mandatory', 'allows_parallel', 'requires_inspection',
            'initial_requirements', 'completion_criteria', 'deliverables',
            'is_active', 'version'
        ]


# Serializers para ModelTask
class ModelTaskListSerializer(serializers.ModelSerializer):
    model_phase_name = serializers.CharField(
        source='model_phase.phase_name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ModelTask
        fields = [
            'id', 'task_name', 'task_code', 'model_phase', 'model_phase_name',
            'task_type', 'estimated_duration_hours', 'execution_order',
            'is_mandatory', 'allows_parallel', 'requires_specialization',
            'skill_category', 'required_people', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]


class ModelTaskDetailSerializer(serializers.ModelSerializer):
    model_phase = ModelPhaseListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ModelTask
        fields = [
            'id', 'task_name', 'task_code', 'model_phase', 'task_type',
            'detailed_description', 'task_objective', 'estimated_duration_hours',
            'execution_order', 'is_mandatory', 'allows_parallel',
            'requires_specialization', 'skill_category', 'required_people',
            'required_skills', 'special_requirements', 'execution_conditions',
            'required_equipment', 'acceptance_criteria', 'checkpoints',
            'identified_risks', 'safety_measures', 'required_ppe',
            'cost_subgroup', 'estimated_labor_cost', 'is_active',
            'version', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ModelTaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTask
        fields = [
            'task_name', 'task_code', 'model_phase', 'task_type',
            'detailed_description', 'task_objective', 'estimated_duration_hours',
            'execution_order', 'is_mandatory', 'allows_parallel',
            'requires_specialization', 'skill_category', 'required_people',
            'required_skills', 'special_requirements', 'execution_conditions',
            'required_equipment', 'acceptance_criteria', 'checkpoints',
            'identified_risks', 'safety_measures', 'required_ppe',
            'cost_subgroup', 'estimated_labor_cost', 'is_active',
            'version'
        ]


class CostGroupListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)
    total_subgroups = serializers.ReadOnlyField()

    class Meta:
        model = CostGroup
        fields = [
            'id', 'name', 'description', 'is_active',
            'total_subgroups', 'created_by', 'created_by_name', 'created_at'
        ]


class CostGroupDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    total_subgroups = serializers.ReadOnlyField()
    active_subgroups = serializers.SerializerMethodField()

    class Meta:
        model = CostGroup
        fields = [
            'id', 'name', 'description', 'is_active',
            'total_subgroups', 'active_subgroups',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at',
                            'updated_at', 'total_subgroups']

    def get_active_subgroups(self, obj):
        return obj.active_subgroups.count()


class CostGroupCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostGroup
        fields = [
            'name', 'description', 'is_active'
        ]

    def validate_name(self, value):
        """Validar se o nome não está vazio e não existe duplicado"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")

        # Verificar duplicatas apenas se for criação ou mudança de nome
        instance = getattr(self, 'instance', None)
        if CostGroup.objects.filter(name__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A cost group with this name already exists.")

        return value.strip()


# =====================================================
# SERIALIZERS PARA COSTSUBGROUP
# =====================================================

class CostSubGroupListSerializer(serializers.ModelSerializer):
    cost_group_name = serializers.CharField(
        source='cost_group.name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)
    total_tasks = serializers.ReadOnlyField()

    class Meta:
        model = CostSubGroup
        fields = [
            'id', 'name', 'cost_group', 'cost_group_name',
            'value_stimated', 'is_active', 'total_tasks',
            'created_by', 'created_by_name', 'created_at'
        ]


class CostSubGroupDetailSerializer(serializers.ModelSerializer):
    cost_group = CostGroupListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    total_tasks = serializers.ReadOnlyField()
    active_tasks = serializers.SerializerMethodField()

    class Meta:
        model = CostSubGroup
        fields = [
            'id', 'name', 'cost_group', 'description', 'value_stimated',
            'is_active', 'total_tasks', 'active_tasks',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by',
                            'created_at', 'updated_at', 'total_tasks']

    def get_active_tasks(self, obj):
        return obj.active_tasks.count()


class CostSubGroupCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostSubGroup
        fields = [
            'name', 'cost_group', 'description', 'value_stimated', 'is_active'
        ]

    def validate_name(self, value):
        """Validar se o nome não está vazio"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value.strip()

    def validate_value_stimated(self, value):
        """Validar se o valor estimado é positivo"""
        if value < 0:
            raise serializers.ValidationError(
                "Estimated value must be positive.")
        return value

    def validate(self, data):
        """Validar combinação única de cost_group + name"""
        cost_group = data.get('cost_group')
        name = data.get('name', '').strip()

        if cost_group and name:
            instance = getattr(self, 'instance', None)
            if CostSubGroup.objects.filter(
                cost_group=cost_group,
                name__iexact=name
            ).exclude(pk=instance.pk if instance else None).exists():
                raise serializers.ValidationError({
                    'name': 'A subgroup with this name already exists in this cost group.'
                })

        return data


# =====================================================
# SERIALIZERS PARA PRODUCTIONCELL
# =====================================================

class ProductionCellListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCell
        fields = [
            'id', 'name', 'code', 'color', 'icon', 'order', 'is_active', 'created_at'
        ]


class ProductionCellDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCell
        fields = [
            'id', 'name', 'code', 'description', 'color', 'icon',
            'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductionCellCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCell
        fields = [
            'name', 'code', 'description', 'color', 'icon', 'order', 'is_active'
        ]

    def validate_name(self, value):
        """Validar se o nome não está vazio e não existe duplicado"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")

        # Verificar duplicatas apenas se for criação ou mudança de nome
        instance = getattr(self, 'instance', None)
        if ProductionCell.objects.filter(name__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A production cell with this name already exists.")

        return value.strip()

    def validate_code(self, value):
        """Validar se o código não está vazio e não existe duplicado"""
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        # Verificar duplicatas apenas se for criação ou mudança de código
        instance = getattr(self, 'instance', None)
        if ProductionCell.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A production cell with this code already exists.")

        return value.strip().upper()  # Códigos em maiúscula por convenção

    def validate_order(self, value):
        """Validar se a ordem é positiva"""
        if value < 0:
            raise serializers.ValidationError(
                "Order must be a positive number.")
        return value

    def validate_color(self, value):
        """Validar formato de cor (hex)"""
        if value and not value.startswith('#'):
            raise serializers.ValidationError(
                "Color must be in hex format (e.g., #FF0000).")
        return value


# Adicionar ao final do arquivo apps/projects/serializers.py

# =====================================================
# CHOICE TYPES SERIALIZERS COMPLETOS
# =====================================================

# PROJECT TYPE SERIALIZERS
class ProjectTypeListSerializer(ChoiceTypeSerializer):
    projects_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = ProjectType
        fields = ChoiceTypeSerializer.Meta.fields + ['projects_count']

    def get_projects_count(self, obj):
        return obj.model_projects.count()


class ProjectTypeDetailSerializer(serializers.ModelSerializer):
    projects_count = serializers.SerializerMethodField()
    recent_projects = serializers.SerializerMethodField()

    class Meta:
        model = ProjectType
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'projects_count', 'recent_projects', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'projects_count']

    def get_projects_count(self, obj):
        return obj.model_projects.count()

    def get_recent_projects(self, obj):
        recent = obj.model_projects.order_by('-created_at')[:5]
        return [
            {
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at
            }
            for p in recent
        ]


class ProjectTypeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if ProjectType.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A project type with this code already exists.")

        return value.strip().upper()

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value.strip()


# PROJECT STATUS SERIALIZERS
class ProjectStatusListSerializer(ChoiceTypeSerializer):
    projects_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = ProjectStatus
        fields = ChoiceTypeSerializer.Meta.fields + ['projects_count']

    def get_projects_count(self, obj):
        return obj.projects.count()


class ProjectStatusDetailSerializer(serializers.ModelSerializer):
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectStatus
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'projects_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'projects_count']

    def get_projects_count(self, obj):
        return obj.projects.count()


class ProjectStatusCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if ProjectStatus.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A project status with this code already exists.")

        return value.strip().upper()


# INCORPORATION TYPE SERIALIZERS
class IncorporationTypeListSerializer(ChoiceTypeSerializer):
    incorporations_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = IncorporationType
        fields = ChoiceTypeSerializer.Meta.fields + ['incorporations_count']

    def get_incorporations_count(self, obj):
        return obj.incorporations.count()


class IncorporationTypeDetailSerializer(serializers.ModelSerializer):
    incorporations_count = serializers.SerializerMethodField()

    class Meta:
        model = IncorporationType
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'incorporations_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'incorporations_count']

    def get_incorporations_count(self, obj):
        return obj.incorporations.count()


class IncorporationTypeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncorporationType
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if IncorporationType.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "An incorporation type with this code already exists.")

        return value.strip().upper()


# INCORPORATION STATUS SERIALIZERS
class IncorporationStatusListSerializer(ChoiceTypeSerializer):
    incorporations_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = IncorporationStatus
        fields = ChoiceTypeSerializer.Meta.fields + ['incorporations_count']

    def get_incorporations_count(self, obj):
        return obj.incorporations.count()


class IncorporationStatusDetailSerializer(serializers.ModelSerializer):
    incorporations_count = serializers.SerializerMethodField()

    class Meta:
        model = IncorporationStatus
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'incorporations_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'incorporations_count']

    def get_incorporations_count(self, obj):
        return obj.incorporations.count()


class IncorporationStatusCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncorporationStatus
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if IncorporationStatus.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "An incorporation status with this code already exists.")

        return value.strip().upper()


# STATUS CONTRACT SERIALIZERS
class StatusContractListSerializer(ChoiceTypeSerializer):
    contracts_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = StatusContract
        fields = ChoiceTypeSerializer.Meta.fields + ['contracts_count']

    def get_contracts_count(self, obj):
        return obj.contracts.count()


class StatusContractDetailSerializer(serializers.ModelSerializer):
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = StatusContract
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'contracts_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'contracts_count']

    def get_contracts_count(self, obj):
        return obj.contracts.count()


class StatusContractCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusContract
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if StatusContract.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A contract status with this code already exists.")

        return value.strip().upper()


# PAYMENT METHOD SERIALIZERS
class PaymentMethodListSerializer(ChoiceTypeSerializer):
    contracts_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = PaymentMethod
        fields = ChoiceTypeSerializer.Meta.fields + ['contracts_count']

    def get_contracts_count(self, obj):
        return obj.contracts.count()


class PaymentMethodDetailSerializer(serializers.ModelSerializer):
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'contracts_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'contracts_count']

    def get_contracts_count(self, obj):
        return obj.contracts.count()


class PaymentMethodCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if PaymentMethod.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "A payment method with this code already exists.")

        return value.strip().upper()


# OWNER TYPE SERIALIZERS
class OwnerTypeListSerializer(ChoiceTypeSerializer):
    owners_count = serializers.SerializerMethodField()

    class Meta(ChoiceTypeSerializer.Meta):
        model = OwnerType
        fields = ChoiceTypeSerializer.Meta.fields + ['owners_count']

    def get_owners_count(self, obj):
        return obj.contract_owners.count()


class OwnerTypeDetailSerializer(serializers.ModelSerializer):
    owners_count = serializers.SerializerMethodField()

    class Meta:
        model = OwnerType
        fields = [
            'id', 'code', 'name', 'color', 'icon', 'order', 'is_active',
            'owners_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'owners_count']

    def get_owners_count(self, obj):
        return obj.contract_owners.count()


class OwnerTypeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerType
        fields = ['code', 'name', 'color', 'icon', 'order', 'is_active']

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")

        instance = getattr(self, 'instance', None)
        if OwnerType.objects.filter(code__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "An owner type with this code already exists.")

        return value.strip().upper()


# =====================================================
# CONTRACT MANAGEMENT SERIALIZERS COMPLETOS
# =====================================================

# CONTRACT OWNER SERIALIZERS
class ContractOwnerListSerializer(serializers.ModelSerializer):
    owner_type_name = serializers.CharField(
        source='owner_type.name', read_only=True)
    client_name = serializers.CharField(
        source='client.get_full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    contract_number = serializers.CharField(
        source='contract.contract_number', read_only=True)
    incorporation_name = serializers.CharField(
        source='contract.incorporation.name', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ContractOwner
        fields = [
            'id', 'contract', 'contract_number', 'incorporation_name',
            'client', 'client_name', 'client_email', 'owner_type',
            'owner_type_name', 'percentual_propriedade', 'valor_participacao',
            'created_by', 'created_by_name', 'created_at'
        ]


class ContractOwnerDetailSerializer(serializers.ModelSerializer):
    owner_type = OwnerTypeSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    contract = ContractListSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ContractOwner
        fields = [
            'id', 'contract', 'client', 'owner_type',
            'percentual_propriedade', 'valor_participacao',
            'observations', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at',
                            'updated_at', 'valor_participacao']


class ContractOwnerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractOwner
        fields = [
            'contract', 'client', 'owner_type',
            'percentual_propriedade', 'observations'
        ]

    def validate_percentual_propriedade(self, value):
        """Validar se o percentual está entre 0 e 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Ownership percentage must be between 0 and 100.")
        return value

    def validate(self, data):
        """Validar se a soma dos percentuais do contrato não excede 100%"""
        contract = data.get('contract')
        percentual = data.get('percentual_propriedade', 0)

        if contract:
            instance = getattr(self, 'instance', None)
            existing_total = ContractOwner.objects.filter(
                contract=contract
            ).exclude(pk=instance.pk if instance else None).aggregate(
                total=Sum('percentual_propriedade')
            )['total'] or 0

            if (existing_total + percentual) > 100:
                raise serializers.ValidationError({
                    'percentual_propriedade': f'Total ownership percentage for this contract would exceed 100%. Current total: {existing_total}%'
                })

        return data


# CONTRACT PROJECT SERIALIZERS (melhorados)
class ContractProjectListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source='project.project_name', read_only=True)
    contract_number = serializers.CharField(
        source='contract.contract_number', read_only=True)
    incorporation_name = serializers.CharField(
        source='contract.incorporation.name', read_only=True)
    project_status = serializers.CharField(
        source='project.status_project.name', read_only=True)
    # created_by_name = serializers.CharField(
    #   source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ContractProject
        fields = [
            'id', 'contract', 'contract_number', 'incorporation_name',
            'project', 'project_name', 'project_status',
            'preco_venda_unidade', 'data_vinculacao', 'created_at'
        ]


class ContractProjectDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    contract = ContractListSerializer(read_only=True)
    # created_by = UserSerializer(read_only=True)

    class Meta:
        model = ContractProject
        fields = [
            'id', 'contract', 'project', 'preco_venda_unidade',
            'data_vinculacao', 'observacoes_especificas',
            'condicoes_especiais', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'data_vinculacao']


class ContractProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractProject
        fields = [
            'contract', 'project', 'preco_venda_unidade',
            'observacoes_especificas', 'condicoes_especiais'
        ]

    def validate_preco_venda_unidade(self, value):
        """Validar se o preço é positivo"""
        if value <= 0:
            raise serializers.ValidationError("Sale price must be positive.")
        return value

    def validate(self, data):
        """Validar se o projeto já não está vinculado ao contrato"""
        contract = data.get('contract')
        project = data.get('project')

        if contract and project:
            instance = getattr(self, 'instance', None)
            if ContractProject.objects.filter(
                contract=contract,
                project=project
            ).exclude(pk=instance.pk if instance else None).exists():
                raise serializers.ValidationError({
                    'project': 'This project is already linked to this contract.'
                })

        return data


# =====================================================
# TASK RESOURCE SERIALIZERS (ESTRUTURA PREPARADA)
# =====================================================

# Estes serializers serão implementados quando o modelo TaskResource for criado
# class TaskResourceListSerializer(serializers.ModelSerializer):
#     pass

# class TaskResourceDetailSerializer(serializers.ModelSerializer):
#     pass

# class TaskResourceCreateUpdateSerializer(serializers.ModelSerializer):
#     pass
