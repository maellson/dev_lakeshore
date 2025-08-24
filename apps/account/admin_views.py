from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from .models import CustomUser, PerfilInterno
from .serializers import UserProfileSerializer
from .choice_types import NivelAcesso, Cargo, Departamento
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.swagger_tags import API_TAGS


class IsAdminOrDirector(permissions.BasePermission):
    """Permissão customizada para admins e diretores"""

    def has_permission(self, request, view):
        # print(f"🔍 USER DEBUG:")
        # print(f"  ✅ Authenticated: {request.user.is_authenticated}")
        # print(
        #   f"  ✅ User: {request.user.email if request.user.is_authenticated else 'Anonymous'}")

        if not request.user.is_authenticated:
            # print(f"  ❌ Não autenticado")
            return False

        # ✅ SUPERUSER TEM ACESSO A TUDO
        if request.user.is_superuser:
            return True

        # print(f"  ✅ Tipo usuário: {request.user.tipo_usuario}")
        # print(
         #   f"  ✅ Tipo code: {request.user.tipo_usuario.code if request.user.tipo_usuario else 'None'}")

        if not request.user.tipo_usuario or request.user.tipo_usuario.code != 'INTERNO':
            # print(f"  ❌ Não é usuário interno")
            return False

        # print(
        #    f"  ✅ Has perfil_interno: {hasattr(request.user, 'perfil_interno')}")

        if not hasattr(request.user, 'perfil_interno'):
            # print(f"  ❌ Não tem perfil interno")
            return False

        try:
            nivel_acesso = request.user.perfil_interno.nivel_acesso.nivel
            # print(f"  ✅ Nível acesso: {nivel_acesso}")
            resultado = nivel_acesso >= 4
            # print(f"  ✅ Tem acesso (>=4): {resultado}")
            return resultado
        except (AttributeError, TypeError) as e:
            # print(f"  ❌ Erro ao acessar nível: {e}")
            return False


