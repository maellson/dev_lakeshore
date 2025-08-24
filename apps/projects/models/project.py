from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from projects.models.choice_types import ProjectType, ProjectStatus
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from projects.models.model_project import ModelProject
from projects.models.incorporation import Incorporation
from projects.models.choice_types import ProductionCell
from apps.contracts.models.contract import Contract
from projects.models.phase_project import PhaseProject
from projects.models.model_phase import ModelPhase
from projects.models.model_task import ModelTask
from projects.models.task_project import TaskProject

User = get_user_model()


class Project(models.Model):
    """
    Classe abstrata base para todos os tipos de projeto
    Contém apenas campos comuns a TODOS os tipos
    """

    # Relacionamento com incorporação
    incorporation = models.ForeignKey(
        Incorporation,
        on_delete=models.RESTRICT,
        related_name='projects',
        verbose_name="Incorporação",
        help_text="Incorporação ao qual este projeto pertence"
    )
    model_project = models.ForeignKey(
        ModelProject,
        on_delete=models.RESTRICT,
        related_name='projects',
        verbose_name="Modelo de Projeto",
        help_text="Modelo/template utilizado para este projeto"
    )

    project_name = models.CharField(
        max_length=200,
        verbose_name="Project Name",
        help_text="Descriptive name of the project",
    )
    production_cell = models.ForeignKey(
        ProductionCell,
        on_delete=models.RESTRICT,
        related_name='projects',
        verbose_name="Production Cell",
        help_text="Production cell responsible for this project",
        blank=True,
        null=True  
    )

    # Status usando ChoiceTypeBase
    status_project = models.ForeignKey(
        ProjectStatus,
        on_delete=models.RESTRICT,
        verbose_name="Status of the Project",
        help_text="Status atual do projeto"
    )

    # Localização básica (todos têm endereço)
    address = models.TextField(
        verbose_name="address",
        help_text="address of the project"
    )

    # Área total (todos têm alguma área)
    area_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Área Total (m²)",
        help_text="Área total do lote/terreno/unidade",
        default=Decimal('0.01'),
    )

    # Custos básicos (todos têm custo)
    construction_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Construction Cost",
        help_text="Real construction cost of the project",
        default=Decimal('0.00')
    )

    sale_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Sale Value",
        help_text="Total sale value of the contract"
    )

    project_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Project Value",
        help_text="Real cost of the project",
        default=Decimal('0.00')
    )

    roi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="ROI (%)",
        help_text="Return on Investment percentage",
        default=Decimal('0.00')
    )

    # Percentual de conclusão (todos podem ter)
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        default=Decimal('0.00'),
        verbose_name="Completion Percentage (%)",
        help_text="Percentage of completion of the project"
    )

    # Observações gerais
    observations = models.TextField(
        verbose_name="Observations",
        help_text="Additional information about the project",
        blank=True
    )

    def get_default_delivery_date():
        """Calcula data de entrega padrão (120 dias a partir de hoje)"""
        return (timezone.now() + timedelta(days=120)).date()

    expected_delivery_date = models.DateField(  # TODO: CONFIRMAR COM ANA
        verbose_name="Expected Delivery Date",
        help_text="Expected date for project delivery",
        default=get_default_delivery_date
    )
    # Controle de sistema
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="created at"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name="Created By",
        help_text="User who created this project"
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
       # abstract = True  # ← Classe abstrata!
        ordering = ['incorporation']

    def __str__(self):
        return f"{self.project_name} ({self.get_type_display()}) - {self.incorporation.name if self.incorporation else 'No Incorporation'} - "

    @property
    def cost_variance(self):
        """Calcula variação entre custo estimado e real"""
        if self.estimated_cost == 0:
            return Decimal('0.00')

        diff = self.construction_cost - self.project_value
        return (diff / self.project_value) * 100

    @property
    def is_sold(self):
        """Verifica se o projeto foi vendido (tem contrato)"""
        return self.project_contracts.exists()

    # Métodos abstratos que devem ser implementados pelas subclasses
    def can_start_execution(self):
        """Cada tipo implementa sua lógica"""
        raise NotImplementedError(
            "Subclasse deve implementar can_start_execution")

    def get_type_display(self):
        """Template Method: Exibição padronizada do tipo"""
        return self.model_project.project_type if self.model_project else "Não definido"

    @property
    def is_delayed(self):
        """Verifica se o projeto está em atraso"""
        if not self.expected_delivery_date:
            return False

        from django.utils import timezone
        return (
            self.status_projeto not in ['CONCLUIDA', 'ENTREGUE', 'CANCELADA'] and
            timezone.now().date() > self.expected_delivery_date
        )

    def save(self, *args, **kwargs):
        """Override save to initialize project from model"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.model_project:
            self.initialize_from_model()

    def initialize_from_model(self):
        """
        AUTOMAÇÃO CRÍTICA: Popula projeto com fases e tarefas do modelo
        """
        from .phase_project import PhaseProject
        from .task_project import TaskProject

        # Verificar se já foi inicializado para evitar duplicatas
        if self.phases.exists():
            return

        # 1. Criar PhaseProject para cada ModelPhase
        for model_phase in self.model_project.phases.filter(is_active=True).order_by('execution_order'):
            phase_project = PhaseProject.objects.create(
                project=self,
                model_phase=model_phase,
                phase_name=model_phase.phase_name,
                phase_code=model_phase.phase_code,
                phase_status='NOT_STARTED',
                priority='NORMAL',
                execution_order=model_phase.execution_order,  # ✅ CORRIGIDO
                estimated_cost=0,
                requires_inspection=model_phase.requires_inspection,  # ✅ ADICIONAL
                created_by=self.created_by
            )

            # 2. Criar TaskProject para cada ModelTask da fase
            for model_task in model_phase.tasks.filter(is_active=True).order_by('execution_order'):
                TaskProject.objects.create(
                    phase_project=phase_project,
                    model_task=model_task,
                    task_name=model_task.task_name,
                    task_code=model_task.task_code,
                    task_description=model_task.detailed_description,  # ✅ CORRIGIDO
                    task_status='PENDING',  # ✅ CORRIGIDO (status correto)
                    priority='MEDIUM',  # ✅ CORRIGIDO (priority correto)
                    execution_order=model_task.execution_order,  # ✅ CORRIGIDO
                    estimated_duration_hours=model_task.estimated_duration_hours,  # ✅ CORRIGIDO
                    estimated_cost=model_task.estimated_labor_cost,
                    requires_approval=model_task.requires_specialization,  # ✅ ADICIONAL
                    created_by=self.created_by
                )

        # 3. Configurar dependências entre fases
        self._setup_phase_dependencies()

        # 4. Configurar dependências entre tarefas
        self._setup_task_dependencies()

    def _setup_phase_dependencies(self):
        """Configura dependências entre fases baseado no modelo"""
        phase_projects = self.phases.all()

        for phase_project in phase_projects:
            # Buscar fases pré-requisito no modelo
            for prereq_model_phase in phase_project.model_phase.prerequisite_phases.all():
                # Encontrar a PhaseProject correspondente
                try:
                    prereq_phase_project = phase_projects.get(
                        model_phase=prereq_model_phase)
                    phase_project.prerequisite_phases.add(prereq_phase_project)
                except PhaseProject.DoesNotExist:
                    continue

    def _setup_task_dependencies(self):
        """Configura dependências entre tarefas baseado no modelo"""
        for phase_project in self.phases.all():
            task_projects = phase_project.tasks.all()

            for task_project in task_projects:
                # Buscar tarefas pré-requisito no modelo
                for prereq_model_task in task_project.model_task.prerequisite_tasks.all():
                    # Encontrar a TaskProject correspondente
                    try:
                        prereq_task_project = task_projects.get(
                            model_task=prereq_model_task)
                        task_project.prerequisite_tasks.add(
                            prereq_task_project)
                    except TaskProject.DoesNotExist:
                        continue

    @property
    def total_phases(self):
        """Total de fases do projeto"""
        return self.phases.count()

    @property
    def completed_phases(self):
        """Fases concluídas do projeto"""
        return self.phases.filter(phase_status='COMPLETED').count()

    @property
    def total_tasks(self):
        """Total de tarefas do projeto"""
        return sum(phase.tasks.count() for phase in self.phases.all())

    @property
    def completed_tasks(self):
        """Tarefas concluídas do projeto"""
        return sum(phase.tasks.filter(task_status='COMPLETED').count() for phase in self.phases.all())
