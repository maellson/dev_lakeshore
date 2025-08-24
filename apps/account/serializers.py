from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    CustomUser,
    PerfilInterno,
    PerfilSubcontratado,
    PerfilClient,
    PerfilFornecedor,
    PasswordResetToken,
    EmailVerificationToken
)

from .models import TipoUsuario, Idioma, MetodoContato, FrequenciaAtualizacao, FonteClient, CondicaoPagamento, NivelAcesso, Cargo, Departamento


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer customizado para JWT tokens com informações extras"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Converter objetos para strings serializáveis
        token['tipo_usuario'] = user.tipo_usuario.code if user.tipo_usuario else None
        token['preferencia_idioma'] = user.preferencia_idioma.code if user.preferencia_idioma else None
        token['nome_completo'] = user.get_full_name()

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Adicionar dados do usuário na resposta
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'nome_completo': self.user.get_full_name(),
            'tipo_usuario': self.user.tipo_usuario.code if self.user.tipo_usuario else None,
            'preferencia_idioma': self.user.preferencia_idioma.code if self.user.preferencia_idioma else None,
        }

        return data


class PerfilInternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilInterno
        exclude = ['user']


class PerfilSubcontratadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilSubcontratado
        exclude = ['user']


class PerfilClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilClient
        exclude = ['user']


class PerfilFornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilFornecedor
        exclude = ['user']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para visualizar perfil do usuário"""
    tipo_usuario_info = serializers.SerializerMethodField()
    idioma_info = serializers.SerializerMethodField()

    perfil_interno = PerfilInternoSerializer(read_only=True)
    perfil_subcontratado = PerfilSubcontratadoSerializer(read_only=True)
    perfil_client = PerfilClientSerializer(read_only=True)
    perfil_fornecedor = PerfilFornecedorSerializer(read_only=True)
    permissoes = serializers.SerializerMethodField()
    grupos = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'tipo_usuario_info', 'idioma_info', 'created_at',
            'last_login', 'perfil_interno', 'perfil_subcontratado',
            'perfil_client', 'perfil_fornecedor', 'permissoes', 'grupos'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']

    def get_tipo_usuario_info(self, obj):
        """Retorna dados completos do tipo de usuário"""
        if obj.tipo_usuario:
            return {
                'code': obj.tipo_usuario.code,
                'name': obj.tipo_usuario.name,
                'icon': obj.tipo_usuario.icon,
                'color': obj.tipo_usuario.color
            }
        return None

    def get_idioma_info(self, obj):
        """Retorna dados completos do idioma"""
        if obj.preferencia_idioma:
            return {
                'code': obj.preferencia_idioma.code,
                'name': obj.preferencia_idioma.name,
                'locale_code': obj.preferencia_idioma.locale_code
            }
        return None

    def get_permissoes(self, obj):
        """Retorna todas as permissões do usuário"""
        perms = obj.get_all_permissions()
        return list(perms)

    def get_grupos(self, obj):
        """Retorna grupos do usuário"""
        return [group.name for group in obj.groups.all()]


# Substituir no arquivo: account/serializers.py

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários com ForeignKeys"""
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    # Campos ForeignKey que aceitam tanto PK quanto código
    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.filter(is_active=True),
        help_text="ID do tipo de usuário (1, 2, 3, etc.)"
    )
    preferencia_idioma = serializers.PrimaryKeyRelatedField(
        queryset=Idioma.objects.filter(is_active=True),
        help_text="ID do idioma preferido (1, 2, 3, etc.)"
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone', 'tipo_usuario', 'preferencia_idioma',
            'password', 'password_confirm'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data):
        # Remover password_confirm dos dados
        validated_data.pop('password_confirm')

        # Criar usuário
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        """Customiza resposta para mostrar dados legíveis"""
        data = super().to_representation(instance)

        # Substituir IDs por dados legíveis na resposta
        if instance.tipo_usuario:
            data['tipo_usuario'] = {
                'id': instance.tipo_usuario.id,
                'code': instance.tipo_usuario.code,
                'name': instance.tipo_usuario.name
            }

        if instance.preferencia_idioma:
            data['preferencia_idioma'] = {
                'id': instance.preferencia_idioma.id,
                'code': instance.preferencia_idioma.code,
                'name': instance.preferencia_idioma.name
            }

        # Remover campos sensíveis da resposta
        data.pop('password', None)
        data.pop('password_confirm', None)

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitar reset de senha"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "Usuário com este email não encontrado.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar reset de senha"""
    token = serializers.UUIDField()
    password = serializers.CharField(validators=[validate_password])
    password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")

        # Validar token
        try:
            reset_token = PasswordResetToken.objects.get(token=attrs['token'])
            if not reset_token.is_valid():
                raise serializers.ValidationError(
                    "Token inválido ou expirado.")
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token não encontrado.")

        attrs['reset_token'] = reset_token
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualizar dados do usuário"""

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone', 'preferencia_idioma'
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer para verificar email através do token"""
    token = serializers.UUIDField()

    def validate_token(self, value):
        """Valida se o token de verificação é válido"""
        try:
            verification_token = EmailVerificationToken.objects.get(
                token=value)
            if not verification_token.is_valid():
                raise serializers.ValidationError(
                    "Token inválido ou expirado.")
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Token não encontrado.")

        return value

    def save(self):
        """Ativa o usuário e marca token como usado"""
        token_value = self.validated_data['token']
        verification_token = EmailVerificationToken.objects.get(
            token=token_value)

        # Ativar usuário
        user = verification_token.user
        user.is_active = True
        user.save()

        # Marcar token como usado
        verification_token.is_used = True
        verification_token.save()

        return user


class ResendEmailVerificationSerializer(serializers.Serializer):
    """Serializer para reenviar email de verificação"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Valida se o email existe e ainda não foi verificado"""
        try:
            user = CustomUser.objects.get(email=value)

            if user.is_active:
                raise serializers.ValidationError(
                    "Este email já foi verificado. Você pode fazer login normalmente."
                )

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "Usuário com este email não encontrado."
            )

        self.user = user  # Armazenar para uso posterior
        return value

    def save(self):
        """Invalidar tokens antigos e criar novo"""
        user = self.user

        # Invalidar tokens de verificação anteriores
        EmailVerificationToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        # Criar novo token
        verification_token = EmailVerificationToken.objects.create(user=user)

        return verification_token


