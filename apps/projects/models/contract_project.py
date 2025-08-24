from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from projects.models.project import Project
from apps.contracts.models.contract import Contract
from django.utils import timezone


class ContractProject(models.Model):
    """
    Model intermediário entre Contrato e Projeto
    Permite que um contrato tenha múltiplos projetos com preços específicos
    """

    # Relacionamentos principais
    # Um contrato pode ter vários projetos associados -- se um projeto tem contrato
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='contract_projects',
        verbose_name="Contract"
    )
    # Um projeto pode estar vinculado a vários contratos
    # (embora na prática seja comum um projeto estar em apenas um contrato)
    # Isso permite flexibilidade para customizações de preços por contrato
    # e também para casos onde um projeto pode ser vendido em diferentes condições
    # (ex: pré-venda, venda normal, etc.)
    # -- se um contrato tem projeto
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_contracts',
        verbose_name="Project"
    )
    # Observações específicas
    observacoes_especificas = models.TextField(
        verbose_name="Observações Específicas",
        help_text="Observações específicas desta venda (customizações, condições especiais, etc.)",
        blank=True
    )

    # Datas importantes
    data_vinculacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Vinculação",
        help_text="Data em que o projeto foi vinculado ao contrato"
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

    class Meta:
        verbose_name = "Contract-Project"
        verbose_name_plural = "Contracts-Projects"
        # Um projeto só pode estar em um contrato
        unique_together = ['contract', 'project']
        ordering = ['contract', 'project__model_project__code']
        indexes = [
            models.Index(fields=['contract']),
            models.Index(fields=['project']),
            models.Index(fields=['data_vinculacao']),
            models.Index(fields=['preco_venda_unidade']),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} → {self.project.model_project}"

    @property
    def dias_desde_vinculacao(self):
        """Calcula quantos dias desde a vinculação"""
        if self.data_vinculacao is None:
            # Padrão: retorna None para indicar ausência de valor
            return None
        return (timezone.now() - self.data_vinculacao).days

    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError

        # Verifica se o projeto pertence a mesma incorporação do contrato
        if (self.project and self.contract and
                self.project.incorporation != self.contract.incorporation):
            raise ValidationError(
                "O projeto deve pertencer a mesma incorporação do contrato."
            )

        # Calcula desconto automático se percentual foi informado
        if self.percentual_desconto > 0:
            desconto_calculado = (
                self.preco_venda_unidade * self.percentual_desconto) / 100
            if abs(self.desconto_aplicado - desconto_calculado) > Decimal('0.01'):
                self.desconto_aplicado = desconto_calculado

    def save(self, *args, **kwargs):
        """Override save para aplicar validações"""
        self.clean()
        super().save(*args, **kwargs)
