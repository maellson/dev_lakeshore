"""
Admin refatorado com organização por categorias
Design Pattern: Factory + Template Method
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .admin_permissions import *

from .models import (
    CustomUser, PerfilInterno, PerfilSubcontratado,
    PerfilClient, PerfilFornecedor, PasswordResetToken,
    EmailVerificationToken
)
from .choice_types import (
    TipoUsuario, Idioma, NivelAcesso, Cargo, Departamento,
    MetodoContato, FrequenciaAtualizacao, FonteClient, CondicaoPagamento
)


# =====================================================
# ADMIN BASE PARA TIPOS (Template Method Pattern)
# =====================================================

class ChoiceTypeAdminBase(admin.ModelAdmin):
    """
    Admin base para todos os tipos de escolha
    Template Method Pattern
    """
    list_display = ['name', 'code', 'colored_display', 'order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('code', 'name', 'description')
        }),
        ('Apresentação', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def colored_display(self, obj):
        """Exibe uma amostra da cor"""
        if obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 3px 8px; color: white; border-radius: 3px;">{}</span>',
                obj.color,
                obj.icon or '●'
            )
        return obj.icon or '-'
    colored_display.short_description = 'Visual'

# =============================================

# form customizavel

# ==========================================


class CustomUserCreationForm(UserCreationForm):
    """Form customizado para criação de usuários com opção de email"""

    send_verification_email = forms.BooleanField(
        label='Enviar Email de Verificação',
        help_text=(
            'Se marcado, o usuário será criado como inativo e receberá '
            'um email para verificar e ativar sua conta.'
        ),
        required=False,
        initial=False
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name',
                  'tipo_usuario', 'preferencia_idioma', 'phone')

# =====================================================
# ADMINS DOS TIPOS DE ESCOLHA
# =======================================================


@admin.register(TipoUsuario)
class TipoUsuarioAdmin(ChoiceTypeAdminBase):
    list_display = ['name', 'code', 'colored_display',
                    'users_count', 'order', 'is_active']

    def users_count(self, obj):
        count = obj.customuser_set.count()
        return format_html('<strong>{}</strong> usuários', count)
    users_count.short_description = 'Usuários'


@admin.register(Idioma)
class IdiomaAdmin(ChoiceTypeAdminBase):
    list_display = ['name', 'code', 'locale_code',
                    'colored_display', 'order', 'is_active']

    fieldsets = ChoiceTypeAdminBase.fieldsets + (
        ('Localização', {
            'fields': ('locale_code',)
        }),
    )


@admin.register(NivelAcesso)
class NivelAcessoAdmin(ChoiceTypeAdminBase):
    list_display = ['nivel', 'name', 'code',
                    'cargos_count', 'order', 'is_active']
    ordering = ['nivel']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nivel', 'code', 'name', 'description')
        }),
        ('Apresentação', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def cargos_count(self, obj):
        count = obj.cargo_set.count()
        return format_html('<span class="badge">{}</span> cargos', count)
    cargos_count.short_description = 'Cargos'


@admin.register(Cargo)
class CargoAdmin(ChoiceTypeAdminBase):
    list_display = ['name', 'code', 'nivel_acesso',
                    'users_count', 'order', 'is_active']
    list_filter = ['nivel_acesso', 'is_active']

    fieldsets = ChoiceTypeAdminBase.fieldsets + (
        ('Hierarquia', {
            'fields': ('nivel_acesso',)
        }),
    )

    def users_count(self, obj):
        count = obj.perfilinterno_set.count()
        return format_html('<span class="badge">{}</span>', count)
    users_count.short_description = 'Usuários'


@admin.register(Departamento)
class DepartamentoAdmin(ChoiceTypeAdminBase):
    list_display = ['name', 'code', 'responsavel',
                    'users_count', 'order', 'is_active']
    list_filter = ['is_active']

    fieldsets = ChoiceTypeAdminBase.fieldsets + (
        ('Gestão', {
            'fields': ('responsavel',)
        }),
    )

    def users_count(self, obj):
        count = obj.perfilinterno_set.count()
        return format_html('<span class="badge">{}</span>', count)
    users_count.short_description = 'Usuários'


@admin.register(MetodoContato)
class MetodoContatoAdmin(ChoiceTypeAdminBase):
    pass


@admin.register(FrequenciaAtualizacao)
class FrequenciaAtualizacaoAdmin(ChoiceTypeAdminBase):
    list_display = ['name', 'code', 'dias',
                    'colored_display', 'order', 'is_active']

    fieldsets = ChoiceTypeAdminBase.fieldsets + (
        ('Configuração', {
            'fields': ('dias',)
        }),
    )


@admin.register(FonteClient)
class FonteClientAdmin(ChoiceTypeAdminBase):
    pass


@admin.register(CondicaoPagamento)
class CondicaoPagamentoAdmin(ChoiceTypeAdminBase):
    list_display = ['name', 'code', 'prazo_dias',
                    'desconto_percentual', 'order', 'is_active']

    fieldsets = ChoiceTypeAdminBase.fieldsets + (
        ('Condições Financeiras', {
            'fields': ('prazo_dias', 'desconto_percentual')
        }),
    )


# =====================================================
# INLINES PARA PERFIS
# =====================================================

class PerfilInternoInline(admin.StackedInline):
    model = PerfilInterno
    can_delete = False
    verbose_name_plural = 'Perfil Interno'

    fieldsets = (
        ('Informações Profissionais', {
            'fields': ('cargo', 'departamento', 'nivel_acesso')
        }),
        ('Hierarquia', {
            'fields': ('responsavel_direto',)
        }),
        ('Permissões Especiais', {
            'fields': ('permissoes_especiais',),
            'classes': ('collapse',)
        }),
    )


class PerfilSubcontratadoInline(admin.StackedInline):
    model = PerfilSubcontratado
    can_delete = False
    verbose_name_plural = 'Perfil Subcontratado'


class PerfilClientInline(admin.StackedInline):
    model = PerfilClient
    can_delete = False
    verbose_name_plural = 'Perfil Client'


class PerfilFornecedorInline(admin.StackedInline):
    model = PerfilFornecedor
    can_delete = False
    verbose_name_plural = 'Perfil Fornecedor'


# =====================================================
# ADMIN PRINCIPAL DO USUÁRIO
# =====================================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'email', 'id', 'first_name', 'last_name',
        'tipo_usuario_display', 'status_display', 'date_joined'
    ]
    list_filter = [
        'tipo_usuario', 'is_active', 'is_staff',
        'preferencia_idioma', 'date_joined'
    ]

    # =====================================================
    # FIELDSETS PARA EDIÇÃO DE USUÁRIOS EXISTENTES
    # =====================================================
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        (_('Configurações do Sistema'), {
            'fields': ('tipo_usuario', 'preferencia_idioma')
        }),
        (_('🔐 Status da Conta'), {
            'fields': ('is_active',),
            'description': 'Marque para permitir login do usuário'
        }),
        (_('Permissões'), {
            'fields': (
                'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Datas Importantes'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    # =====================================================
    # FIELDSETS PARA CRIAÇÃO (SEM CAMPO PROBLEMÁTICO)
    # =====================================================
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'first_name', 'last_name', 'tipo_usuario', 'preferencia_idioma',
                'phone'
            ),
        }),
        (_('Configurações de Ativação'), {
            'classes': ('wide',),
            'fields': (
                'is_active',
                'send_verification_email',  # ← Agora funciona porque está no form
            ),
            'description': (
                'Escolha como ativar o usuário:<br>'
                '• <strong>Ativo</strong>: Usuário pode fazer login imediatamente<br>'
                '• <strong>Enviar Email</strong>: Usuário recebe email para ativar conta'
            )
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # =====================================================
    # USAR FORM CUSTOMIZADO PARA CRIAÇÃO
    # =====================================================
    add_form = CustomUserCreationForm

    def get_form(self, request, obj=None, **kwargs):
        """Usa form customizado para criação"""
        if obj is None:  # Criação de novo usuário
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)

    # =====================================================
    # LÓGICA DE SALVAMENTO FLEXÍVEL (mantida)
    # =====================================================
    def save_model(self, request, obj, form, change):
        """Implementa lógica flexível de ativação"""

        # Se é criação de novo usuário (change=False)
        if not change:
            send_email = form.cleaned_data.get(
                'send_verification_email', False)
            is_active = form.cleaned_data.get('is_active', True)

            if send_email:
                #  OPÇÃO 1: Enviar email de verificação
                if not is_active:  # ← RESPEITAR escolha do admin
                    obj.is_active = False
                # Se admin marcou is_active=True, usuário fica ativo mesmo com email

                super().save_model(request, obj, form, change)

                # Criar token e enviar email
                self._create_and_send_verification_email(obj, request)

                # Mensagem de sucesso
                from django.contrib import messages
                messages.success(
                    request,
                    f'Usuário {obj.email} criado! Email de verificação enviado.'
                )
            else:
                # OPÇÃO 2: Ativar diretamente (comportamento padrão)
                super().save_model(request, obj, form, change)

                if obj.is_active:
                    from django.contrib import messages
                    messages.success(
                        request,
                        f'Usuário {obj.email} criado e ativado diretamente.'
                    )
        else:
            # Para usuários existentes, comportamento normal
            super().save_model(request, obj, form, change)

    def _create_and_send_verification_email(self, user, request):
        """Cria token e envia email de verificação"""
        try:
            # Invalidar tokens anteriores (se houver)
            EmailVerificationToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)

            # Criar novo token
            verification_token = EmailVerificationToken.objects.create(
                user=user)

            # Enviar email
            self._send_verification_email(user, verification_token)

        except Exception as e:
            from django.contrib import messages
            messages.error(
                request,
                f'Erro ao enviar email de verificação: {str(e)}'
            )

    def _send_verification_email(self, user, verification_token):
        """Envia email de verificação (método reutilizável)"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"

        context = {
            'user': user,
            'verification_url': verification_url,
            'token_expires': verification_token.expires_at,
        }

        # Render do template HTML
        html_message = render_to_string(
            'emails/email_verification.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject='Verificação de Email - ERP Lakeshore',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

    # =====================================================
    # MÉTODOS DE DISPLAY (mantidos)
    # =====================================================
    def tipo_usuario_display(self, obj):
        """Exibe tipo com cor"""
        if obj.tipo_usuario and obj.tipo_usuario.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.tipo_usuario.color,
                obj.tipo_usuario.name
            )
        return obj.tipo_usuario.name if obj.tipo_usuario else '-'
    tipo_usuario_display.short_description = 'Tipo'

    def status_display(self, obj):
        """Exibe status com ícone"""
        if obj.is_active:
            return format_html('<span style="color: green;">● Ativo</span>')
        return format_html('<span style="color: red;">● Inativo</span>')
    status_display.short_description = 'Status'

    def get_inline_instances(self, request, obj=None):
        """Factory Pattern: Retorna inline apropriado baseado no tipo"""
        if not obj or not obj.tipo_usuario:
            return []

        tipo_code = obj.tipo_usuario.code
        inline_map = {
            'INTERNO': PerfilInternoInline,
            'SUBCONTRATADO': PerfilSubcontratadoInline,
            'CLIENT': PerfilClientInline,
            'FORNECEDOR': PerfilFornecedorInline,
        }

        inline_class = inline_map.get(tipo_code)
        if inline_class:
            return [inline_class(self.model, self.admin_site)]
        return []
