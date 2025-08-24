from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import CustomUser, PasswordResetToken, PerfilInterno, PerfilClient, PerfilFornecedor, EmailVerificationToken, TipoUsuario
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    ResendEmailVerificationSerializer,
    ClientRegistrationSerializer,
    InternoRegistrationSerializer,
    SubcontratadoRegistrationSerializer,
    FornecedorRegistrationSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.swagger_tags import API_TAGS


class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para obter token JWT"""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Login de usuário",
        operation_description="Endpoint para autenticação de usuários e obtenção de tokens JWT",
        responses={
            200: openapi.Response('Login bem-sucedido', CustomTokenObtainPairSerializer),
            401: 'Credenciais inválidas'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """View customizada para atualizar token JWT"""

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Atualizar token JWT",
        operation_description="Endpoint para atualizar o token JWT usando o refresh token",
        responses={
            200: openapi.Response('Token atualizado com sucesso'),
            401: 'Token inválido ou expirado'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DynamicRegisterView(APIView):
    """View para registro de novos usuários com verificação de email"""
    permission_classes = [permissions.AllowAny]
    # Mapear tipos para serializers
    SERIALIZER_MAP = {
        'client': ClientRegistrationSerializer,
        'interno': InternoRegistrationSerializer,
        'subcontratado': SubcontratadoRegistrationSerializer,
        'fornecedor': FornecedorRegistrationSerializer,
    }

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Registro dinâmico de usuário",
        operation_description="""
        ## Registro de Usuários por Tipo
        
        Este endpoint permite registrar usuários de diferentes tipos com seus perfis específicos.
        
        ### Tipos Disponíveis:
        - **client** - Clientes da empresa
        - **interno** - Funcionários internos  
        - **subcontratado** - Prestadores de serviços
        - **fornecedor** - Fornecedores de materiais
        
        ### Estrutura Obrigatória:
        Todos os tipos requerem:
        - Dados básicos do usuário (email, nome, senha, etc.)
        - Objeto `perfil_{tipo}` com campos específicos do tipo
        
        ### Exemplos por Tipo:
        
        #### Cliente:
        ```json
        {
          "email": "cliente@exemplo.com",
          "username": "cliente123",
          "first_name": "João",
          "last_name": "Silva", 
          "phone": "11999999999",
          "preferencia_idioma": 1,
          "password": "MinhaSenh@123",
          "password_confirm": "MinhaSenh@123",
          "perfil_client": {
            "main_address": "Rua das Flores, 123",
            "metodo_contato_preferido": 1,
            "frequencia_atualizacao": 2,
            "fonte_client": 1,
            "notas_importantes": "Cliente VIP"
          }
        }
        ```
        
        #### Funcionário Interno:
        ```json
        {
          "email": "funcionario@empresa.com",
          "username": "funcionario123",
          "first_name": "Maria",
          "last_name": "Santos",
          "preferencia_idioma": 1, 
          "password": "MinhaSenh@123",
          "password_confirm": "MinhaSenh@123",
          "perfil_interno": {
            "cargo": 1,
            "departamento": 2,
            "nivel_acesso": 3,
            "responsavel_direto": null
          }
        }
        ```
        
        #### Subcontratado:
        ```json
        {
          "email": "contato@empresa.com",
          "username": "empresa123",
          "first_name": "Pedro",
          "last_name": "Silva",
          "preferencia_idioma": 1,
          "password": "MinhaSenh@123", 
          "password_confirm": "MinhaSenh@123",
          "perfil_subcontratado": {
            "empresa": "Empresa XYZ Ltda",
            "classificacao": 4.5,
            "documentos_verificados": true
          }
        }
        ```
        
        #### Fornecedor:
        ```json
        {
          "email": "vendas@fornecedor.com",
          "username": "fornecedor123",
          "first_name": "Ana",
          "last_name": "Costa",
          "preferencia_idioma": 1,
          "password": "MinhaSenh@123",
          "password_confirm": "MinhaSenh@123", 
          "perfil_fornecedor": {
            "empresa": "Fornecedor ABC",
            "prazo_medio_entrega": 5,
            "condicoes_pagamento": 1
          }
        }
        ```
        
        ### 💡 Dica:
        Use GET `/api/auth/user-types/` para obter todos os IDs e opções disponíveis.
        """,
        request_body=UserRegistrationSerializer,
        manual_parameters=[
            openapi.Parameter(
                'tipo_usuario',
                openapi.IN_PATH,
                description="Tipo de usuário: client, interno, subcontratado, fornecedor",
                type=openapi.TYPE_STRING,
                enum=['client', 'interno', 'subcontratado', 'fornecedor'],
                required=True
            )
        ],
        responses={
            201: openapi.Response(
                'Usuário criado com sucesso'
            ),
            400: openapi.Response(
                'Dados inválidos ou tipo não suportado'
            )
        }
    )
    def post(self, request, tipo_usuario):
        """Registra um novo usuário com perfil específico"""

        # Validar tipo de usuário
        tipo_lower = tipo_usuario.lower()
        if tipo_lower not in self.SERIALIZER_MAP:
            return Response({
                'error': f'Tipo de usuário "{tipo_usuario}" não suportado',
                'tipos_disponiveis': list(self.SERIALIZER_MAP.keys())
            }, status=status.HTTP_400_BAD_REQUEST)

        # Obter serializer apropriado
        serializer_class = self.SERIALIZER_MAP[tipo_lower]
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            with transaction.atomic():  # Garantir que tudo seja criado junto
                user = serializer.save()  # ← Variável definida aqui

            # Criar usuário INATIVO (aguardando verificação)
            user.is_active = False  # ← Agora pode acessar user
            user.save()

            # Criar token de verificação
            verification_token = EmailVerificationToken.objects.create(
                user=user)

            # Enviar email de verificação
            self.send_verification_email(user, verification_token)

            return Response({
                'message': 'Usuário criado com sucesso! Verifique seu email para ativar a conta.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nome_completo': user.get_full_name(),
                    'tipo_usuario': {
                        'id': user.tipo_usuario.id,
                        'code': user.tipo_usuario.code,
                        'name': user.tipo_usuario.name
                    },
                    'perfil_criado': True,
                    'is_active': user.is_active  # ← False
                },
                'verification_required': True
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, verification_token):
        """Enviar email de verificação (método reutilizável)"""
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


class LogoutView(APIView):
    """View para logout do usuário"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Logout de usuário",
        operation_description="Endpoint para logout e invalidação do token JWT",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de refresh')
            },
            required=['refresh_token']
        ),
        responses={
            200: 'Logout realizado com sucesso',
            400: 'Token inválido'
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'message': 'Logout realizado com sucesso'
            }, status=status.HTTP_200_OK)

        except TokenError:
            return Response({
                'error': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):

    """View para visualizar e atualizar perfil do usuário"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Obter perfil do usuário",
        operation_description="Obter perfil do usuário logado",
        responses={200: UserProfileSerializer})
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Atualizar perfil do usuário",
        operation_description="Atualizar perfil do usuário"
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()

            # Retornar perfil atualizado
            profile_serializer = UserProfileSerializer(request.user)
            return Response({
                'message': 'Perfil atualizado com sucesso',
                'user': profile_serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# verificar erro se smtp ou porta minha fechada ta osso
class PasswordResetRequestView(APIView):
    """View para solicitar reset de senha"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Solicitar reset de senha",
        operation_description="Endpoint para solicitar reset de senha via email",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: 'Email de recuperação enviado com sucesso',
            400: 'Dados inválidos'
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)

            # Invalidar tokens anteriores
            PasswordResetToken.objects.filter(
                user=user, is_used=False).update(is_used=True)

            # Criar novo token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Enviar email
            self.send_reset_email(user, reset_token)

            return Response({
                'message': 'Email de recuperação enviado com sucesso'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # verificar erro se smtp ou porta minha fechada ta osso
    def send_reset_email(self, user, reset_token):
        """ View para Enviar email de recuperação de senha"""
        reset_url = f"{settings.FRONTEND_URL}/{reset_token.token}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'token_expires': reset_token.expires_at,
        }

        # Render do template HTML
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject='Recuperação de Senha - ERP Lakeshore',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class PasswordResetConfirmView(APIView):
    """View para confirmar reset de senha"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Confirmar reset de senha",
        operation_description="Endpoint para confirmar reset de senha com token",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: 'Senha alterada com sucesso',
            400: 'Token inválido ou expirado'
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            reset_token = serializer.validated_data['reset_token']
            new_password = serializer.validated_data['password']

            # Alterar senha
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Marcar token como usado
            reset_token.is_used = True
            reset_token.save()

            return Response({
                'message': 'Senha alterada com sucesso'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Permissões do usuário",
    operation_description="Endpoint para obter permissões do usuário atual",
    responses={
        200: openapi.Response('Permissões do usuário')
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_view(request):
    """Endpoint para obter permissões do usuário atual"""
    user = request.user

    # Obter todas as permissões
    all_permissions = user.get_all_permissions()

    # Obter grupos
    groups = [group.name for group in user.groups.all()]

    # Permissões específicas do usuário
    user_permissions = [perm.codename for perm in user.user_permissions.all()]

    return Response({
        'user_id': user.id,
        'email': user.email,
        'tipo_usuario': {
                'id': user.tipo_usuario.id,
                'code': user.tipo_usuario.code,
                'name': user.tipo_usuario.name
            } if user.tipo_usuario else None,
        'groups': groups,
        'user_permissions': user_permissions,
        'all_permissions': list(all_permissions),
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    })


@swagger_auto_schema(
    method='post',
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Verificar token",
    operation_description="Endpoint para verificar se um token JWT é válido",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token JWT')
        },
        required=['token']
    ),
    responses={
        200: openapi.Response('Token válido'),
        401: 'Token inválido'
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_token_view(request):
    """Endpoint para verificar se um token JWT é válido"""
    token = request.data.get('token')

    if not token:
        return Response(
            {'error': 'Token é obrigatório'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)

        return Response({
            'valid': True,
            'user_id': access_token['user_id'],
            'expires_at': access_token['exp']
        })

    except TokenError as e:
        return Response({
            'valid': False,
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


# apps/account/views.py - ADICIONAR
@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Opções para formulários",
    operation_description="Retorna todas as opções disponíveis para formulários",
    responses={
        200: openapi.Response('Lista de opções para formulários')
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def choices_view(request):
    """Retorna todas as opções disponíveis para formulários"""
    from .choice_types import TipoUsuario, Idioma, NivelAcesso, MetodoContato, FrequenciaAtualizacao

    return Response({
        'tipos_usuario': list(TipoUsuario.objects.filter(is_active=True).values('id', 'code', 'name')),
        'idiomas': list(Idioma.objects.filter(is_active=True).values('id', 'code', 'name')),
        'niveis_acesso': list(NivelAcesso.objects.filter(is_active=True).values('id', 'code', 'name', 'nivel')),
        'metodos_contato': list(MetodoContato.objects.filter(is_active=True).values('id', 'code', 'name')),
        'frequencias_atualizacao': list(FrequenciaAtualizacao.objects.filter(is_active=True).values('id', 'code', 'name', 'dias'))
    })


class VerifyEmailView(APIView):
    """View para verificar email através do token"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Verificar email",
        operation_description="Endpoint para verificar email através do token",
        responses={
            200: 'Email verificado com sucesso',
            400: 'Token inválido ou expirado'
        }
    )
    def get(self, request, token):
        """Verifica email quando usuário clica no link"""
        serializer = EmailVerificationSerializer(data={'token': token})

        if serializer.is_valid():
            user = serializer.save()  # Ativa usuário + marca token como usado

            return Response({
                'message': 'Email verificado com sucesso! Você já pode fazer login.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nome_completo': user.get_full_name(),
                    'is_active': user.is_active
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Token inválido ou expirado',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ResendEmailVerificationView(APIView):
    """View para reenviar email de verificação"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Reenviar email de verificação",
        operation_description="Endpoint para reenviar email de verificação",
        request_body=ResendEmailVerificationSerializer,
        responses={
            200: 'Email de verificação reenviado com sucesso',
            400: 'Dados inválidos'
        }
    )
    def post(self, request):
        """Reenvia email de verificação"""
        serializer = ResendEmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            verification_token = serializer.save()  # Cria novo token

            # Enviar email
            self.send_verification_email(
                verification_token.user, verification_token)

            return Response({
                'message': 'Email de verificação reenviado com sucesso'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, verification_token):
        """Enviar email de verificação"""
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


@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Guia completo para registro",
    operation_description="Endpoint helper com exemplos completos e IDs disponíveis para cada tipo de usuário",
    responses={
        200: openapi.Response('Guia completo de registro com exemplos')
    }
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def registration_choices_view(request):
    """Endpoint helper para obter guia completo de registro"""
    from .choice_types import (
        TipoUsuario, Idioma, MetodoContato, FrequenciaAtualizacao,
        FonteClient, NivelAcesso, Cargo, Departamento, CondicaoPagamento
    )

    # Dados de apoio
    tipos_usuario = list(TipoUsuario.objects.filter(
        is_active=True).values('id', 'code', 'name', 'icon', 'color'))
    idiomas = list(Idioma.objects.filter(is_active=True).values(
        'id', 'code', 'name', 'locale_code'))

    response_data = {
        'message': '🚀 Guia Completo para Registro de Usuários',
        'base_url': request.build_absolute_uri('/')[:-1],

        'dados_de_apoio': {
            'tipos_usuario': tipos_usuario,
            'idiomas': idiomas,
            'metodos_contato': list(MetodoContato.objects.filter(is_active=True).values('id', 'code', 'name')),
            'frequencias_atualizacao': list(FrequenciaAtualizacao.objects.filter(is_active=True).values('id', 'code', 'name', 'dias')),
            'fontes_client': list(FonteClient.objects.filter(is_active=True).values('id', 'code', 'name')),
            'cargos': list(Cargo.objects.filter(is_active=True).values('id', 'code', 'name')),
            'departamentos': list(Departamento.objects.filter(is_active=True).values('id', 'code', 'name')),
            'niveis_acesso': list(NivelAcesso.objects.filter(is_active=True).values('id', 'code', 'name', 'nivel')),
            'condicoes_pagamento': list(CondicaoPagamento.objects.filter(is_active=True).values('id', 'code', 'name'))
        },

        'tipos_de_registro': [
            {
                'tipo': 'client',
                'nome': 'Cliente',
                'endpoint': f"{request.build_absolute_uri('/')[:-1]}/api/auth/register/client/",
                'descrição': 'Para cadastrar clientes da empresa',
                'estrutura_obrigatoria': {
                    'usuario_base': {
                        'email': 'string (obrigatório)',
                        'username': 'string (obrigatório)',
                        'first_name': 'string (obrigatório)',
                        'last_name': 'string (obrigatório)',
                        'phone': 'string (opcional)',
                        'preferencia_idioma': 'integer - ID do idioma (obrigatório)',
                        'password': 'string (obrigatório)',
                        'password_confirm': 'string (obrigatório)'
                    },
                    'perfil_client': {
                        'main_address': 'string (obrigatório)',
                        'metodo_contato_preferido': 'integer - ID do método (obrigatório)',
                        'frequencia_atualizacao': 'integer - ID da frequência (obrigatório)',
                        'fonte_client': 'integer - ID da fonte (opcional)',
                        'notas_importantes': 'string (opcional)'
                    }
                },
                'exemplo_completo': {
                    'email': 'cliente@exemplo.com',
                    'username': 'cliente123',
                    'first_name': 'João',
                    'last_name': 'Silva',
                    'phone': '11999999999',
                    'preferencia_idioma': 1,
                    'password': 'MinhaSenh@123',
                    'password_confirm': 'MinhaSenh@123',
                    'perfil_client': {
                        'main_address': 'Rua das Flores, 123, São Paulo, SP',
                        'metodo_contato_preferido': 1,
                        'frequencia_atualizacao': 2,
                        'fonte_client': 1,
                        'notas_importantes': 'Cliente VIP - atendimento prioritário'
                    }
                }
            },

            {
                'tipo': 'interno',
                'nome': 'Funcionário Interno',
                'endpoint': f"{request.build_absolute_uri('/')[:-1]}/api/auth/register/interno/",
                'descrição': 'Para cadastrar funcionários da empresa',
                'estrutura_obrigatoria': {
                    'usuario_base': {
                        'email': 'string (obrigatório)',
                        'username': 'string (obrigatório)',
                        'first_name': 'string (obrigatório)',
                        'last_name': 'string (obrigatório)',
                        'phone': 'string (opcional)',
                        'preferencia_idioma': 'integer - ID do idioma (obrigatório)',
                        'password': 'string (obrigatório)',
                        'password_confirm': 'string (obrigatório)'
                    },
                    'perfil_interno': {
                        'cargo': 'integer - ID do cargo (obrigatório)',
                        'departamento': 'integer - ID do departamento (obrigatório)',
                        'nivel_acesso': 'integer - ID do nível (obrigatório)',
                        'responsavel_direto': 'integer - ID do responsável (opcional)'
                    }
                },
                'exemplo_completo': {
                    'email': 'funcionario@empresa.com',
                    'username': 'funcionario123',
                    'first_name': 'Maria',
                    'last_name': 'Santos',
                    'phone': '11888888888',
                    'preferencia_idioma': 1,
                    'password': 'MinhaSenh@123',
                    'password_confirm': 'MinhaSenh@123',
                    'perfil_interno': {
                        'cargo': 1,
                        'departamento': 2,
                        'nivel_acesso': 3,
                        'responsavel_direto': None
                    }
                }
            },

            {
                'tipo': 'subcontratado',
                'nome': 'Subcontratado',
                'endpoint': f"{request.build_absolute_uri('/')[:-1]}/api/auth/register/subcontratado/",
                'descrição': 'Para cadastrar prestadores de serviços terceirizados',
                'estrutura_obrigatoria': {
                    'usuario_base': {
                        'email': 'string (obrigatório)',
                        'username': 'string (obrigatório)',
                        'first_name': 'string (obrigatório)',
                        'last_name': 'string (obrigatório)',
                        'phone': 'string (opcional)',
                        'preferencia_idioma': 'integer - ID do idioma (obrigatório)',
                        'password': 'string (obrigatório)',
                        'password_confirm': 'string (obrigatório)'
                    },
                    'perfil_subcontratado': {
                        'empresa': 'string (obrigatório)',
                        'classificacao': 'float 0-5 (opcional, padrão: 0.0)',
                        'documentos_verificados': 'boolean (opcional, padrão: false)'
                    }
                },
                'exemplo_completo': {
                    'email': 'contato@empresa.com',
                    'username': 'empresa123',
                    'first_name': 'Pedro',
                    'last_name': 'Silva',
                    'phone': '11777777777',
                    'preferencia_idioma': 1,
                    'password': 'MinhaSenh@123',
                    'password_confirm': 'MinhaSenh@123',
                    'perfil_subcontratado': {
                        'empresa': 'Empresa XYZ Ltda',
                        'classificacao': 4.5,
                        'documentos_verificados': True
                    }
                }
            },

            {
                'tipo': 'fornecedor',
                'nome': 'Fornecedor',
                'endpoint': f"{request.build_absolute_uri('/')[:-1]}/api/auth/register/fornecedor/",
                'descrição': 'Para cadastrar fornecedores de materiais',
                'estrutura_obrigatoria': {
                    'usuario_base': {
                        'email': 'string (obrigatório)',
                        'username': 'string (obrigatório)',
                        'first_name': 'string (obrigatório)',
                        'last_name': 'string (obrigatório)',
                        'phone': 'string (opcional)',
                        'preferencia_idioma': 'integer - ID do idioma (obrigatório)',
                        'password': 'string (obrigatório)',
                        'password_confirm': 'string (obrigatório)'
                    },
                    'perfil_fornecedor': {
                        'empresa': 'string (obrigatório)',
                        'prazo_medio_entrega': 'integer dias (opcional, padrão: 7)',
                        'condicoes_pagamento': 'integer - ID das condições (obrigatório)'
                    }
                },
                'exemplo_completo': {
                    'email': 'vendas@fornecedor.com',
                    'username': 'fornecedor123',
                    'first_name': 'Ana',
                    'last_name': 'Costa',
                    'phone': '11666666666',
                    'preferencia_idioma': 1,
                    'password': 'MinhaSenh@123',
                    'password_confirm': 'MinhaSenh@123',
                    'perfil_fornecedor': {
                        'empresa': 'Fornecedor ABC',
                        'prazo_medio_entrega': 5,
                        'condicoes_pagamento': 1
                    }
                }
            }
        ],

        'dicas_importantes': [
            '🔑 O campo perfil_{tipo} é OBRIGATÓRIO e deve conter um objeto',
            '📧 Usuários são criados como INATIVOS e recebem email de verificação',
            '🔍 Use os IDs dos dados_de_apoio nos campos de relacionamento',
            '🌐 preferencia_idioma: 1=Português, 2=English, 3=Español',
            '⚠️ password e password_confirm devem ser idênticos',
            '📱 phone é opcional mas recomendado para contato'
        ],

        'endpoints_relacionados': {
            'listar_tipos': f"{request.build_absolute_uri('/')[:-1]}/api/auth/user-types/",
            'verificar_email': f"{request.build_absolute_uri('/')[:-1]}/api/auth/verify-email/{{token}}/",
            'reenviar_verificacao': f"{request.build_absolute_uri('/')[:-1]}/api/auth/resend-verification/",
            'fazer_login': f"{request.build_absolute_uri('/')[:-1]}/api/auth/login/"
        }
    }

    return Response(response_data)

# apps/account/views.py - ADICIONAR


class AllUsersListView(APIView):
    """View para listar todos os usuários do sistema"""
    permission_classes = [
        permissions.IsAuthenticated]  # Qualquer usuário logado pode ver

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Listar todos os usuários",
        operation_description="Lista todos os usuários do sistema com filtros opcionais",
        manual_parameters=[
            openapi.Parameter('tipo_usuario', openapi.IN_QUERY,
                              description="Filtrar por tipo de usuário",
                              type=openapi.TYPE_STRING,
                              enum=['INTERNO', 'CLIENT', 'SUBCONTRATADO', 'FORNECEDOR']),
            openapi.Parameter('is_active', openapi.IN_QUERY,
                              description="Filtrar por status ativo",
                              type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY,
                              description="Buscar por nome ou email",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY,
                              description="Número da página",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY,
                              description="Itens por página",
                              type=openapi.TYPE_INTEGER)
        ],
        responses={200: 'Lista de usuários com paginação'}
    )
    def get(self, request):
        """Listar todos os usuários com filtros e paginação"""

        # Base queryset
        users = CustomUser.objects.select_related(
            'tipo_usuario', 'preferencia_idioma'
        ).prefetch_related(
            'groups',
            'perfil_interno__cargo',
            'perfil_interno__departamento',
            'perfil_interno__nivel_acesso'
        )

        # Aplicar filtros
        tipo_usuario = request.query_params.get('tipo_usuario')
        if tipo_usuario:
            users = users.filter(tipo_usuario__code=tipo_usuario)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            users = users.filter(is_active=is_active_bool)

        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            users = users.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        # Ordenação
        users = users.order_by('-date_joined')

        # Paginação
        from django.core.paginator import Paginator
        page_size = int(request.query_params.get('page_size', 20))  # Removido limite máximo
        page_number = int(request.query_params.get('page', 1))

        paginator = Paginator(users, page_size)
        page_obj = paginator.get_page(page_number)

        # Serializar dados
        users_data = []
        for user in page_obj:
            user_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'phone': user.phone,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'tipo_usuario': {
                    'code': user.tipo_usuario.code,
                    'name': user.tipo_usuario.name,
                    'icon': user.tipo_usuario.icon,
                    'color': user.tipo_usuario.color
                } if user.tipo_usuario else None,
                'preferencia_idioma': {
                    'code': user.preferencia_idioma.code,
                    'name': user.preferencia_idioma.name
                } if user.preferencia_idioma else None,
                'groups': [group.name for group in user.groups.all()],
            }

            # Adicionar dados específicos do perfil
            if hasattr(user, 'perfil_interno') and user.perfil_interno:
                perfil = user.perfil_interno
                user_data['perfil_interno'] = {
                    'cargo': {
                        'code': perfil.cargo.code,
                        'name': perfil.cargo.name
                    } if perfil.cargo else None,
                    'departamento': {
                        'code': perfil.departamento.code,
                        'name': perfil.departamento.name
                    } if perfil.departamento else None,
                    'nivel_acesso': {
                        'nivel': perfil.nivel_acesso.nivel,
                        'code': perfil.nivel_acesso.code,
                        'name': perfil.nivel_acesso.name
                    } if perfil.nivel_acesso else None
                }

            elif hasattr(user, 'perfil_client') and user.perfil_client:
                perfil = user.perfil_client
                user_data['perfil_client'] = {
                    'main_address': perfil.main_address,
                    'metodo_contato_preferido': perfil.metodo_contato_preferido.name if perfil.metodo_contato_preferido else None,
                    'frequencia_atualizacao': perfil.frequencia_atualizacao.name if perfil.frequencia_atualizacao else None
                }

            elif hasattr(user, 'perfil_subcontratado') and user.perfil_subcontratado:
                perfil = user.perfil_subcontratado
                user_data['perfil_subcontratado'] = {
                    'empresa': perfil.empresa,
                    'classificacao': perfil.classificacao,
                    'documentos_verificados': perfil.documentos_verificados
                }

            elif hasattr(user, 'perfil_fornecedor') and user.perfil_fornecedor:
                perfil = user.perfil_fornecedor
                user_data['perfil_fornecedor'] = {
                    'empresa': perfil.empresa,
                    'prazo_medio_entrega': perfil.prazo_medio_entrega,
                    'condicoes_pagamento': perfil.condicoes_pagamento.name if perfil.condicoes_pagamento else None
                }

            users_data.append(user_data)

        # Resposta com metadados de paginação
        return Response({
            'users': users_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None
            },
            'filters_applied': {
                'tipo_usuario': tipo_usuario,
                'is_active': is_active,
                'search': search
            },
            'summary': {
                'total_users': paginator.count,
                'active_users': CustomUser.objects.filter(is_active=True).count(),
                'inactive_users': CustomUser.objects.filter(is_active=False).count(),
                'by_type': {
                    tipo.code: CustomUser.objects.filter(
                        tipo_usuario=tipo).count()
                    for tipo in TipoUsuario.objects.filter(is_active=True)
                }
            }
        })


# TODO: ADICIONAR LÓGICA NA VIEW DE PRIMEIRO ACESSO

@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Tipos de usuário disponíveis",
    operation_description="Lista todos os tipos de usuário e seus campos específicos para registro",
    responses={200: 'Lista de tipos com campos'}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_types_and_fields_view(request):
    """Retorna tipos de usuário disponíveis e seus campos específicos"""

    from .choice_types import (
        TipoUsuario, Idioma, MetodoContato, FrequenciaAtualizacao,
        FonteClient, NivelAcesso, Cargo, Departamento, CondicaoPagamento
    )

    # Campos base (comuns a todos)
    base_fields = {
        'email': {'type': 'email', 'required': True},
        'username': {'type': 'string', 'required': True},
        'first_name': {'type': 'string', 'required': True},
        'last_name': {'type': 'string', 'required': True},
        'phone': {'type': 'string', 'required': False},
        'preferencia_idioma': {
            'type': 'choice',
            'required': True,
            'choices': list(Idioma.objects.filter(is_active=True).values('id', 'code', 'name'))
        },
        'password': {'type': 'password', 'required': True},
        'password_confirm': {'type': 'password', 'required': True}
    }

    response_data = {
        'tipos_disponiveis': [
            {
                'code': 'client',
                'name': 'Cliente',
                'endpoint': '/api/auth/register/client/',
                'structure': 'nested',
                'base_fields': base_fields,
                'perfil_fields': {
                    'main_address': {'type': 'text', 'required': True},
                    'metodo_contato_preferido': {
                        'type': 'choice', 'required': True,
                        'choices': list(MetodoContato.objects.filter(is_active=True).values('id', 'code', 'name'))
                    },
                    'frequencia_atualizacao': {
                        'type': 'choice', 'required': True,
                        'choices': list(FrequenciaAtualizacao.objects.filter(is_active=True).values('id', 'code', 'name'))
                    },
                    'fonte_client': {
                        'type': 'choice', 'required': False,
                        'choices': list(FonteClient.objects.filter(is_active=True).values('id', 'code', 'name'))
                    },
                    'notas_importantes': {'type': 'text', 'required': False}
                },
                'example_request': {
                    'email': 'cliente@exemplo.com',
                    'username': 'cliente123',
                    'first_name': 'João',
                    'last_name': 'Silva',
                    'phone': '11999999999',
                    'preferencia_idioma': 1,
                    'password': 'senha123',
                    'password_confirm': 'senha123',
                    'perfil_client': {
                        'main_address': 'Rua das Flores, 123',
                        'metodo_contato_preferido': 1,
                        'frequencia_atualizacao': 2,
                        'fonte_client': 1,
                        'notas_importantes': 'Cliente VIP'
                    }
                }
            },
            {
                'code': 'interno',
                'name': 'Funcionário Interno',
                'endpoint': '/api/auth/register/interno/',
                'structure': 'nested',
                'base_fields': base_fields,
                'perfil_fields': {
                    'cargo': {
                        'type': 'choice', 'required': True,
                        'choices': list(Cargo.objects.filter(is_active=True).values('id', 'code', 'name'))
                    },
                    'departamento': {
                        'type': 'choice', 'required': True,
                        'choices': list(Departamento.objects.filter(is_active=True).values('id', 'code', 'name'))
                    },
                    'nivel_acesso': {
                        'type': 'choice', 'required': True,
                        'choices': list(NivelAcesso.objects.filter(is_active=True).values('id', 'code', 'name', 'nivel'))
                    },
                    'responsavel_direto': {
                        'type': 'choice', 'required': False,
                        'choices': [
                            {'id': p.id, 'name': f"{p.user.get_full_name()} ({p.cargo.name})"}
                            for p in PerfilInterno.objects.select_related('user', 'cargo').all()
                        ]
                    }
                },
                'example_request': {
                    'email': 'funcionario@empresa.com',
                    'username': 'funcionario123',
                    'first_name': 'Maria',
                    'last_name': 'Santos',
                    'preferencia_idioma': 1,
                    'password': 'senha123',
                    'password_confirm': 'senha123',
                    'perfil_interno': {
                        'cargo': 1,
                        'departamento': 2,
                        'nivel_acesso': 3
                    }
                }
            },
            {
                'code': 'subcontratado',
                'name': 'Subcontratado',
                'endpoint': '/api/auth/register/subcontratado/',
                'structure': 'nested',
                'base_fields': base_fields,
                'perfil_fields': {
                    'empresa': {'type': 'string', 'required': True},
                    'classificacao': {'type': 'number', 'required': False, 'min': 0, 'max': 5},
                    'documentos_verificados': {'type': 'boolean', 'required': False}
                },
                'example_request': {
                    'email': 'contato@empresa.com',
                    'username': 'empresa123',
                    'first_name': 'Pedro',
                    'last_name': 'Silva',
                    'preferencia_idioma': 1,
                    'password': 'senha123',
                    'password_confirm': 'senha123',
                    'perfil_subcontratado': {
                        'empresa': 'Empresa XYZ Ltda',
                        'classificacao': 4.5,
                        'documentos_verificados': True
                    }
                }
            },
            {
                'code': 'fornecedor',
                'name': 'Fornecedor',
                'endpoint': '/api/auth/register/fornecedor/',
                'structure': 'nested',
                'base_fields': base_fields,
                'perfil_fields': {
                    'empresa': {'type': 'string', 'required': True},
                    'prazo_medio_entrega': {'type': 'number', 'required': False, 'default': 7},
                    'condicoes_pagamento': {
                        'type': 'choice', 'required': True,
                        'choices': list(CondicaoPagamento.objects.filter(is_active=True).values('id', 'code', 'name'))
                    }
                },
                'example_request': {
                    'email': 'vendas@fornecedor.com',
                    'username': 'fornecedor123',
                    'first_name': 'Ana',
                    'last_name': 'Costa',
                    'preferencia_idioma': 1,
                    'password': 'senha123',
                    'password_confirm': 'senha123',
                    'perfil_fornecedor': {
                        'empresa': 'Fornecedor ABC',
                        'prazo_medio_entrega': 5,
                        'condicoes_pagamento': 1
                    }
                }
            }
        ]
    }

    return Response(response_data)
