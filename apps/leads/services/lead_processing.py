# apps/leads/services/lead_processing.py
from django.core.exceptions import ValidationError
from django.db import transaction


class LeadProcessingService:

    @staticmethod
    def qualify_lead_with_associations(lead, realtor_obj=None, hoa_obj=None, user=None):
        """
        Qualifica uma lead associando os objetos corretos

        Args:
            lead: Lead instance
            realtor_obj: Realtor object (se is_realtor=True)
            hoa_obj: HOA object (se has_hoa=True) 
            user: User fazendo a operação
        """
        from django.core.exceptions import ValidationError
        from leads.models.lead_types import StatusChoice

        # Validações
        if lead.is_realtor and not realtor_obj:
            raise ValidationError(
                "Realtor object required for leads with realtor")

        if lead.has_hoa and not hoa_obj:
            raise ValidationError("HOA object required for leads with HOA")

        if hoa_obj and lead.county:
            if hoa_obj.county != lead.county:
                raise ValidationError(
                    f"HOA '{hoa_obj.name}' is from {hoa_obj.county.name} county, "
                    f"but the lead is for {lead.county.name} county. "
                    f"Please select an HOA from the correct county."
                )

        # Associar objetos
        if realtor_obj:
            lead.realtor = realtor_obj

        if hoa_obj:
            lead.hoa = hoa_obj

        # Mudar status
        try:
            qualified_status = StatusChoice.objects.get(code='QUALIFIED')
            lead.status = qualified_status
        except StatusChoice.DoesNotExist:
            raise ValidationError("QUALIFIED status not found in database")

        # Salvar com validação completa
        lead.full_clean()  # Executa validações do modelo
        # Salvar
        lead.save()

        return lead
    @staticmethod
    def find_hoas_by_county(county, name_filter=None):
        """Helper para buscar HOAs do county correto"""
        from core.models import HOA
        
        queryset = HOA.objects.filter(county=county, is_active=True)
        
        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)
            
        return queryset.order_by('name')

    @staticmethod
    def find_or_create_realtor(name, phone=None, email=None):
        """Busca ou cria realtor com base nos dados textuais"""
        from core.models import Realtor

        # Buscar por email primeiro (mais único)
        if email:
            realtor = Realtor.objects.filter(email=email).first()
            if realtor:
                return realtor

        # Buscar por nome + telefone
        if phone:
            realtor = Realtor.objects.filter(name=name, phone=phone).first()
            if realtor:
                return realtor

        # Criar novo se não encontrou
        return Realtor.objects.create(
            name=name,
            phone=phone or '',
            email=email or '',
            is_active=True
        )
    ## TODO: Testar aqui: adicionei aqui essas rotas para eu testar futuramente
    @staticmethod
    def find_similar_leads(lead, limit=5):
        """Busca leads similares para detectar duplicatas ou relacionados"""
        from leads.models import Lead
        from django.db.models import Q
        
        similar_leads = Lead.objects.filter(
            Q(client_email=lead.client_email) |
            Q(client_phone=lead.client_phone) |
            Q(parcel_id=lead.parcel_id) |
            Q(client_full_name=lead.client_full_name)
        ).exclude(id=lead.id).distinct()[:limit]
        
        return similar_leads
    
    @staticmethod
    def validate_lead_readiness_for_qualification(lead):
        """Valida se lead está pronto para qualificação"""
        errors = []
        warnings = []
        
        # Campos obrigatórios básicos
        if not lead.client_full_name:
            errors.append("Client name is required")
        
        if not lead.client_email and not lead.client_phone:
            errors.append("Either email or phone is required")
        
        if not lead.county:
            errors.append("County is required")
        
        if not lead.contract_value or lead.contract_value <= 0:
            errors.append("Valid contract value is required")
        
        # Validações de realtor
        if lead.is_realtor:
            if not lead.realtor_name:
                errors.append("Realtor name is required when realtor is involved")
            if not lead.realtor and not (lead.realtor_name and lead.realtor_email):
                warnings.append("Realtor object not assigned - will need manual association")
        
        # Validações de HOA
        if lead.has_hoa:
            if not lead.hoa_name:
                errors.append("HOA name is required when HOA is involved")
            if not lead.hoa and not lead.hoa_name:
                warnings.append("HOA object not assigned - will need manual association")
        
        return {
            'ready': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
