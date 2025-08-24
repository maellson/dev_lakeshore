# apps/projects/admin.py
from .models import Contact
from django.db.models import Q
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models.choice_types import (
    ProjectType, ProjectStatus, IncorporationStatus, IncorporationType,
    StatusContract, PaymentMethod, ProductionCell, OwnerType
)
from .models import (
    Incorporation, ModelProject, Project, Contract,
    ContractOwner, ContractProject, CostGroup, CostSubGroup,
    ModelPhase, ModelTask, PhaseProject, TaskProject,
    TaskResource, TaskSpecification
)

from .admin_360 import Projects360Admin  # Importar o novo admin


# ======================
# CHOICE TYPES ADMIN
# ======================


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(IncorporationType)
class IncorporationTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(IncorporationStatus)
class IncorporationStatusAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(StatusContract)
class StatusContractAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(ProductionCell)
class ProductionCellAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


@admin.register(OwnerType)
class OwnerTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'color_badge',
                    'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']

    def color_badge(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                obj.color, obj.name
            )
        return obj.name
    color_badge.short_description = 'Color'


# ======================
# MAIN MODELS ADMIN
# ======================

@admin.register(Incorporation)
class IncorporationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'incorporation_type', 'incorporation_status',
        'county', 'total_projects', 'projects_sold', 'launch_date', 'is_active'
    ]
    list_filter = [
        'incorporation_type', 'incorporation_status', 'county',
        'is_active', 'launch_date'
    ]
    search_fields = ['name', 'project_description']
    readonly_fields = ['created_at', 'updated_at',
                       'total_projects', 'projects_sold', 'sold_percentage']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'incorporation_type', 'county')
        }),
        ('Descrição e Status', {
            'fields': ('project_description', 'incorporation_status', 'is_active')
        }),
        ('Datas', {
            'fields': ('launch_date',)
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_projects', 'projects_sold', 'sold_percentage'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ModelProject)
class ModelProjectAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'project_type', 'county',
        'custo_base_estimado', 'versao', 'is_active'
    ]
    list_filter = ['project_type', 'county', 'is_active']
    search_fields = ['code', 'name', 'especificacoes_padrao']
    readonly_fields = ['created_at', 'updated_at',
                       'total_fases', 'total_tasks', 'custo_calculado_por_m2']
    actions = ['duplicate_models']

    def duplicate_models(self, request, queryset):
        """
        Admin Action to duplicate selected project models.
        """
        for model_instance in queryset:
            new_name = f"{model_instance.name} (Copy)"
            model_instance.duplicate_model(new_name=new_name)

        self.message_user(
            request, f'{queryset.count()} project model(s) duplicated successfully.')

    duplicate_models.short_description = "Duplicate selected models"

    fieldsets = (
        ('Identificação', {
            'fields': ('code', 'name', 'project_type', 'county', 'versao')
        }),
        ('Especificações', {
            'fields': (
                'area_construida_padrao',
                'especificacoes_padrao'
            )
        }),
        ('Custos', {
            'fields': (
                'custo_base_estimado', 'custo_por_m2', 'custo_calculado_por_m2'
            )
        }),
        ('Cronograma e Requisitos', {
            'fields': (
                'duracao_construcao_dias', 'requisitos_especiais',
                'regulamentacoes_county'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_fases', 'total_tasks'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ContractOwnerInline(admin.TabularInline):
    model = ContractOwner
    extra = 1
    readonly_fields = ['created_at', 'valor_participacao']
    fields = [
        'client', 'owner_type', 'percentual_propriedade',
        'valor_participacao', 'observations'
    ]


class ContractProjectInline(admin.TabularInline):
    model = ContractProject
    extra = 1
    readonly_fields = ['data_vinculacao',]
    fields = [
        'project', 'preco_venda_unidade', 'observacoes_especificas'
    ]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        'contract_number', 'incorporation', 'contract_value', 'lead',
        'payment_method', 'status_contract', 'sign_date',
        'total_owners', 'total_projects'
    ]
    list_filter = [
        'status_contract', 'payment_method', 'incorporation',
        'sign_date', 'lead'
    ]
    search_fields = ['contract_number', 'incorporation__name']
    readonly_fields = [
        'created_at', 'updated_at', 'total_owners',
        'total_projects', 'valor_medio_projeto', 'contract_value'
    ]
    inlines = [ContractOwnerInline, ContractProjectInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('contract_number', 'lead', 'incorporation', 'management_company')
        }),
        ('Informações Financeiras', {
            'fields': (
                'contract_value', 'payment_method',
                'valor_medio_projeto'
            )
        }),
        ('Status e Datas', {
            'fields': ('status_contract', 'sign_date', 'payment_date')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_owners', 'total_projects'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Atribui o usuário logado ao campo 'created_by' dos objetos inlines.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            # Checa se é uma nova instância (não tem pk) e se precisa do created_by
            if hasattr(instance, 'created_by') and not instance.pk:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def save_formset(self, request, form, formset, change):
        """
        Atribui o usuário logado ao campo 'created_by' dos objetos inlines.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, (ContractOwner, ContractProject)) and not instance.pk:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_name', 'id', 'incorporation', 'model_project',
        'status_project', 'area_total', 'project_value',
        'completion_percentage', 'is_sold'
    ]
    list_filter = [
        'status_project', 'incorporation', 'model_project',
        'expected_delivery_date'
    ]
    search_fields = ['project_name', 'address', 'observations']
    readonly_fields = [
        'created_at', 'updated_at', 'cost_variance',
        'is_sold', 'is_delayed'
    ]

    fieldsets = (
        ('Identificação', {
            'fields': (
                'project_name', 'incorporation', 'model_project', 'production_cell'
            )
        }),
        ('Localização e Especificações', {
            'fields': ('address', 'area_total')
        }),
        ('Status e Cronograma', {
            'fields': (
                'status_project', 'completion_percentage',
                'expected_delivery_date', 'is_delayed'
            )
        }),
        ('Custos', {
            'fields': ('construction_cost', 'project_value', 'sale_value', 'cost_variance')
        }),
        ('Observações', {
            'fields': ('observations',)
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('is_sold',),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContractOwner)
class ContractOwnerAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'id', 'nome_completo', 'owner_type',
        'percentual_propriedade', 'valor_participacao'
    ]
    list_filter = ['owner_type', 'contract__incorporation']
    search_fields = [
        'client__first_name', 'client__last_name',
        'contract__contract_number'
    ]
    readonly_fields = [
        'created_at', 'nome_completo', 'email',
        'phone', 'address', 'valor_participacao'
    ]

    fieldsets = (
        ('Contrato e Cliente', {
            'fields': ('contract', 'client', 'owner_type')
        }),
        ('Participação', {
            'fields': ('percentual_propriedade', 'valor_participacao')
        }),
        ('Informações do Cliente (Somente Leitura)', {
            'fields': ('nome_completo', 'email', 'phone', 'address'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observations',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContractProject)
class ContractProjectAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'project', 'preco_venda_unidade', 'updated_at'
    ]
    list_filter = [
        'contract__incorporation', 'project__model_project',
        'data_vinculacao'
    ]
    search_fields = [
        'contract__contract_number', 'project__project_name'
    ]
    readonly_fields = [
        'data_vinculacao', 'updated_at', 'dias_desde_vinculacao'
    ]

    fieldsets = (
        ('Relacionamentos', {
            'fields': ('contract', 'project')
        }),
        ('Datas e Condições', {
            'fields': (
                'preco_venda_unidade',
                'dias_desde_vinculacao'
            )
        }),
        ('Observações', {
            'fields': ('observacoes_especificas', 'condicoes_especiais')
        }),
        ('Sistema', {
            'fields': ('data_vinculacao', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ======================
# COST MANAGEMENT ADMIN
# ======================

@admin.register(CostGroup)
class CostGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_subgroups', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_subgroups']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_subgroups',),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CostSubGroup)
class CostSubGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost_group',
                    'total_tasks', 'is_active', 'created_at']
    list_filter = ['cost_group', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'cost_group__name']
    readonly_fields = ['created_at', 'updated_at', 'total_tasks']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('cost_group', 'name', 'description', 'is_active')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_tasks',),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ======================
# TEMPLATE MODELS ADMIN
# ======================

@admin.register(ModelPhase)
class ModelPhaseAdmin(admin.ModelAdmin):
    list_display = [
        'execution_order', 'phase_name', 'project_model',
        'estimated_duration_days', 'total_tasks', 'is_mandatory', 'is_active'
    ]
    list_filter = ['project_model', 'is_mandatory',
                   'requires_inspection', 'is_active']
    search_fields = ['phase_name', 'phase_code', 'project_model__name']
    readonly_fields = ['created_at', 'updated_at',
                       'total_tasks', 'mandatory_tasks', 'total_task_duration']

    fieldsets = (
        ('Identificação', {
            'fields': ('project_model', 'phase_name', 'phase_code', 'execution_order')
        }),
        ('Descrição', {
            'fields': ('phase_description', 'phase_objectives')
        }),
        ('Características', {
            'fields': (
                'estimated_duration_days', 'is_mandatory',
                'allows_parallel', 'requires_inspection'
            )
        }),
        ('Requisitos', {
            'fields': ('prerequisite_phases', 'initial_requirements')
        }),
        ('Critérios de Conclusão', {
            'fields': ('completion_criteria', 'deliverables')
        }),
        ('Status', {
            'fields': ('is_active', 'version')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_tasks', 'mandatory_tasks', 'total_task_duration'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ModelTask)
class ModelTaskAdmin(admin.ModelAdmin):
    list_display = [
        'execution_order', 'task_name', 'model_phase', 'task_type',
        'cost_subgroup', 'estimated_duration_hours', 'estimated_labor_cost',
        'is_mandatory', 'is_active'
    ]
    list_filter = [
        'model_phase', 'task_type', 'cost_subgroup', 'skill_category',
        'is_mandatory', 'requires_specialization', 'is_active'
    ]
    search_fields = ['task_name', 'task_code', 'model_phase__phase_name']
    readonly_fields = ['created_at', 'updated_at',
                       'total_resources', 'total_resource_cost', 'total_time_hours']

    fieldsets = (
        ('Identificação', {
            'fields': ('model_phase', 'task_name', 'task_code', 'task_type', 'execution_order')
        }),
        ('Classificação de Custos', {
            'fields': ('cost_subgroup',)
        }),
        ('Descrição', {
            'fields': ('detailed_description', 'task_objective')
        }),
        ('Tempo e Execução', {
            'fields': ('estimated_duration_hours', 'total_time_hours')
        }),
        ('Características', {
            'fields': (
                'is_mandatory', 'allows_parallel', 'requires_specialization',
                'skill_category'
            )
        }),
        ('Recursos Humanos', {
            'fields': ('required_people', 'required_skills')
        }),
        ('Requisitos Especiais', {
            'fields': (
                'special_requirements', 'execution_conditions',
                'required_equipment'
            )
        }),
        ('Controle de Qualidade', {
            'fields': ('acceptance_criteria', 'checkpoints')
        }),
        ('Segurança', {
            'fields': ('identified_risks', 'safety_measures', 'required_ppe')
        }),
        ('Custos', {
            'fields': ('estimated_labor_cost', 'total_resource_cost')
        }),
        ('Dependências', {
            'fields': ('prerequisite_tasks',)
        }),
        ('Status', {
            'fields': ('is_active', 'version')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('total_resources',),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ======================
# PROJECT EXECUTION ADMIN
# ======================

@admin.register(PhaseProject)
class PhaseProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'phase_name', 'phase_status', 'priority',
        'planned_start_date', 'planned_end_date', 'completion_percentage'
    ]
    list_filter = [
        'phase_status', 'priority', 'project__incorporation',
        'planned_start_date', 'inspection_result', 'project',
    ]
    search_fields = ['phase_name',
                     'project__project_name', 'model_phase__phase_name']
    readonly_fields = [
        'created_at', 'updated_at', 'is_delayed',
        'total_tasks', 'completed_tasks'
    ]

    fieldsets = (
        ('Identificação', {
            'fields': ('project', 'model_phase', 'phase_name', 'phase_code')
        }),
        ('Status e Prioridade', {
            'fields': ('phase_status', 'priority', 'completion_percentage')
        }),
        ('Cronograma Planejado', {
            'fields': ('planned_start_date', 'planned_end_date')
        }),
        ('Execução Real', {
            'fields': ('actual_start_date', 'actual_end_date')
        }),
        ('Responsabilidades', {
            'fields': ('technical_responsible',)
        }),
        ('Inspeção', {
            'fields': ('inspection_result', 'inspection_notes')
        }),
        ('Custos', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('is_delayed', 'total_tasks', 'completed_tasks'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskProject)
class TaskProjectAdmin(admin.ModelAdmin):
    list_display = [
        'task_name', 'phase_project', 'task_status', 'priority',
        'assigned_to', 'planned_start_date', 'planned_end_date',
        'completion_percentage'
    ]
    list_filter = [
        'task_status', 'priority', 'phase_project__project',
        'assigned_to', 'planned_start_date'
    ]
    search_fields = ['task_name',
                     'phase_project__phase_name', 'model_task__task_name']
    readonly_fields = [
        'created_at', 'updated_at', 'is_delayed',
        'total_specifications',  'cost_variance'
    ]

    fieldsets = (
        ('Identificação', {
            'fields': ('phase_project', 'model_task', 'task_name', 'task_code')
        }),
        ('Status e Atribuição', {
            'fields': ('task_status', 'priority', 'assigned_to', 'completion_percentage')
        }),
        ('Cronograma Planejado', {
            'fields': ('planned_start_date', 'planned_end_date')
        }),
        ('Execução Real', {
            'fields': ('actual_start_date', 'actual_end_date')
        }),
        ('Custos', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Observações', {
            'fields': ('notes', 'approval_notes')
        }),
        ('Métricas (Somente Leitura)', {
            'fields': ('is_delayed', 'total_specifications'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskResource)
class TaskResourceAdmin(admin.ModelAdmin):
    list_display = [
        'resource_name', 'model_task', 'resource_type',
        'required_quantity', 'unit_measure', 'estimated_unit_cost',
        'estimated_total_cost', 'is_mandatory'
    ]
    list_filter = ['resource_type', 'is_mandatory', 'model_task__model_phase']
    search_fields = ['resource_name', 'model_task__task_name']
    readonly_fields = ['created_at', 'updated_at', 'estimated_total_cost']

    fieldsets = (
        ('Identificação', {
            'fields': ('model_task', 'resource_name', 'resource_type')
        }),
        ('Quantidade e Unidade', {
            'fields': ('required_quantity', 'unit_measure')
        }),
        ('Custos', {
            'fields': ('estimated_unit_cost', 'estimated_total_cost')
        }),
        ('Características', {
            'fields': ('is_mandatory', 'resource_notes')
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskSpecification)
class TaskSpecificationAdmin(admin.ModelAdmin):
    list_display = [
        'task_project', 'task_resource', 'planned_quantity',
        'actual_quantity_used', 'actual_unit_cost', 'actual_total_cost',
        'specification_status', 'supplier_used'
    ]
    list_filter = [
        'specification_status', 'task_project__phase_project__project',
        'task_resource__resource_type'
    ]
    search_fields = [
        'task_project__task_name', 'task_resource__resource_name',
        'supplier_used'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'quantity_variance',
        'cost_variance', 'actual_total_cost'
    ]

    fieldsets = (
        ('Identificação', {
            'fields': ('task_project', 'task_resource', 'usage_description')
        }),
        ('Quantidades', {
            'fields': ('planned_quantity', 'actual_quantity_used', 'quantity_variance')
        }),
        ('Custos', {
            'fields': ('actual_unit_cost', 'actual_total_cost', 'cost_variance')
        }),
        ('Status e Fornecedor', {
            'fields': ('specification_status', 'supplier_used')
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# apps/projects/admin.py - ADICIONAR

    @admin.register(Contact)
    class ContactAdmin(admin.ModelAdmin):
        """
        Admin para gerenciar contatos de projetos
        Permite associar clientes a projetos específicos com papéis definidos
        """

        # =====================================================
        # CONFIGURAÇÕES DE LISTAGEM
        # =====================================================
        list_display = [
            'contact_display', 'project_link', 'owner_display',
            'contact_role_badge', 'is_active_status', 'created_at'
        ]

        list_filter = [
            'contact_role', 'is_active', 'created_at',
            'project__incorporation', 'contact__tipo_usuario'
        ]

        search_fields = [
            'contact__email', 'contact__first_name', 'contact__last_name',
            'project__project_name', 'owner__client__email',
            'owner__client__first_name', 'owner__client__last_name'
        ]

        # =====================================================
        # ORGANIZAÇÃO DOS CAMPOS NO FORMULÁRIO
        # =====================================================
        fieldsets = (
            ('Relacionamentos Principais', {
                'fields': ('contact', 'project', 'owner'),
                'description': 'Defina quem monitora qual projeto e por qual proprietário'
            }),
            ('Configurações do Contato', {
                'fields': ('contact_role', 'is_active'),
                'classes': ('wide',)
            }),
            ('Sistema', {
                'fields': ('created_by', 'created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )

        # =====================================================
        # CAMPOS SOMENTE LEITURA E AUTOCOMPLETE
        # =====================================================
        readonly_fields = ['created_at', 'updated_at']
        autocomplete_fields = ['contact', 'project', 'owner', 'created_by']

        # =====================================================
        # FILTROS HORIZONTAIS PARA MELHOR UX
        # =====================================================
        raw_id_fields = ['contact', 'project', 'owner', 'created_by']

        # =====================================================
        # ORDENAÇÃO PADRÃO
        # =====================================================
        ordering = ['-created_at', 'project__project_name', 'contact_role']

        # =====================================================
        # OTIMIZAÇÃO DE QUERIES
        # =====================================================
        def get_queryset(self, request):
            """Otimiza queries com select_related e prefetch_related"""
            return super().get_queryset(request).select_related(
                'contact', 'project', 'owner', 'owner__client',
                'project__incorporation', 'created_by'
            )

        # =====================================================
        # MÉTODOS DE DISPLAY PERSONALIZADOS
        # =====================================================

        def contact_display(self, obj):
            """Exibe informações do contato com link para edição"""
            if obj.contact:
                user_url = reverse(
                    'admin:account_customuser_change', args=[obj.contact.id])
                return format_html(
                    '<a href="{}" target="_blank">{}</a><br>'
                    '<small style="color: #666;">{}</small>',
                    user_url,
                    obj.contact.get_full_name(),
                    obj.contact.email
                )
            return '-'
        contact_display.short_description = 'Contato'
        contact_display.admin_order_field = 'contact__first_name'

        def project_link(self, obj):
            """Link para o projeto relacionado"""
            if obj.project:
                project_url = reverse(
                    'admin:projects_project_change', args=[obj.project.id])
                return format_html(
                    '<a href="{}" target="_blank">{}</a><br>'
                    '<small style="color: #666;">{}</small>',
                    project_url,
                    obj.project.project_name,
                    obj.project.incorporation.name if obj.project.incorporation else 'Sem incorporação'
                )
            return '-'
        project_link.short_description = 'Projeto'
        project_link.admin_order_field = 'project__project_name'

        def owner_display(self, obj):
            """Exibe informações do proprietário"""
            if obj.owner and obj.owner.client:
                owner_url = reverse(
                    'admin:projects_contractowner_change', args=[obj.owner.id])
                return format_html(
                    '<a href="{}" target="_blank">{}</a><br>'
                    '<small style="color: #666;">{}% - {}</small>',
                    owner_url,
                    obj.owner.client.get_full_name(),
                    obj.owner.percentual_propriedade,
                    obj.owner.owner_type.name if obj.owner.owner_type else 'Tipo não definido'
                )
            return '-'
        owner_display.short_description = 'Proprietário'
        owner_display.admin_order_field = 'owner__client__first_name'

        def contact_role_badge(self, obj):
            """Badge colorido para o papel do contato"""
            role_colors = {
                'PRIMARY': '#28a745',      # Verde
                'TECHNICAL': '#007bff',    # Azul
                'FINANCIAL': '#ffc107',    # Amarelo
                'LEGAL': '#6f42c1',        # Roxo
                'PROJECT_MANAGER': '#fd7e14',  # Laranja
                'SUPERVISOR': '#20c997',   # Teal
            }

            color = role_colors.get(obj.contact_role, '#6c757d')

            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
                color,
                obj.get_contact_role_display()
            )
        contact_role_badge.short_description = 'Papel'
        contact_role_badge.admin_order_field = 'contact_role'

        def is_active_status(self, obj):
            """Status visual ativo/inativo"""
            if obj.is_active:
                return format_html(
                    '<span style="color: #28a745; font-weight: bold;">● Ativo</span>'
                )
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">● Inativo</span>'
            )
        is_active_status.short_description = 'Status'
        is_active_status.admin_order_field = 'is_active'

        # =====================================================
        # AÇÕES PERSONALIZADAS
        # =====================================================

        actions = ['ativar_contatos',
                   'desativar_contatos', 'duplicar_contatos']

        def ativar_contatos(self, request, queryset):
            """Ação para ativar contatos selecionados"""
            updated = queryset.update(is_active=True)
            self.message_user(
                request,
                f'{updated} contato(s) ativado(s) com sucesso.'
            )
        ativar_contatos.short_description = "Ativar contatos selecionados"

        def desativar_contatos(self, request, queryset):
            """Ação para desativar contatos selecionados"""
            updated = queryset.update(is_active=False)
            self.message_user(
                request,
                f'{updated} contato(s) desativado(s) com sucesso.'
            )
        desativar_contatos.short_description = "Desativar contatos selecionados"

        # =====================================================
        # VALIDAÇÕES E SALVAMENTO
        # =====================================================

        def save_model(self, request, obj, form, change):
            """Configura created_by automaticamente"""
            if not change:  # Novo objeto
                obj.created_by = request.user

            # Validação customizada
            if obj.contact and obj.contact.tipo_usuario.code != 'CLIENT':
                from django.contrib import messages
                messages.warning(
                    request,
                    f'Atenção: O usuário {obj.contact.email} não é do tipo CLIENT'
                )

            super().save_model(request, obj, form, change)

        # =====================================================
        # PERMISSÕES BASEADAS NO USUÁRIO
        # =====================================================

        def has_change_permission(self, request, obj=None):
            """Controla permissão de edição"""
            if request.user.is_superuser:
                return True

            # Usuários internos podem gerenciar contatos
            if (hasattr(request.user, 'perfil_interno') and
                    request.user.perfil_interno.nivel_acesso.nivel >= 3):
                return True

            return False

        def has_delete_permission(self, request, obj=None):
            """Controla permissão de exclusão"""
            if request.user.is_superuser:
                return True

            # Apenas níveis 4+ podem deletar
            if (hasattr(request.user, 'perfil_interno') and
                    request.user.perfil_interno.nivel_acesso.nivel >= 4):
                return True

            return False
