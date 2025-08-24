# account/choice_types.py
"""
Tipos de escolha específicos para o módulo Account
Design Pattern: Factory + Strategy
"""
from django.db import models
from core.models.base import ChoiceTypeBase


class TipoUsuario(ChoiceTypeBase):
    """Tipos de usuários do sistema"""

    class Meta:
        verbose_name = 'Tipo de Usuário'
        verbose_name_plural = 'Tipos de Usuários'
        db_table = 'account_tipo_usuario'


class Idioma(ChoiceTypeBase):
    """Idiomas disponíveis no sistema"""
    locale_code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Código de localização (pt-BR, en-US, es-ES)"
    )

    class Meta:
        verbose_name = 'Idioma'
        verbose_name_plural = 'Idiomas'
        db_table = 'account_idioma'


class NivelAcesso(ChoiceTypeBase):
    """Níveis de acesso hierárquicos"""
    nivel = models.PositiveIntegerField(
        unique=True,
        help_text="Nível hierárquico (1-5)"
    )

    class Meta:
        verbose_name = 'Nível de Acesso'
        verbose_name_plural = 'Níveis de Acesso'
        ordering = ['nivel']
        db_table = 'account_nivel_acesso'

    def __str__(self):
        return f"{self.nivel} - {self.name}"


class Cargo(ChoiceTypeBase):
    """Cargos disponíveis na empresa"""
    nivel_acesso = models.ForeignKey(
        NivelAcesso,
        on_delete=models.PROTECT,
        help_text="Nível de acesso associado a este cargo"
    )

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        db_table = 'account_cargo'


class Departamento(ChoiceTypeBase):
    """Departamentos da empresa"""
    responsavel = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departamentos_responsavel',
        help_text="Responsável pelo departamento"
    )

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        db_table = 'account_departamento'


class MetodoContato(ChoiceTypeBase):
    """Métodos de contato preferidos"""

    class Meta:
        verbose_name = 'Método de Contato'
        verbose_name_plural = 'Métodos de Contato'
        db_table = 'account_metodo_contato'


class FrequenciaAtualizacao(ChoiceTypeBase):
    """Frequências de atualização para clientes"""
    dias = models.PositiveIntegerField(
        help_text="Intervalo em dias"
    )

    class Meta:
        verbose_name = 'Frequência de Atualização'
        verbose_name_plural = 'Frequências de Atualização'
        db_table = 'account_frequencia_atualizacao'


class FonteClient(ChoiceTypeBase):
    """Como o cliente conheceu a empresa"""

    class Meta:
        verbose_name = 'Fonte do Cliente'
        verbose_name_plural = 'Fontes dos Clientes'
        db_table = 'account_fonte_cliente'


class CondicaoPagamento(ChoiceTypeBase):
    """Condições de pagamento para fornecedores"""
    prazo_dias = models.PositiveIntegerField(
        default=30,
        help_text="Prazo em dias para pagamento"
    )
    desconto_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Desconto para pagamento antecipado (%)"
    )

    class Meta:
        verbose_name = 'Condição de Pagamento'
        verbose_name_plural = 'Condições de Pagamento'
        db_table = 'account_condicao_pagamento'
