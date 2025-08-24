# apps/core/serializers.py
from rest_framework import serializers
from .models import County, HOA, Realtor


class CountyChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices de County"""

    class Meta:
        model = County
        fields = ['id', 'name', 'code', 'state']
        ref_name = "CoreCountyChoice"

    def to_representation(self, instance):
        """Customizar saída para ser mais user-friendly"""
        data = super().to_representation(instance)
        # Adicionar campo display_name para forms
        data['display_name'] = f"{instance.name}, {instance.state}"
        return data


class CountyDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para County"""

    class Meta:
        model = County
        fields = [
            'id',
            'name',
            'code',
            'state',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HOAChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices de HOA"""

    county_name = serializers.CharField(source='county.name', read_only=True)

    class Meta:
        model = HOA
        fields = ['id', 'name', 'county',
                  'county_name', 'has_special_permit_rules']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['display_name'] = f"{instance.name} ({instance.county.name})"
        return data


class HOAListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de HOAs"""
    
    county_name = serializers.CharField(source='county.name', read_only=True)
    
    class Meta:
        model = HOA
        fields = [
            'id', 'name', 'county', 'county_name',
            'has_special_permit_rules', 'is_active', 'created_at'
        ]


class HOADetailSerializer(serializers.ModelSerializer):
    """Serializer completo para HOA"""
    
    county = CountyChoiceSerializer(read_only=True)
    
    class Meta:
        model = HOA
        fields = [
            'id', 'name', 'county', 'has_special_permit_rules',
            'permit_requirements', 'contact_info', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HOACreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e atualização de HOA"""
    
    class Meta:
        model = HOA
        fields = [
            'name', 'county', 'has_special_permit_rules',
            'permit_requirements', 'contact_info', 'is_active'
        ]
        
    def validate_name(self, value):
        """Validar se o nome não está duplicado no mesmo county"""
        county = self.initial_data.get('county')
        if county:
            if self.instance:
                # Atualização - excluir o próprio registro da verificação
                if HOA.objects.exclude(pk=self.instance.pk).filter(
                    name=value, county=county
                ).exists():
                    raise serializers.ValidationError(
                        "Já existe um HOA com este nome neste county."
                    )
            else:
                # Criação - verificar se já existe
                if HOA.objects.filter(name=value, county=county).exists():
                    raise serializers.ValidationError(
                        "Já existe um HOA com este nome neste county."
                    )
        return value

class RealtorChoiceSerializer(serializers.ModelSerializer):
    """Serializer para choices de Realtor"""

    class Meta:
        model = Realtor
        fields = ['id', 'name', 'email', 'phone']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['display_name'] = f"{instance.name} ({instance.email})"
        return data


class RealtorListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de Realtors"""
    
    counties_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Realtor
        fields = [
            'id', 'name', 'email', 'phone',
            'default_commission_rate', 'is_active',
            'counties_count', 'created_at'
        ]
        
    def get_counties_count(self, obj):
        return obj.usually_works_in.count()


class RealtorDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para Realtor"""
    
    usually_works_in = CountyChoiceSerializer(many=True, read_only=True)
    counties_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Realtor
        fields = [
            'id', 'name', 'email', 'phone',
            'default_commission_rate', 'usually_works_in',
            'counties_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def get_counties_count(self, obj):
        return obj.usually_works_in.count()


class RealtorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e atualização de Realtor"""
    
    class Meta:
        model = Realtor
        fields = [
            'name', 'email', 'phone',
            'default_commission_rate', 'usually_works_in',
            'is_active'
        ]
        
    def validate_name(self, value):
        """Validar se o nome não está duplicado"""
        if self.instance:
            # Atualização - excluir o próprio registro da verificação
            if Realtor.objects.exclude(pk=self.instance.pk).filter(name=value).exists():
                raise serializers.ValidationError("Já existe um realtor com este nome.")
        else:
            # Criação - verificar se já existe
            if Realtor.objects.filter(name=value).exists():
                raise serializers.ValidationError("Já existe um realtor com este nome.")
        return value

