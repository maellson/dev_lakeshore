from .choice_types import (
    TipoUsuario, Idioma, NivelAcesso, Cargo, Departamento,
    MetodoContato, FrequenciaAtualizacao, FonteClient, CondicaoPagamento
)
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    """Modelo customizado de usuário com tipos específicos"""
    # Campos principais
    email = models.EmailField(unique=True, verbose_name='Email')
    tipo_usuario = models.ForeignKey(
        'account.TipoUsuario',
        on_delete=models.PROTECT,
        verbose_name='Tipo de Usuário',
        help_text='Tipo do usuário no sistema'
    )
    preferencia_idioma = models.ForeignKey(
        'account.Idioma',
        on_delete=models.PROTECT,
        verbose_name='Idioma Preferido',
        help_text='Idioma de preferência do usuário'
    )
    address = models.TextField(
        verbose_name='address',
        help_text='Complete address of the user',
        blank=True
    )

    phone = models.CharField(
        max_length=20, blank=True, verbose_name='Phone')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At")
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    ultimo_login = models.DateTimeField(null=True, blank=True)

    # Campo de login principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'tipo_usuario']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def save(self, *args, **kwargs):
        # Atualizar último login
        if self.pk and self.last_login != self.ultimo_login:
            self.ultimo_login = self.last_login
        super().save(*args, **kwargs)

    def get_tipo_display(self):
        """Template Method: Exibição padronizada do tipo"""
        return self.tipo_usuario.name if self.tipo_usuario else "Não definido"


class PerfilInterno(models.Model):
    """
    Perfil para funcionários internos
    Design Pattern: Composition + Strategy
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_interno'
    )

    # Relacionamentos com tipos externos
    cargo = models.ForeignKey(
        'account.Cargo',
        on_delete=models.PROTECT,
        verbose_name='Cargo'
    )
    departamento = models.ForeignKey(  # diego colocar many-to-many
        'account.Departamento',
        on_delete=models.PROTECT,
        verbose_name='Departamento'
    )
    nivel_acesso = models.ForeignKey(
        'account.NivelAcesso',
        on_delete=models.PROTECT,
        verbose_name='Nível de Acesso'
    )

    responsavel_direto = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Responsável Direto'
    )
    permissoes_especiais = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Permissões Especiais'
    )

    class Meta:
        verbose_name = 'Perfil Interno'
        verbose_name_plural = 'Perfis Internos'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.cargo.name}"

    def get_nivel_numerico(self):
        """Retorna o nível numérico para compatibilidade"""
        return self.nivel_acesso.nivel if self.nivel_acesso else 1


class PerfilSubcontratado(models.Model):
    """
    Perfil para subcontratados
    Design Pattern: Composition
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_subcontratado'
    )
    empresa = models.CharField(max_length=200, verbose_name='Empresa')
    classificacao = models.FloatField(
        default=0.0,
        help_text='Rating de 0 a 5',
        verbose_name='Classificação'
    )
    data_ultimo_servico = models.DateField(null=True, blank=True)
    documentos_verificados = models.BooleanField(
        default=False,
        verbose_name='Documentos Verificados'
    )

    class Meta:
        verbose_name = 'Perfil Subcontratado'
        verbose_name_plural = 'Perfis Subcontratados'

    def __str__(self):
        return f"{self.empresa} - {self.user.get_full_name()}"


class PerfilClient(models.Model):
    """
    Perfil para clientes
    Design Pattern: Strategy (tipos de contato e frequência)
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.RESTRICT,
        related_name='perfil_client'
    )
    main_address = models.TextField(
        verbose_name='Main Address',
        help_text='Main address of the client',)

    # Relacionamentos com tipos externos (Strategy Pattern)
    metodo_contato_preferido = models.ForeignKey(
        'account.MetodoContato',
        on_delete=models.PROTECT,
        verbose_name='Método de Contato Preferido'
    )
    frequencia_atualizacao = models.ForeignKey(
        'account.FrequenciaAtualizacao',
        on_delete=models.PROTECT,
        verbose_name='Frequência de Atualização'
    )
    fonte_client = models.ForeignKey(
        'account.FonteClient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Como nos conheceu'
    )

    notas_importantes = models.TextField(
        blank=True,
        verbose_name='Notas Importantes'
    )

    class Meta:
        verbose_name = 'Perfil Client'
        verbose_name_plural = 'Perfis Clients'

    def __str__(self):
        return f"Client: {self.user.get_full_name()}"


class PerfilFornecedor(models.Model):
    """
    Perfil para fornecedores
    Design Pattern: Strategy (condições de pagamento)
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_fornecedor'
    )
    empresa = models.CharField(max_length=200, verbose_name='Empresa')
    prazo_medio_entrega = models.IntegerField(
        default=7,
        help_text='Dias para entrega',
        verbose_name='Prazo Médio Entrega (dias)'
    )

    # Relacionamento com tipo externo (Strategy Pattern)
    condicoes_pagamento = models.ForeignKey(
        'account.CondicaoPagamento',
        on_delete=models.PROTECT,
        verbose_name='Condições de Pagamento'
    )

    class Meta:
        verbose_name = 'Perfil Fornecedor'
        verbose_name_plural = 'Perfis Fornecedores'

    def __str__(self):
        return f"{self.empresa} - {self.user.get_full_name()}"


class PasswordResetToken(models.Model):
    """Token para recuperação de senha"""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Token Reset Senha'
        verbose_name_plural = 'Tokens Reset Senha'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expira em 1 hora
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Reset token para {self.user.email}"


class EmailVerificationToken(models.Model):
    """Token para verificação de email no registro"""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Token Email Verification'
        verbose_name_plural = 'Tokens Email Verification'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expira em 24 horas (vs 1h do reset)
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Verifica se token ainda é válido"""
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Email verification token para {self.user.email}"



