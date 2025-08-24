from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import County
from simple_history.models import HistoricalRecords
from projects.models.choice_types import ProjectType


class ModelProject(models.Model):
    """
    Model para templates/modelos de projetos
    Define padrões reutilizáveis para diferentes tipos de construção
    """

    # Identificação do modelo
    name = models.CharField(
        max_length=200,
        verbose_name="Name of the Model",
        help_text="Ex: Casa Tipo A, Townhouse Padrão, Terreno Comercial"
    )

    code = models.CharField(
        max_length=50,
        verbose_name="Code of the Model",
        help_text="Unique code for identification , like M1, C2, T3",
        unique=True
    )
    # PODE SER UMA INFRAESTRUTURA, UMA HOUSE, UM APARTAMENTO..
    project_type = models.ForeignKey(
        ProjectType,
        related_name='modelos_projeto',
        on_delete=models.RESTRICT,
        verbose_name="Tipo Base do Projeto"
    )

    # Localização aplicável
    county = models.ForeignKey(
        County,
        on_delete=models.PROTECT,
        related_name='modelos_projeto',
        verbose_name="County/Condado",
        help_text="County onde este modelo é aplicável"
    )
    builders_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('10000.00'))],
        verbose_name="Fee for Builders",
        help_text="Fee charged by the builder for this model"
    )

    area_construida_padrao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Área Construída Padrão (m²)",
        help_text="Área construída padrão (0 para terrenos)",
        default=Decimal('0.00')
    )

    # Informações técnicas
    especificacoes_padrao = models.TextField(
        verbose_name="Especificações Padrão",
        help_text="Especificações técnicas padrão para este modelo",
        blank=True
    )

    # Custos estimados
    custo_base_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Custo Base Estimado",
        help_text="Custo base estimado para este modelo"
    )

    custo_por_m2 = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Custo por m² (R$/m²)",
        help_text="Custo estimado por metro quadrado",
        null=True,
        blank=True
    )

    # Tempo estimado
    duracao_construcao_dias = models.IntegerField(
        verbose_name="Duração Estimada (dias)",
        help_text="Duração estimada da construção em dias",
        validators=[MinValueValidator(1)]
    )

    # Requisitos especiais
    requisitos_especiais = models.TextField(
        verbose_name="Requisitos Especiais",
        help_text="Requisitos especiais para este tipo de projeto",
        blank=True
    )

    regulamentacoes_county = models.TextField(
        verbose_name="Regulamentações do County",
        help_text="Regulamentações específicas do county para este modelo",
        blank=True
    )

    # Status e versioning
    versao = models.CharField(
        max_length=10,
        verbose_name="Versão",
        help_text="Versão do modelo (ex: 1.0, 1.1, 2.0)",
        default="1.0"
    ) 

    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Se este modelo está ativo para uso"
    )

    # Controle
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    created_by = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='models_created',
        verbose_name="Created by"
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Model of Project"
        verbose_name_plural = "Models of Projects"
        ordering = ['county', 'project_type', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['project_type']),
            models.Index(fields=['county']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.county.name}) v{self.versao}"

    @property
    def total_fases(self):
        """Retorna o total de fases deste modelo"""
        return self.phases.count()

    @property
    def total_tasks(self):
        """Retorna o total de tarefas em todas as fases"""
        return sum(phase.tasks.count() for phase in self.phases.all())

    @property
    def custo_calculado_por_m2(self):
        """Calcula custo por m² baseado no custo base e área"""
        if self.area_construida_padrao > 0:
            return self.custo_base_estimado / self.area_construida_padrao
        return Decimal('0.00')

    def can_be_used(self):
        """Verifica se o modelo pode ser usado para criar projetos"""
        return self.is_active and self.total_fases > 0

    def duplicate_model(self, new_name, new_county=None):
        """Creates a copy of this model for another county or version"""
        new_model = ModelProject.objects.create(
            name=new_name,
            code=f"{self.code}_COPY",
            project_type=self.project_type,
            county=new_county or self.county,
            builders_fee=self.builders_fee,
            area_construida_padrao=self.area_construida_padrao,
            especificacoes_padrao=self.especificacoes_padrao,
            custo_base_estimado=self.custo_base_estimado,
            custo_por_m2=self.custo_por_m2,
            duracao_construcao_dias=self.duracao_construcao_dias,
            requisitos_especiais=self.requisitos_especiais,
            versao="1.0"
        )

        # Copiar fases e tarefas
        for phase in self.phases.all():
            new_phase = phase.duplicate_to_model(new_model)

        return new_model
