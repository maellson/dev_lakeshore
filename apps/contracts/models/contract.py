from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from leads.models import Lead
from simple_history.models import HistoricalRecords
from ...projects.models.incorporation import Incorporation
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()


class Contract(models.Model):
    """
    Model para contratos - ponte comercial entre leads e empreendimentos
    Um contrato pode ter múltiplos proprietários e múltiplos projetos
    """

    # Identificação única
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Contrato",
        help_text="Número único do contrato (gerado automaticamente se vazio)",
        blank=True
    )

    # Relacionamentos principais
    lead = models.ForeignKey(
        Lead,
        on_delete=models.PROTECT,
        related_name='contract',
        verbose_name="Lead Origem",
        help_text="Lead que originou este contrato",
        # A lógica de negócio para conversão é tratada no LeadConversionService
    )

    incorporation = models.ForeignKey(
        Incorporation,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name="Incorporation",
        help_text="Incorporation associated with this contract",
    )

    # Informações financeiras
    contract_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Contract Value",
        help_text="Total value of all units in the contract - this value comes from the lead - automatically updated when the contract is created",
    )

    management_company = models.CharField(
        max_length=50,
        choices=[
            ('L. Lira', 'L. Lira'),
            ('H & S', 'H & S')
        ],
        default='L. Lira',
        verbose_name="Type of Management",
        help_text="Type of management for this contract"
    )

    payment_method = models.ForeignKey(
        'projects.PaymentMethod',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name="Forma de Pagamento"
    )

    sign_date = models.DateField(
        verbose_name="Signature Date",
        help_text="Signature date of the contract (when it was signed)",
        blank=True,
        null=True
    )
    payment_date = models.DateField(
        verbose_name="Payment Date",
        help_text="Payment date of the contract",
        null=True,
        blank=True
    )

    # Status e controle
    status_contract = models.ForeignKey(
        'projects.StatusContract',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name="Status do Contrato"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Created date of the contract"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
        help_text="Date of the last update"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name="Created By",
        help_text="User who created this contract"
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        ordering = ['-sign_date']
        indexes = [
            models.Index(fields=['contract_number']),
            models.Index(fields=['status_contract']),
            models.Index(fields=['sign_date']),
            models.Index(fields=['incorporation']),
            models.Index(fields=['lead']),
        ]

    def __str__(self):
        return f"Contrato {self.contract_number} - {self.incorporation.name}"

    def save(self, *args, **kwargs):
        """
        Gera número do contrato e preenche o valor do contrato a partir do lead.
        """
        # Preenche o valor do contrato a partir do lead associado
        if self.lead and self.lead.contract_value:
            self.contract_value = self.lead.contract_value

        # Gera número do contrato automaticamente se não fornecido
        if not self.contract_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d")
            unique_id = str(uuid.uuid4())[:8].upper()
            self.contract_number = f"CT-{timestamp}-{unique_id}"

        super().save(*args, **kwargs)

    @property
    def total_owners(self):
        """Retorna o número total de proprietários do contrato"""
        return self.owners.count()

    @property
    def total_projects(self):
        """Retorna o número total de projetos no contrato"""
        return self.contract_projects.count()

    @property
    def valor_medio_projeto(self):
        """Calcula o valor médio por projeto no contrato"""
        total_projetos = self.total_projects
        if total_projetos == 0:
            return Decimal('0.00')
        return self.contract_value / total_projetos

    def pode_cancelar(self):
        """Verifica se o contrato pode ser cancelado"""
        return self.status_contract == 'ATIVO'




