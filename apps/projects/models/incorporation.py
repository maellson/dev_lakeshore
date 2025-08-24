from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import County
from simple_history.models import HistoricalRecords
from projects.models.choice_types import IncorporationStatus, IncorporationType

User = get_user_model()


class Incorporation(models.Model):
    """
    Model para incorporações - o que será construído (criado ANTES das vendas)
    Pode ser desde um terreno individual até um condomínio complexo
    """

    # Identificação básica
    name = models.CharField(
        max_length=200,
        verbose_name="name of Incorporation",
        help_text="Ex: Condomínio Vila Bella, Casa dos Santos, Lote 45"
    )

    incorporation_type = models.ForeignKey(
        IncorporationType,
        on_delete=models.RESTRICT,
        verbose_name="Type of Incorporation",
        help_text="Type of incorporation (e.g. Land Development, Residential Complex, etc.)"
    )

    county = models.ForeignKey(
        County,
        on_delete=models.RESTRICT,
        related_name='incorporations',
        verbose_name="County/Condado"
    )

    # Descrição e planejamento
    project_description = models.TextField(
        verbose_name="Project Description",
        help_text="Detailed description of what will be built",
        blank=True
    )
    # Datas importantes
    launch_date = models.DateField(
        verbose_name="Launch Date",
        help_text="Launch date for sales",
        null=True,
        blank=True
    )

    # Status e controle
    incorporation_status = models.ForeignKey(
        IncorporationStatus,
        on_delete=models.RESTRICT,
        verbose_name="Status of Incorporation",
        help_text="Current status of the incorporation"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Incorporation",
        help_text="Indicates if the incorporation is currently active"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name="Created By",
        help_text="User who created this incorporation",
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Incorporation"
        verbose_name_plural = "Incorporations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['incorporation_type']),
            models.Index(fields=['incorporation_status']),
            models.Index(fields=['county']),
            models.Index(fields=['launch_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.incorporation_type})"

    @property
    def total_projects(self):
        """Retorna o total de projetos (unidades) neste empreendimento"""
        return self.projects.count()

    @property
    def projects_sold(self):
        """Retorna quantos projetos já foram vendidos"""
        return self.projects.filter(project_contracts__isnull=False).count()

    @property
    def sold_percentage(self):
        """Calcula o percentual de projetos vendidos"""
        total = self.total_projects
        if total == 0:
            return 0
        return (self.projects_sold / total) * 100

    def can_start_sales(self):
        """Verifica se o empreendimento pode iniciar vendas"""
        return self.incorporation_status == 'PLANNING' and self.total_projects > 0


#TODO: mudar o nome para ProjectGroup -- 