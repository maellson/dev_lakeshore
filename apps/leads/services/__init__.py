# apps/leads/services/__init__.py

"""
Services para gerenciamento de leads

SERVICES DISPONÍVEIS:
- LeadConversionService: Conversão Lead → Contract  
- LeadProcessingService: Qualificação e associação de objetos
"""

from .lead_conversion import LeadConversionService, ConversionResult
from .lead_processing import LeadProcessingService

__all__ = [
    'LeadConversionService',
    'ConversionResult', 
    'LeadProcessingService',
]