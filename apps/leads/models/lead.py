# apps/leads/models/lead.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from core.models import County, Realtor, HOA
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from projects.models.model_project import ModelProject
from leads.models.lead_types import StatusChoice, ElevationChoice


User = get_user_model()


class Lead(models.Model):
    """
    Lead de cliente potencial - captura inicial de dados

    BUSINESS LOGIC:
    - Primeira entrada do cliente no sistema
    - Dados coletados via formulário web público
    - Pipeline: PENDING → QUALIFIED → CONVERTED/REJECTED
    - Source para criação de contratos
    - Métricas de conversão de marketing
    """
    # ======================
    # CLIENT INFORMATION
    # ======================
    client_company_name = models.CharField(
        max_length=200,
        verbose_name="Client Company Name",
        help_text="Company name if client is a business"
    )
    client_full_name = models.CharField(
        max_length=200,
        verbose_name="Client Full Name",
        help_text="Full name of primary contact"
    )
    client_phone = PhoneNumberField(
        verbose_name="Client Phone",
        help_text="Primary phone number",
        blank=True
    )
    client_email = models.EmailField(
        verbose_name="Client Email",
        help_text="Primary email address"
    )
    note = models.TextField(
        blank=True,
        verbose_name="Additional Notes",
        help_text="Optional notes or special instructions"
    )
    realtor_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Realtor Name",
        help_text="Name of the realtor (if applicable)"
    )
    realtor_phone = PhoneNumberField(
        verbose_name="Realtor Phone",
        help_text="Phone number of the realtor (if applicable)",
        blank=True
    )
    realtor_email = models.EmailField(
        verbose_name="Realtor Email",
        help_text="Email address of the realtor (if applicable)",
        blank=True
    )
    # ======================
    # REALTOR INFORMATION
    # ======================
    is_realtor = models.BooleanField(
        verbose_name="Is Realtor Involved",
        help_text="Whether there is a realtor involved in this deal"
    )
    realtor = models.ForeignKey(
        Realtor,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        verbose_name="Realtor",
        help_text="Realtor involved in this deal (if applicable)"
    )
    # ======================
    # PROPERTY INFORMATION
    # ======================
    state = models.CharField(
        max_length=2,
        default='FL',
        verbose_name="State",
        help_text="Property state (default: Florida)"
    )
    county = models.ForeignKey(
        County,
        on_delete=models.RESTRICT,
        verbose_name="County",
        help_text="County where property is located"
    )
    parcel_id = models.CharField(
        max_length=50,
        verbose_name="Parcel ID",
        help_text="Property parcel identification number"
    )
    house_model = models.ForeignKey(
        ModelProject,
        on_delete=models.RESTRICT,
        limit_choices_to={'is_active': True},
        verbose_name="House Model",
        help_text="Selected house model type",
    )
    other_model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Other Model Name",
        help_text="Custom model name if 'Other' is selected"
    )
    elevation = models.ForeignKey(
        ElevationChoice,
        on_delete=models.RESTRICT,
        related_name='leads',
        verbose_name="House Elevation",
        help_text="Elevation specification for the house"
    )
    has_hoa = models.BooleanField(
        verbose_name="Has HOA/Association",
        # associacao demoradores se sim, gatilho para permit especifica
        help_text="Whether property has HOA or association"
    )
    hoa_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="HOA Name",
        help_text="Name of the Homeowners Association (if applicable)"
    )
    hoa = models.ForeignKey(
        HOA,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name="HOA",
        help_text="Homeowners Association (if applicable)"
    )
    contract_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1000.00'))],
        verbose_name="Contract Value",
        help_text="Expected contract value in USD"
    )
    # ======================
    # WORKFLOW & METADATA
    # ======================
    status = models.ForeignKey(
        StatusChoice,
        on_delete=models.RESTRICT,
        default=1,  # Assumindo que 1 é o ID do status PENDING no banco de dados
        related_name='leads',
        verbose_name="Lead Status",
        help_text="Current status in the lead pipeline"
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
        help_text="User who created this lead",
        blank=True,
        null=True
    )
    # Conversion tracking
    converted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Converted At",
        help_text="When lead was converted to contract"
    )
    history = HistoricalRecords(inherit=True)
    class Meta:
        # app_label = ''
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['county', 'status']),
            models.Index(fields=['client_email']),
        ]

    def __str__(self):
        return f"{self.client_full_name} - {self.county.name} ({self.status.name})"

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError

        # VALIDAÇÃO CRÍTICA: HOA no mesmo county
        if self.has_hoa and self.hoa and self.county:
            if self.hoa.county != self.county:
                raise ValidationError({
                    'hoa': f'HOA "{self.hoa.name}" is from {self.hoa.county.name} county, '
                    f'but property is in {self.county.name} county. '
                    f'HOA and property must be in the same county.'
                })

        # Para status QUALIFIED, validar objetos FK
        if self.status and self.status.code == 'QUALIFIED':
            if self.is_realtor and not self.realtor:
                raise ValidationError({
                    'realtor': 'Realtor object is required for qualified leads with realtor involvement.'
                })

            if self.has_hoa and not self.hoa:
                raise ValidationError({
                    'hoa': 'HOA object is required for qualified leads with HOA involvement.'
                })

        # Se house_model é 'Other', other_model é obrigatório
        if self.house_model == 'Other' and not self.other_model:
            raise ValidationError({
                'other_model': 'Other model name is required when "Other" is selected.'
            })

        # Se house_model não é 'Other', other_model deve estar vazio
        if self.house_model != 'Other' and self.other_model:
            raise ValidationError({
                'other_model': 'Other model name should only be filled when "Other" is selected.'
            })

    def save(self, *args, **kwargs):
        # Executar validações antes de salvar
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_convertible(self):
        """Verifica se lead pode ser convertido para contrato"""
        return self.status.code in ['PENDING', 'QUALIFIED']

    @property
    def days_since_created(self):
        """Quantos dias desde criação - com proteção para None"""
        from django.utils import timezone
        if not self.created_at:
            return 0
        return (timezone.now() - self.created_at).days

    def mark_as_converted(self, user=None):
        """Marca lead como convertido"""
        from django.utils import timezone
        try:
            converted_status = StatusChoice.objects.get(code='CONVERTED')
            self.status = converted_status
            self.converted_at = timezone.now()
            self.save()
        except StatusChoice.DoesNotExist:
            # Lidar com o caso em que o status 'CONVERTED' não existe
            # Isso pode ser um log, uma exceção, etc.
            # Por enquanto, vamos apenas evitar que o código quebre.
            pass

    def get_display_model(self):
        """Retorna o modelo a ser exibido (considerando Other)"""
        if self.house_model == 'Other':
            return self.other_model
        return self.house_model
