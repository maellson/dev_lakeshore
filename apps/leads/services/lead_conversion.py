# apps/leads/services.py
from dataclasses import dataclass
from typing import Optional, List
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from projects.models import Contract, Incorporation
from projects.models.choice_types import PaymentMethod, StatusContract
from leads.models.lead_types import StatusChoice

# Importar constantes
from ..constants import (
    ConversionStatus,
    VALID_MANAGEMENT_COMPANIES,
    DEFAULT_CONTRACT_STATUS_CODES,
    CONVERTED_LEAD_STATUS_CODES
)

from django.contrib.auth.models import AbstractBaseUser


User = get_user_model()


@dataclass
class ConversionResult:
    """
    Resultado estruturado da conversão Lead → Contract
    
    Attributes:
        success: Se a conversão foi bem-sucedida
        contract: Contract criado (None se falhou)
        errors: Lista de erros críticos
        warnings: Lista de avisos não-críticos
        lead_updated: Se o lead foi atualizado
    """
    success: bool
    status: ConversionStatus = ConversionStatus.FAILED  # ← Usar enum
    contract: Optional[Contract] = None
    errors: List[str] = None
    warnings: List[str] = None
    lead_updated: bool = False
    
    def __post_init__(self):
        """Inicializa listas vazias se None"""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class LeadConversionService:
    """
    Service para conversão de Lead em Contract
    
    BUSINESS LOGIC:
    - Valida se lead pode ser convertido
    - Cria contract com dados mínimos necessários
    - Atualiza status do lead
    - Mantém transação atômica
    - Retorna resultado estruturado
    """
    @classmethod
    def _validate_management_company(cls, management_company: str, result: ConversionResult):
        """Valida usando constante importada"""
        if management_company not in VALID_MANAGEMENT_COMPANIES:
            result.errors.append(
                f"Invalid management company '{management_company}'. "
                f"Valid options: {', '.join(VALID_MANAGEMENT_COMPANIES)}"
            )
    
    @classmethod
    def _get_default_contract_status(cls, result: ConversionResult):
        """Busca usando códigos das constantes"""
        default_status = StatusContract.objects.filter(
            code__in=DEFAULT_CONTRACT_STATUS_CODES,
            is_active=True
        ).first()
    
    @classmethod
    @transaction.atomic
    def convert_lead_to_contract(
        cls,
        lead,
        incorporation_id: int,
        management_company: str,
        payment_method_id: int,
        user: AbstractBaseUser
    ) -> ConversionResult:
        """
        Converte Lead qualificado em Contract ativo
        
        Args:
            lead: Lead a ser convertido
            incorporation_id: ID da incorporação
            management_company: "L. Lira" ou "H & S"
            payment_method_id: ID do método de pagamento
            user: Usuário responsável pela conversão
            
        Returns:
            ConversionResult com sucesso/erro + dados
            
        Raises:
            ValidationError: Em caso de dados inválidos
        """
        
        # Inicializar resultado
        result = ConversionResult(success=False)
        
        try:
            # ====================================
            # 1. VALIDAÇÕES CRÍTICAS
            # ====================================
            cls._validate_lead_for_conversion(lead, result)
            cls._validate_incorporation(incorporation_id, result)
            cls._validate_payment_method(payment_method_id, result)
            cls._validate_management_company(management_company, result)
            cls._validate_user(user, result)
            
            # Se há erros críticos, abortar
            if result.errors:
                return result
            
            # ====================================
            # 2. BUSCAR OBJETOS RELACIONADOS
            # ====================================
            incorporation = Incorporation.objects.get(
                id=incorporation_id, is_active=True
            )
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id, is_active=True
            )
            
            # Buscar status padrão para contratos novos
            default_contract_status = cls._get_default_contract_status(result)
            if not default_contract_status:
                return result
            
            # ====================================
            # 3. CRIAR CONTRACT
            # ====================================
            contract = Contract.objects.create(
                lead=lead,
                incorporation=incorporation,
                management_company=management_company,
                payment_method=payment_method,
                status_contract=default_contract_status,
                created_by=user
                # contract_value será preenchido automaticamente via save()
            )
            
            result.contract = contract
            
            # ====================================
            # 4. ATUALIZAR LEAD STATUS
            # ====================================
            converted_status = cls._get_converted_lead_status(result)
            if converted_status:
                lead.status = converted_status
                lead.converted_at = timezone.now()
                lead.save()
                result.lead_updated = True
            
            # ====================================
            # 5. VALIDAÇÕES PÓS-CRIAÇÃO
            # ====================================
            cls._validate_contract_creation(contract, result)
            
            # ====================================
            # 6. SUCESSO
            # ====================================
            result.success = True
            
            # Adicionar warnings informativos
            if contract.contract_value != lead.contract_value:
                result.warnings.append(
                    f"Contract value ({contract.contract_value}) differs from lead value ({lead.contract_value})"
                )
            
            return result
            
        except Exception as e:
            # ====================================
            # 7. TRATAMENTO DE ERROS
            # ====================================
            result.errors.append(f"Unexpected error during conversion: {str(e)}")
            result.success = False
            return result
    
    # ====================================
    # MÉTODOS PRIVADOS DE VALIDAÇÃO
    # ====================================
    
    @classmethod
    def _validate_lead_for_conversion(cls, lead, result: ConversionResult):
        """Valida se o lead pode ser convertido"""
        
        if not lead:
            result.errors.append("Lead is required")
            return
        
        if not lead.is_convertible:
            result.errors.append(
                f"Lead with status '{lead.status.name}' cannot be converted. "
                f"Only PENDING or QUALIFIED leads can be converted."
            )
        
        # Verificar se já tem contrato
        if hasattr(lead, 'contract') and lead.contract.exists():
            result.errors.append(
                f"Lead {lead.id} already has a contract ({lead.contract.first().contract_number})"
            )
        
        # Verificar campos obrigatórios
        if not lead.contract_value or lead.contract_value <= 0:
            result.errors.append("Lead must have a valid contract value")
        
        if not lead.county:
            result.warnings.append("Lead has no county specified")
    
    @classmethod
    def _validate_incorporation(cls, incorporation_id: int, result: ConversionResult):
        """Valida se a incorporação existe e está ativa"""
        
        if not incorporation_id:
            result.errors.append("Incorporation ID is required")
            return
        
        try:
            incorporation = Incorporation.objects.get(id=incorporation_id)
            if not incorporation.is_active:
                result.errors.append(f"Incorporation '{incorporation.name}' is not active")
                
        except Incorporation.DoesNotExist:
            result.errors.append(f"Incorporation with ID {incorporation_id} not found")
    
    @classmethod
    def _validate_payment_method(cls, payment_method_id: int, result: ConversionResult):
        """Valida se o método de pagamento existe e está ativo"""
        
        if not payment_method_id:
            result.errors.append("Payment method ID is required")
            return
        
        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            if not payment_method.is_active:
                result.errors.append(f"Payment method '{payment_method.name}' is not active")
                
        except PaymentMethod.DoesNotExist:
            result.errors.append(f"Payment method with ID {payment_method_id} not found")
    
    @classmethod
    def _validate_management_company(cls, management_company: str, result: ConversionResult):
        """Valida se a empresa de gestão é válida"""
        
        valid_companies = ['L. Lira', 'H & S']
        
        if not management_company:
            result.errors.append("Management company is required")
            return
        
        if management_company not in valid_companies:
            result.errors.append(
                f"Invalid management company '{management_company}'. "
                f"Valid options: {', '.join(valid_companies)}"
            )
    
    @classmethod
    def _validate_user(cls, user: AbstractBaseUser, result: ConversionResult):
        """Valida se o usuário pode criar contratos"""
        
        if not user:
            result.errors.append("User is required for contract creation")
            return
        
        if not user.is_active:
            result.errors.append("User must be active to create contracts")
        
        # Validação de permissão (opcional)
        if not user.has_perm('projects.add_contract'):
            result.warnings.append(
                f"User {user.email} may not have permission to create contracts"
            )
    
    @classmethod
    def _get_default_contract_status(cls, result: ConversionResult):
        """Busca status padrão para contratos novos"""
        
        try:
            # Assumindo que existe um status "ATIVO" ou similar
            # Você pode ajustar conforme seus status reais
            default_status = StatusContract.objects.filter(
                code__in=['ACTIVE', 'ATIVO', 'SIGNED'], 
                is_active=True
            ).first()
            
            if not default_status:
                # Fallback: primeiro status ativo
                default_status = StatusContract.objects.filter(is_active=True).first()
            
            if not default_status:
                result.errors.append("No active contract status found in system")
                return None
            
            return default_status
            
        except Exception as e:
            result.errors.append(f"Error finding default contract status: {str(e)}")
            return None
    
    @classmethod
    def _get_converted_lead_status(cls, result: ConversionResult):
        """Busca status 'CONVERTED' para leads"""
        
        try:
            converted_status = StatusChoice.objects.filter(
                code__in=['CONVERTED', 'CONVERTIDO'],
                is_active=True
            ).first()
            
            if not converted_status:
                result.warnings.append("No 'CONVERTED' status found for leads")
                return None
            
            return converted_status
            
        except Exception as e:
            result.warnings.append(f"Error finding converted lead status: {str(e)}")
            return None
    
    @classmethod
    def _validate_contract_creation(cls, contract: Contract, result: ConversionResult):
        """Valida se o contrato foi criado corretamente"""
        
        if not contract.contract_number:
            result.warnings.append("Contract number was not generated")
        
        if not contract.contract_value or contract.contract_value <= 0:
            result.warnings.append("Contract value is zero or empty")
        
        # Verificar se o save() funcionou corretamente
        try:
            contract.refresh_from_db()
        except Exception as e:
            result.errors.append(f"Failed to verify contract creation: {str(e)}")