class UserNivelAcessoView(APIView):
    """Gerenciar nível de acesso de usuários"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Atualizar nível de acesso",
        operation_description="Atualiza o nível de acesso, cargo e departamento de um usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nivel_acesso_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do nível de acesso'),
                'cargo_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do cargo'),
                'departamento_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do departamento')
            }
        ),
        responses={
            200: 'Usuário atualizado com sucesso',
            400: 'Dados inválidos',
            403: 'Sem permissão',
            404: 'Usuário não encontrado'
        }
    )
    def patch(self, request, user_id):
        """Atualizar nível de acesso de usuário"""

        try:
            target_user = CustomUser.objects.get(
                id=user_id, tipo_usuario__code='INTERNO')

            # Verificar se pode gerenciar este usuário
            if not self.can_manage_user(request.user, target_user):
                return Response({
                    'error': 'Sem permissão para alterar este usuário'
                }, status=status.HTTP_403_FORBIDDEN)

            perfil = target_user.perfil_interno

            # carregar os dados par avalidação antes:
            novo_nivel_id = request.data.get(
                'nivel_acesso_id')  # ID do NivelAcesso
            novo_cargo_id = request.data.get('cargo_id')        # ID do Cargo
            novo_depto_id = request.data.get(
                'departamento_id')  # ID do Departamento

            if novo_nivel_id:
                try:
                    novo_nivel = NivelAcesso.objects.get(id=novo_nivel_id)
                    if not self.can_set_level(request.user, novo_nivel.nivel):
                        return Response({
                            'error': f'Sem permissão para definir nível {novo_nivel.nivel}'
                        }, status=status.HTTP_403_FORBIDDEN)
                    perfil.nivel_acesso = novo_nivel
                except NivelAcesso.DoesNotExist:
                    return Response({'error': 'Nível de acesso inválido'}, status=400)

            if novo_cargo_id:
                try:
                    novo_cargo = Cargo.objects.get(id=novo_cargo_id)
                    perfil.cargo = novo_cargo
                except Cargo.DoesNotExist:
                    return Response({'error': 'Cargo inválido'}, status=400)

            if novo_depto_id:
                try:
                    novo_depto = Departamento.objects.get(id=novo_depto_id)
                    perfil.departamento = novo_depto
                except Departamento.DoesNotExist:
                    return Response({'error': 'Departamento inválido'}, status=400)

            perfil.save()

            return Response({
                'message': 'Usuário atualizado com sucesso',
                'user': {
                    'id': target_user.id,
                    'email': target_user.email,
                    'nome_completo': target_user.get_full_name(),
                    'nivel_acesso': {
                        'nivel': perfil.nivel_acesso.nivel,
                        'code': perfil.nivel_acesso.code,
                        'name': perfil.nivel_acesso.name
                    },
                    'cargo': {
                        'code': perfil.cargo.code,
                        'name': perfil.cargo.name
                    } if perfil.cargo else None,
                    'departamento': {
                        'code': perfil.departamento.code,
                        'name': perfil.departamento.name
                    } if perfil.departamento else None
                }
            })

        except CustomUser.DoesNotExist:
            return Response({
                'error': 'Usuário não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

    def can_manage_user(self, admin_user, target_user):
        """Verificar se admin pode gerenciar o usuário alvo"""
        admin_nivel = admin_user.perfil_interno.nivel_acesso.nivel
        target_nivel = target_user.perfil_interno.nivel_acesso.nivel

        # Admin (5) pode gerenciar qualquer um
        if admin_nivel == 5:
            return True

        # Diretoria (4) pode gerenciar níveis 1-3
        if admin_nivel == 4 and target_nivel <= 3:
            return True

        return False

    def can_set_level(self, admin_user, new_level):
        """Verificar se admin pode definir determinado nível"""
        admin_nivel = admin_user.perfil_interno.nivel_acesso.nivel

        # Admin (5) pode definir qualquer nível
        if admin_nivel == 5:
            return True

        # Diretoria (4) só pode definir níveis 1-3
        if admin_nivel == 4 and new_level <= 3:
            return True

        return False


class UserListByLevelView(APIView):
    """Listar usuários por nível de acesso"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Listar usuários por nível - Internos",
        operation_description="Lista usuários filtrados por nível de acesso e departamento",
        manual_parameters=[
            openapi.Parameter('nivel_acesso', openapi.IN_QUERY,
                              description="Filtrar por nível de acesso", type=openapi.TYPE_INTEGER),
            openapi.Parameter('departamento', openapi.IN_QUERY,
                              description="Filtrar por departamento", type=openapi.TYPE_STRING)
        ],
        responses={200: 'Lista de usuários'}
    )
    def get(self, request):
        nivel_filtro = request.query_params.get('nivel_acesso')
        departamento_filtro = request.query_params.get('departamento')

        # Filtrar usuários internos QUE POSSUEM PERFIL_INTERNO
        usuarios = CustomUser.objects.filter(
            tipo_usuario__code='INTERNO',
            perfil_interno__isnull=False  # ← Garantir que tem perfil
        ).select_related('perfil_interno__nivel_acesso', 'perfil_interno__cargo', 'perfil_interno__departamento')

        # Aplicar filtros
        if nivel_filtro:
            usuarios = usuarios.filter(
                perfil_interno__nivel_acesso__nivel=nivel_filtro)

        if departamento_filtro:
            usuarios = usuarios.filter(
                perfil_interno__departamento__code__icontains=departamento_filtro)

        # Verificar permissões (evitar query duplicada)
        if not request.user.is_superuser:
            if hasattr(request.user, 'perfil_interno') and request.user.perfil_interno:
                admin_nivel = request.user.perfil_interno.nivel_acesso.nivel
                if admin_nivel < 5:  # Se não é Admin supremo
                    usuarios = usuarios.filter(
                        perfil_interno__nivel_acesso__nivel__lt=admin_nivel)

        # Serializar dados
        result = []
        for user in usuarios:
            # Verificação adicional de segurança
            if not hasattr(user, 'perfil_interno') or not user.perfil_interno:
                continue  # Pular usuários sem perfil
                
            perfil = user.perfil_interno
            result.append({
                'id': user.id,
                'email': user.email,
                'nome_completo': user.get_full_name(),
                'nivel_acesso': {
                    'nivel': perfil.nivel_acesso.nivel,          # ← Número
                    'code': perfil.nivel_acesso.code,           # ← Código
                    'name': perfil.nivel_acesso.name            # ← Nome
                },
                'cargo': {
                    'code': perfil.cargo.code,
                    'name': perfil.cargo.name
                } if perfil.cargo else None,
                'departamento': {
                    'code': perfil.departamento.code,
                    'name': perfil.departamento.name
                } if perfil.departamento else None,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login
            })

        return Response({
            'usuarios': result,
            'total': len(result),
            'filtros_aplicados': {
                'nivel_acesso': nivel_filtro,
                'departamento': departamento_filtro
            }
        })


