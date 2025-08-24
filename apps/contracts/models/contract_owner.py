from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from django.core.validators import EmailValidator, RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal
from projects.models.choice_types import OwnerType
from phonenumber_field.modelfields import PhoneNumberField
from apps.contracts.models.contract import Contract
from django.db.models import Q

User = get_user_model()


class ContractOwner(models.Model):
    """
    Model para proprietários de um contrato
    Um contrato pode ter múltiplos proprietários com percentuais diferentes
    """

    # Relacionamento com contrato
    contract = models.ForeignKey(
        Contract,
        on_delete=models.RESTRICT,
        related_name='owners',
        verbose_name="Contract"
    )

    client = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.RESTRICT,
        related_name='contracts_as_owner',
        verbose_name="Client",
        help_text="Cliente que é proprietário neste contrato",
        limit_choices_to=Q(tipo_usuario__code='CLIENT') & Q(is_active=True)
        # limit_choices_to={'tipo_usuario__code': 'CLIENT'}  # Apenas clientes
    )

    # Participação no contrato
    percentual_propriedade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name="Percentual de Propriedade (%)",
        help_text="Percentual de participação no contrato (0.01 a 100.00)"
    )

    owner_type = models.ForeignKey(
        OwnerType,
        on_delete=models.RESTRICT,
        verbose_name="Tipo de Proprietário"
    )
    observations = models.TextField(
        verbose_name="Observations",
        help_text="Additional information about the owner",
        blank=True
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
        help_text="User who created this lead"
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Contract Owner"
        verbose_name_plural = "Contract Owners"
        ordering = ['-percentual_propriedade',
                    'client__first_name', 'client__last_name']
        # Mesmo doc_number não pode aparecer 2x no mesmo contrato
        unique_together = ['contract', 'client']
        indexes = [
            models.Index(fields=['contract']),
            models.Index(fields=['client']),
            models.Index(fields=['owner_type']),
        ]

    def __str__(self):
        return f"{self.client.get_full_name()} ({self.percentual_propriedade}%) - {self.contract.contract_number}"

    @property
    def nome_completo(self):
        return self.client.get_full_name()

    @property
    def email(self):
        return self.client.email

    @property
    def phone(self):
        return self.client.phone

    @property
    def address(self):
        return self.client.perfil_client.endereco_principal if hasattr(self.client, 'perfil_client') else None

    @property
    def valor_participacao(self):
        """Calcula o valor em dinheiro da participação do proprietário"""
        return (self.contract.valor_total_contrato * self.percentual_propriedade) / Decimal('100.00')

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError

        # Verifica se a soma dos percentuais do contrato não ultrapassa 100%
        if self.contract_id:
            total_percentual = ContractOwner.objects.filter(
                contract=self.contract
            ).exclude(id=self.id).aggregate(
                total=models.Sum('percentual_propriedade')
            )['total'] or Decimal('0.00')

            if total_percentual + self.percentual_propriedade > Decimal('100.00'):
                raise ValidationError(
                    f"Soma dos percentuais não pode ultrapassar 100%. "
                    f"Atual: {total_percentual}%, Tentando adicionar: {self.percentual_propriedade}%"
                )

