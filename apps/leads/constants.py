# apps/leads/constants.py
"""
Constantes e enums para o módulo Leads
"""
from django.db import models


class ConversionStatus(models.TextChoices):
    """
    Status de conversão Lead → Contract
    Usado para tracking interno, não salvo no banco
    """
    SUCCESS = 'SUCCESS', 'Converted Successfully'
    FAILED = 'FAILED', 'Conversion Failed'
    PARTIAL = 'PARTIAL', 'Partially Converted'


# Constantes para validação
VALID_MANAGEMENT_COMPANIES = [
    'L. Lira',
    'H & S'
]

CONVERTIBLE_LEAD_STATUSES = [
    'PENDING',
    'QUALIFIED'
]

# Status codes para busca no banco
DEFAULT_CONTRACT_STATUS_CODES = [
    'ACTIVE',
    'ATIVO', 
    'SIGNED',
    'ASSINADO'
]

CONVERTED_LEAD_STATUS_CODES = [
    'CONVERTED',
    'CONVERTIDO'
]