class HierarchyDashboardView(APIView):
    """Dashboard hierárquico da organização"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Dashboard hierárquico",
        operation_description="Retorna dados para o dashboard hierárquico da organização",
        responses={200: 'Dashboard hierárquico'}
    )
    def get(self, request):
        # Contar usuários por nível
        niveis_count = {}
        for nivel, display in PerfilInterno.NIVEL_ACESSO_CHOICES:
            count = PerfilInterno.objects.filter(nivel_acesso=nivel).count()
            niveis_count[nivel] = {
                'nome': display,
                'count': count
            }

        # Departamentos e seus usuários
        departamentos = {}
        perfis = PerfilInterno.objects.select_related('usuario').all()

        for perfil in perfis:
            dept = perfil.departamento or 'Não definido'
            if dept not in departamentos:
                departamentos[dept] = []

            departamentos[dept].append({
                'usuario': perfil.user.get_full_name(),
                'email': perfil.user.email,
                'nivel': perfil.get_nivel_acesso_display(),
                'cargo': perfil.cargo
            })

        # Usuários ativos vs inativos
        usuarios_stats = {
            'total': CustomUser.objects.filter(tipo_usuario__code='INTERNO').count(),
            'ativos': CustomUser.objects.filter(tipo_usuario__code='INTERNO', is_active=True).count(),
            'inativos': CustomUser.objects.filter(tipo_usuario__code='INTERNO', is_active=False).count(),
        }

        return Response({
            'niveis_hierarquia': niveis_count,
            'departamentos': departamentos,
            'estatisticas_usuarios': usuarios_stats,
            'admin_logado': {
                'email': request.user.email,
                'nivel': request.user.perfil_interno.get_nivel_acesso_display(),
                'pode_gerenciar': list(range(1, request.user.perfil_interno.nivel_acesso))
            }
        })


@swagger_auto_schema(
    method='get',
    tags=[API_TAGS['ACCOUNT']],
    operation_summary="Listar permissões",
    operation_description="Lista todas as permissões disponíveis no sistema",
    responses={200: 'Lista de permissões'}
)
@api_view(['GET'])
@permission_classes([IsAdminOrDirector])
def list_all_permissions_view(request):
    """Listar todas as permissões disponíveis no sistema"""
    from django.contrib.auth.models import Permission

    permissions = Permission.objects.all().values(
        'id', 'name', 'codename', 'content_type__app_label', 'content_type__model'
    )

    # Agrupar por app
    permissions_by_app = {}
    for perm in permissions:
        app = perm['content_type__app_label']
        if app not in permissions_by_app:
            permissions_by_app[app] = []
        permissions_by_app[app].append(perm)

    return Response({
        'permissions_by_app': permissions_by_app,
        'total_permissions': len(permissions)
    })