# =====================================================
# ADMINS DOS PERFIS SEPARADOS
# =====================================================

class PerfilAdminBase(admin.ModelAdmin):
    """Classe base para admins de perfis"""
    
    def get_user_id(self, obj):
        """Exibe o ID do usuário relacionado"""
        return obj.user.id if obj.user else None
    get_user_id.short_description = 'User ID'
    get_user_id.admin_order_field = 'user__id'
    
    def get_queryset(self, request):
        """Otimiza queries com select_related para evitar N+1"""
        return super().get_queryset(request).select_related('user')


@admin.register(PerfilInterno)
class PerfilInternoAdmin(PerfilAdminBase):
    list_display = [
        'user', 'get_user_id', 'cargo', 'departamento',
        'nivel_acesso', 'responsavel_direto'
    ]
    list_filter = ['cargo', 'departamento', 'nivel_acesso']
    search_fields = ['user__email',
                     'user__first_name', 'user__last_name']
    raw_id_fields = ['user', 'responsavel_direto']

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações Profissionais', {
            'fields': ('cargo', 'departamento', 'nivel_acesso')
        }),
        ('Hierarquia', {
            'fields': ('responsavel_direto',)
        }),
        ('Permissões Especiais', {
            'fields': ('permissoes_especiais',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Otimiza queries específicas do PerfilInterno"""
        return super().get_queryset(request).select_related(
            'user', 'cargo', 'departamento', 'nivel_acesso', 'responsavel_direto__user'
        )


@admin.register(PerfilSubcontratado)
class PerfilSubcontratadoAdmin(PerfilAdminBase):
    list_display = [
        'user', 'get_user_id', 'empresa', 'classificacao',
        'documentos_verificados', 'data_ultimo_servico'
    ]
    list_filter = ['documentos_verificados', 'classificacao']
    search_fields = ['user__email', 'empresa']


@admin.register(PerfilClient)
class PerfilClientAdmin(PerfilAdminBase):
    list_display = [
        'user', 'get_user_id', 'metodo_contato_preferido',
        'frequencia_atualizacao', 'fonte_client'
    ]
    list_filter = ['metodo_contato_preferido', 'frequencia_atualizacao']
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'main_address'
    ]
    
    def get_queryset(self, request):
        """Otimiza queries específicas do PerfilClient"""
        return super().get_queryset(request).select_related(
            'user', 'metodo_contato_preferido', 'frequencia_atualizacao', 'fonte_client'
        )


@admin.register(PerfilFornecedor)
class PerfilFornecedorAdmin(PerfilAdminBase):
    list_display = [
        'user', 'get_user_id', 'empresa', 'prazo_medio_entrega', 'condicoes_pagamento'
    ]
    list_filter = ['condicoes_pagamento']
    search_fields = ['user__email', 'empresa']
    
    def get_queryset(self, request):
        """Otimiza queries específicas do PerfilFornecedor"""
        return super().get_queryset(request).select_related(
            'user', 'condicoes_pagamento'
        )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['token', 'created_at']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin para tokens de verificação de email"""

    list_display = [
        'user', 'created_at', 'expires_at',
        'is_used', 'status_display', 'time_remaining'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['token', 'created_at', 'expires_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Informações do Token', {
            'fields': ('token', 'user')
        }),
        ('Status', {
            'fields': ('is_used', 'created_at', 'expires_at')
        }),
    )

    def status_display(self, obj):
        """Exibe status visual do token"""
        if obj.is_used:
            return format_html('<span style="color: gray;">✓ Usado</span>')
        elif obj.is_valid():
            return format_html('<span style="color: green;">● Válido</span>')
        else:
            return format_html('<span style="color: red;">⚠ Expirado</span>')
    status_display.short_description = 'Status'

    def time_remaining(self, obj):
        """Mostra tempo restante para expiração"""
        if obj.is_used:
            return "Token usado"

        from django.utils import timezone
        now = timezone.now()

        if now > obj.expires_at:
            return "Expirado"

        delta = obj.expires_at - now
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)

        return f"{hours}h {minutes}m restantes"
    time_remaining.short_description = 'Tempo Restante'

    def get_queryset(self, request):
        """Otimiza queries com select_related"""
        return super().get_queryset(request).select_related('user')

    # TODO: ADICIONAR FUNCIONALIDADE PARA ENVIO DE EMAIL DE VERIFICAÇÃO NO ADMIN
