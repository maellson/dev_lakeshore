"""
Choice Types específicos para o módulo Projects
Design Pattern: Factory + Strategy (seguindo padrão do sistema)
"""
from django.db import models
from core.models.base import ChoiceTypeBase


class ProjectType(ChoiceTypeBase):
    """Tipos de projeto disponíveis"""

    class Meta:
        verbose_name = 'Type Project'
        verbose_name_plural = 'Types Projects'
        db_table = 'projects_type_project'


class ProjectStatus(ChoiceTypeBase):
    """Status dos projetos"""

    class Meta:
        verbose_name = 'Status of Project'
        verbose_name_plural = 'Status of Projects'
        db_table = 'projects_status_project'


class IncorporationStatus(ChoiceTypeBase):
    """Status of Incorporation"""

    class Meta:
        verbose_name = 'Status of Incorporation'
        verbose_name_plural = 'Status of Incorporations'
        db_table = 'projects_status_incorporacao'


class IncorporationType(ChoiceTypeBase):
    """Types of Incorporation"""

    class Meta:
        verbose_name = 'Type of Incorporation'
        verbose_name_plural = 'Types of Incorporation'
        db_table = 'projects_tipo_incorporacao'


class StatusContract(ChoiceTypeBase):
    """Status of Contracts"""

    class Meta:
        verbose_name = 'Status of Contract'
        verbose_name_plural = 'Status of Contracts'
        db_table = 'projects_status_contract'


class PaymentMethod(ChoiceTypeBase):
    """Formas de pagamento disponíveis"""

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        db_table = 'projects_payment_method'


class ProductionCell(ChoiceTypeBase):
    """Células de produção - usadas para identificar áreas de trabalho específicas"""

    class Meta:
        verbose_name = 'Production Cell'
        verbose_name_plural = 'Production Cells'
        db_table = 'projects_production_cell'


class OwnerType(ChoiceTypeBase):
    """Tipos de proprietário - para contratos e projetos pode ser pessoa física ou jurídica"""

    class Meta:
        verbose_name = 'Owner Type'
        verbose_name_plural = 'Owner Types'
        db_table = 'projects_owner_type'

# Todo: Verificar com Ana sobre o uso de "Owner Type"  qual a terminologia usada nos EUA
#       Pode ser "Client Type" ou "Customer Type" dependendo do contexto

class ManagementCompany(ChoiceTypeBase):
    """Tipos de empresa de gestão - para contratos e projetos"""

    class Meta:
        verbose_name = 'Management Company'
        verbose_name_plural = 'Management Companies'
        db_table = 'projects_management_company'


"""
#projects:


    TIPO_CHOICES = [
        ('LAND', 'Land'),
        ('SIMPLE_HOUSE', 'Simple House'),
        ('TOWNHOUSE_BLOCK', 'Townhouse Block'),
        ('APARTMENT', 'Apartment'),
        ('INFRASTRUCTURE', 'Infrastructure'),
    ]
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    PRODUCTIONS_CELLS = [
        ('C1', 'C1'),
        ('C2', 'C2)'),
        ('C3', 'C3'),
     
    ]

#Incorporacao:

    TIPO_CHOICES = [
        ('LAND_DEVELOPMENT', 'Land Development'),
        ('BUILD_SIMPLE', 'Simple Build (Single House)'),
        ('TOWNHOUSE', 'Townhouse (Apartment Block)'),
        ('CONDOMINIUM', 'Condominium (Multiple Units)'),
    ]

    STATUS_CHOICES = [
        ('PLANNING', 'Em Planejamento'),
        ('SALES', 'Em Vendas'),
        ('CONSTRUCTION', 'Em Construção'),
        ('DELIVERED', 'Entregue'),
    ]
    
## CONTRATCTS


    STATUS_CHOICES = [
        ('ACTIVE', 'Ativo'),
        ('COMPLETED', 'Concluído'),
        ('CANCELLED', 'Cancelado'),
        ('PAYED', 'Pago'),
        ('UNPAYED', 'Não Pago'),
        ('SIGNED', 'Assinado'),
        ('SIGNED_PAYED', 'Assinado e Pago'),#CASO NÃO APLICADA A ORDEN DAS CHOICES
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('CASH', 'À Vista'),
        ('FINANCED', 'Financiado'),
        ('INSTALMENTS', 'Parcelado'),
        ('DRAWS', 'Draws (Por Etapas)'),
    ]
## TypeOwner
    
    TIPO_CHOICES = [
        ('PRINCIPAL', 'Proprietário Principal'),
        ('CONJUGE', 'Cônjuge'),
        ('INVESTIDOR', 'Investidor'),
        ('EMPRESA', 'Pessoa Jurídica'),
        ('HERDEIRO', 'Herdeiro'),
        ('PROCURADOR', 'Procurador'),
    ]
        

"""
