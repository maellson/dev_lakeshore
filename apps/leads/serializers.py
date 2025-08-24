# apps/leads/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import County, HOA, Realtor
from core.serializers import CountyChoiceSerializer, HOAChoiceSerializer
from .models import Lead
from leads.models.lead_types import StatusChoice

User = get_user_model()


class CountyChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices de County"""

    class Meta:
        model = County
        fields = ['id', 'name', 'code']
        ref_name = "LeadsCountyChoice"


class LeadListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de leads - campos resumidos

    USAGE:
    - Lista principal de leads
    - Dashboard/overview
    - Filtros e busca
    """

    county_name = serializers.CharField(source='county.name', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    days_old = serializers.IntegerField(
        source='days_since_created', read_only=True)
    display_model = serializers.CharField(
        source='get_display_model', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'client_full_name',
            'client_company_name',
            'client_email',
            'county_name',
            'display_model',
            'contract_value',
            'status',
            'status_display',
            'days_old',
            'created_at',
            'created_by_name',
            'is_convertible',
        ]


class LeadDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalhes de lead

    USAGE:
    - Visualização completa
    - Edição de lead
    - Conversão para contrato
    """

    # Related field displays
    county_name = serializers.CharField(source='county.name', read_only=True)
    county_info = CountyChoiceSerializer(source='county', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    elevation_display = serializers.CharField(
        source='get_elevation_display', read_only=True)
    display_model = serializers.CharField(
        source='get_display_model', read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name', read_only=True)

    # Computed fields
    days_old = serializers.IntegerField(
        source='days_since_created', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            # Client Information
            'client_company_name',
            'client_full_name',
            'client_phone',
            'client_email',
            'note',
            # Realtor Information
            'is_realtor',
            'realtor',
            'realtor_name',
            'realtor_phone',
            'realtor_email',
            # Property Information
            'state',
            'county',
            # os demais campos .. uwaauaauuu
            'county_name',
            'county_info',
            'parcel_id',
            'house_model',
            'other_model',
            'display_model',
            'elevation',
            'elevation_display',
            'has_hoa',
            'hoa_name',
            'hoa',
            'contract_value',
            # Workflow
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'converted_at',
            'created_by',
            'created_by_name',
            'days_old',
            'is_convertible',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'converted_at',
            'created_by',
        ]


class LeadCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de leads - formulário web público

    USAGE:
    - Formulário web de captura
    - API pública para leads
    - Validações específicas de criação
    """

    class Meta:
        model = Lead
        fields = [
            # Client Information
            'client_company_name',
            'client_full_name',
            'client_phone',
            'client_email',
            'note',
            # Realtor Information
            'is_realtor',
            'realtor_name',
            'realtor_phone',
            'realtor_email',
            'realtor',
            # Property Information
            'state',
            'county',
            # Us otooo"
            'parcel_id',
            'house_model',
            'other_model',
            'elevation',
            'has_hoa',
            'hoa_name',
            'hoa',
            'contract_value',
        ]

    def validate(self, data):
        """Validações customizadas para criação"""

        # Validar house_model vs other_model
        house_model = data.get('house_model')
        other_model = data.get('other_model', '')

        if house_model == 'Other' and not other_model:
            raise serializers.ValidationError({
                'other_model': 'Other model name is required when "Other" is selected.'
            })

        if house_model != 'Other' and other_model:
            raise serializers.ValidationError({
                'other_model': 'Other model name should only be filled when "Other" is selected.'
            })

        # Validar contract_value mínimo
        contract_value = data.get('contract_value')
        if contract_value and contract_value < 10000:
            raise serializers.ValidationError({
                # tentando evitar erros no preenchimento do campo
                'contract_value': 'Contract value must be at least $1,000.00'
            })

        # Validando o campo is realtor para cadastro dele no lead
        # VALIDAÇÃO REALTOR - campos textuais obrigatórios se is_realtor=True
        is_realtor = data.get('is_realtor', False)
        realtor_name = data.get('realtor_name', '').strip()
        realtor_phone = data.get('realtor_phone')
        realtor_email = data.get('realtor_email', '').strip()

        if is_realtor and not realtor_name:
            raise serializers.ValidationError({
                'realtor_name': 'Realtor name is required when "Is Realtor" is checked.'
            })

        if is_realtor and not realtor_phone:
            raise serializers.ValidationError({
                'realtor_phone': 'Realtor phone is required when "Is Realtor" is checked.'
            })

        if is_realtor and not realtor_email:
            raise serializers.ValidationError({
                'realtor_email': 'Realtor email is required when "Is Realtor" is checked.'
            })
        else:
            # Se não marcou is_realtor, limpar campos textuais
            data['realtor_name'] = ''
            data['realtor_phone'] = None
            data['realtor_email'] = ''
            data['realtor'] = None

        # is_realtor = data.get('is_realtor', False)
        realtor = data.get('realtor')

        """if is_realtor and not realtor:
            raise serializers.ValidationError({
                'realtor': 'Realtor is required when "Is Realtor" is checked.'
            })"""

        if not is_realtor and realtor:
            # Limpar realtor se não está marcado
            data['realtor'] = None

        # Validando o campo has_HOA para cadastro dele no lead
        has_hoa = data.get('has_hoa', False)
        hoa_name = data.get('hoa_name', '').strip()
        # hoa = data.get('hoa')

        if has_hoa:
            # Se marcou has_hoa, o campo textual é obrigatório
            if not hoa_name:
                raise serializers.ValidationError({
                    'hoa_name': 'HOA name is required when "Has HOA" is checked.'
                })
        else:
            # Se não marcou has_hoa, limpar campos
            data['hoa_name'] = ''
            data['hoa'] = None

        return data

    def create(self, validated_data):
        """Criação customizada - definir campos default"""
        # Status inicial sempre PENDING - buscar instância de StatusChoice

        try:
            pending_status = StatusChoice.objects.get(
                code='PENDING', is_active=True)
            validated_data['status'] = pending_status
        except StatusChoice.DoesNotExist:
            # Fallback para o primeiro status ativo se PENDING não existir
            first_status = StatusChoice.objects.filter(is_active=True).first()
            if first_status:
                validated_data['status'] = first_status

        # Created_by vem do context (request.user)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user

        return super().create(validated_data)


class LeadUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de leads

    USAGE:
    - Edição interna de leads
    - Mudança de status
    - Correções de dados
    """

    class Meta:
        model = Lead
        fields = [
            # Client Information
            'client_company_name',
            'client_full_name',
            'client_phone',
            'client_email',
            'note',
            # Realtor Information
            'is_realtor',
            'realtor',
            'realtor_name',
            'realtor_phone',
            'realtor_email',
            'has_hoa',
            'hoa_name',
            'hoa',
            # Property Information
            'state',
            'county',
            'parcel_id',
            'house_model',
            'other_model',
            'elevation',
            'contract_value',
            # Workflow (permitir mudança de status)
            'status',
        ]

    def validate_status(self, value):
        """Validar transições de status"""
        instance = self.instance

        if instance:
            # Não permitir voltar de CONVERTED - comparar por código
            if instance.status.code == 'CONVERTED' and (not hasattr(value, 'code') or value.code != 'CONVERTED'):
                raise serializers.ValidationError(
                    'Cannot change status from CONVERTED to another status.'
                )

        return value
    def validate(self, data):
        """Validações para ATUALIZAÇÃO - objetos FK podem ser obrigatórios"""

        # Pegar valores atuais ou novos
        instance = self.instance
        has_hoa = data.get('has_hoa', instance.has_hoa if instance else False)
        hoa_obj = data.get('hoa', instance.hoa if instance else None)
        county = data.get('county', instance.county if instance else None)
        new_status = data.get('status')
        
        # VALIDAÇÃO CRITICAL: HOA deve estar no mesmo county
        if has_hoa and hoa_obj and county:
            if hoa_obj.county != county:
                raise serializers.ValidationError({
                    'hoa': f'Selected HOA "{hoa_obj.name}" is not in the same county as the property. '
                           f'Please select an HOA from {county.name} county. '
                           f'Currently selected HOA is from {hoa_obj.county.name} county.'
                })
        
        # Se está mudando para QUALIFIED, validar objetos FK
        new_status = data.get('status')
        if new_status and hasattr(new_status, 'code') and new_status.code == 'QUALIFIED':
            
            # VALIDAÇÃO REALTOR PARA QUALIFIED
            is_realtor = data.get('is_realtor', self.instance.is_realtor if self.instance else False)
            realtor_obj = data.get('realtor', self.instance.realtor if self.instance else None)
            
            if is_realtor and not realtor_obj:
                raise serializers.ValidationError({
                    'realtor': 'Realtor object must be selected before qualifying the lead. '
                             'Please create/select the appropriate realtor from the database.'
                })
            
            # VALIDAÇÃO HOA PARA QUALIFIED
            has_hoa = data.get('has_hoa', self.instance.has_hoa if self.instance else False)
            hoa_obj = data.get('hoa', self.instance.hoa if self.instance else None)
            
            if has_hoa and not hoa_obj:
                raise serializers.ValidationError({
                    'hoa': 'HOA object must be selected before qualifying the lead. '
                          'Please create/select the appropriate HOA from the database.'
                })

        return data


class LeadConversionSerializer(serializers.Serializer):
    """
    Serializer para dados necessários na conversão Lead → Contract

    USAGE:
    - Endpoint de conversão
    - Preview de dados antes da conversão
    - Validação de dados para contrato
    """

    lead_id = serializers.IntegerField()
    contract_type = serializers.ChoiceField(
        choices=[
            ('STANDARD', 'Standard'),
            ('CUSTOM', 'Custom'),
            ('LAND', 'Land'),
        ],
        default='STANDARD'
    )
    additional_notes = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Additional notes for the contract"
    )

    def validate_lead_id(self, value):
        """Validar se lead existe e pode ser convertido"""
        try:
            lead = Lead.objects.get(id=value)
        except Lead.DoesNotExist:
            raise serializers.ValidationError('Lead not found.')

        if not lead.is_convertible:
            raise serializers.ValidationError(
                f'Lead with status "{lead.get_status_display()}" cannot be converted.'
            )

        return value