class ClientRegistrationSerializer(UserRegistrationSerializer):
    """Serializer para registro de clientes com campos adicionais"""

    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.filter(is_active=True),
        required=False
    )
    perfil_client = PerfilClientSerializer()

    class Meta(UserRegistrationSerializer.Meta):
        fields = UserRegistrationSerializer.Meta.fields + ['perfil_client']

    def create(self, validated_data):
        """Cria usuário e perfil de cliente"""

        # 1. Definir tipo automaticamente
        tipo_client = TipoUsuario.objects.get(code='CLIENT')
        validated_data['tipo_usuario'] = tipo_client

        # 2. Extrair dados do perfil
        perfil_client_data = validated_data.pop('perfil_client', {})

        # 3. Criar usuário (UMA vez só)
        user = super().create(validated_data)

        # 4. Criar perfil do cliente
        perfil, created = PerfilClient.objects.get_or_create(
            user=user,
            defaults=perfil_client_data
        )
        # Se já existia, atualizar com novos dados
        if not created:
            for key, value in perfil_client_data.items():
                setattr(perfil, key, value)
            perfil.save()

        return user


class InternoRegistrationSerializer(UserRegistrationSerializer):
    """Registro de funcionário interno com nested serializer"""
    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.filter(is_active=True),
        required=False
    )
    perfil_interno = PerfilInternoSerializer()

    class Meta(UserRegistrationSerializer.Meta):
        fields = UserRegistrationSerializer.Meta.fields + ['perfil_interno']

    def create(self, validated_data):
        # Definir tipo automaticamente
        tipo_interno = TipoUsuario.objects.get(code='INTERNO')
        validated_data['tipo_usuario'] = tipo_interno

        perfil_interno_data = validated_data.pop('perfil_interno', {})

       # 3. Criar usuário (UMA vez só)
        user = super().create(validated_data)

        # 4. Criar perfil interno
        perfil, created = PerfilInterno.objects.get_or_create(
            user=user,
            defaults=perfil_interno_data
        )
        # Se já existia, atualizar com novos dados
        if not created:
            for key, value in perfil_interno_data.items():
                setattr(perfil, key, value)
            perfil.save()

        return user


class SubcontratadoRegistrationSerializer(UserRegistrationSerializer):
    """Registro de subcontratado com nested serializer"""
    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.filter(is_active=True),
        required=False
    )
    perfil_subcontratado = PerfilSubcontratadoSerializer()

    class Meta(UserRegistrationSerializer.Meta):
        fields = UserRegistrationSerializer.Meta.fields + \
            ['perfil_subcontratado']

    def create(self, validated_data):
        """Cria usuário e perfil subcontratado"""

        # 1. Definir tipo automaticamente
        tipo_subcontratado = TipoUsuario.objects.get(code='SUBCONTRATADO')
        validated_data['tipo_usuario'] = tipo_subcontratado

        # 2. Extrair dados do perfil
        perfil_subcontratado_data = validated_data.pop(
            'perfil_subcontratado', {})

        # 3. Criar usuário (UMA vez só)
        user = super().create(validated_data)

        # 4. Criar perfil subcontratado
        perfil, created = PerfilSubcontratado.objects.get_or_create(
            user=user,
            defaults=perfil_subcontratado_data
        )
        # Se já existia, atualizar com novos dados
        if not created:
            for key, value in perfil_subcontratado_data.items():
                setattr(perfil, key, value)
            perfil.save()

        return user


class FornecedorRegistrationSerializer(UserRegistrationSerializer):
    """Registro de fornecedor com nested serializer"""
    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.filter(is_active=True),
        required=False
    )
    perfil_fornecedor = PerfilFornecedorSerializer()

    class Meta(UserRegistrationSerializer.Meta):
        fields = UserRegistrationSerializer.Meta.fields + ['perfil_fornecedor']

    def create(self, validated_data):
        """Cria usuário e perfil fornecedor"""

        # 1. Definir tipo automaticamente
        tipo_fornecedor = TipoUsuario.objects.get(code='FORNECEDOR')
        validated_data['tipo_usuario'] = tipo_fornecedor

        # 2. Extrair dados do perfil
        perfil_fornecedor_data = validated_data.pop('perfil_fornecedor', {})

        # 3. Criar usuário (UMA vez só)
        user = super().create(validated_data)

        # 4. Criar perfil fornecedor
        perfil, created = PerfilFornecedor.objects.get_or_create(
            user=user,
            defaults=perfil_fornecedor_data
        )
        # Se já existia, atualizar com novos dados
        if not created:
            for key, value in perfil_fornecedor_data.items():
                setattr(perfil, key, value)
            perfil.save()

        return user
