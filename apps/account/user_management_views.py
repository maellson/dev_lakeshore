# apps/account/user_management_views.py - IMPLEMENTAR

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from .models import CustomUser
from .admin_views import IsAdminOrDirector
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.swagger_tags import API_TAGS


class UserGroupAddView(APIView):
    """Adicionar usuário a grupo"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        operation_id='add_user_to_group',
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Adicionar usuário a grupo",
        operation_description="Adiciona um usuário a um grupo específico",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['group_name'],
            properties={
                'group_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do grupo')
            }
        ),
        responses={
            200: 'Usuário adicionado ao grupo',
            404: 'Usuário ou grupo não encontrado'
        }
    )
    def post(self, request, user_id):
        """Adicionar usuário a grupo"""
        try:
            user = CustomUser.objects.get(id=user_id)
            group_name = request.data.get('group_name')
            group = Group.objects.get(name=group_name)

            user.groups.add(group)

            return Response({
                'message': f'Usuário {user.email} adicionado ao grupo {group_name}',
                'user_groups': [g.name for g in user.groups.all()]
            })

        except (CustomUser.DoesNotExist, Group.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class UserGroupRemoveView(APIView):
    """Remover usuário de grupo"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        operation_id='remove_user_from_group',
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Remover usuário de grupo",
        operation_description="Remove um usuário de um grupo específico",
        responses={
            200: 'Usuário removido do grupo',
            404: 'Usuário ou grupo não encontrado'
        }
    )
    def delete(self, request, user_id, group_name):
        """Remover usuário de grupo"""
        try:
            user = CustomUser.objects.get(id=user_id)
            group = Group.objects.get(name=group_name)

            user.groups.remove(group)

            return Response({
                'message': f'Usuário {user.email} removido do grupo {group_name}'
            })

        except (CustomUser.DoesNotExist, Group.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class GroupManagementView(APIView):
    """Gerenciar grupos do sistema"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Listar grupos",
        operation_description="Lista todos os grupos do sistema com suas permissões",
        responses={200: 'Lista de grupos'}
    )
    def get(self, request):
        """Listar todos os grupos"""
        groups = Group.objects.all()

        result = []
        for group in groups:
            users_count = group.user_set.count()
            permissions = [p.codename for p in group.permissions.all()]

            result.append({
                'id': group.id,
                'name': group.name,
                'users_count': users_count,
                'permissions': permissions
            })

        return Response({
            'groups': result,
            'total': len(result)
        })

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Criar grupo",
        operation_description="Cria um novo grupo com permissões",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do grupo'),
                'permissions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='Lista de codenames de permissões'
                )
            }
        ),
        responses={
            201: 'Grupo criado com sucesso',
            400: 'Grupo já existe'
        }
    )
    def post(self, request):
        """Criar novo grupo"""
        group_name = request.data.get('name')
        permissions = request.data.get('permissions', [])

        if Group.objects.filter(name=group_name).exists():
            return Response(
                {'error': 'Grupo já existe'},
                status=status.HTTP_400_BAD_REQUEST
            )

        group = Group.objects.create(name=group_name)

        # Adicionar permissões
        for perm_codename in permissions:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass

        return Response({
            'message': f'Grupo {group_name} criado com sucesso',
            'group': {
                'id': group.id,
                'name': group.name,
                'permissions': permissions
            }
        }, status=status.HTTP_201_CREATED)


class UserPermissionAddView(APIView):
    """Adicionar permissão a usuário"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        operation_id='add_user_permission',
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Adicionar permissão a usuário",
        operation_description="Adiciona uma permissão específica a um usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['permission'],
            properties={
                'permission': openapi.Schema(type=openapi.TYPE_STRING, description='Codename da permissão')
            }
        ),
        responses={
            200: 'Permissão adicionada ao usuário',
            404: 'Usuário ou permissão não encontrada'
        }
    )
    def post(self, request, user_id):
        """Dar permissão específica a usuário"""
        try:
            user = CustomUser.objects.get(id=user_id)
            permission_codename = request.data.get('permission')
            permission = Permission.objects.get(codename=permission_codename)

            user.user_permissions.add(permission)

            return Response({
                'message': f'Permissão {permission.name} adicionada ao usuário {user.email}'
            })

        except CustomUser.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=404)
        except Permission.DoesNotExist:
            return Response({'error': 'Permissão não encontrada'}, status=404)


class UserPermissionRemoveView(APIView):
    """Remover permissão de usuário"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        operation_id='remove_user_permission',
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Remover permissão de usuário",
        operation_description="Remove uma permissão específica de um usuário",
        responses={
            200: 'Permissão removida do usuário',
            404: 'Usuário ou permissão não encontrada'
        }
    )
    def delete(self, request, user_id, permission_codename):
        """Remover permissão específica de usuário"""
        try:
            user = CustomUser.objects.get(id=user_id)
            permission = Permission.objects.get(codename=permission_codename)

            user.user_permissions.remove(permission)

            return Response({
                'message': f'Permissão {permission.name} removida do usuário {user.email}'
            })

        except (CustomUser.DoesNotExist, Permission.DoesNotExist) as e:
            return Response({'error': str(e)}, status=404)


class PermissionsMatrixView(APIView):
    """Matriz visual de usuários x permissões"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Matriz de permissões",
        operation_description="Gera uma matriz completa de usuários x permissões",
        responses={200: 'Matriz de permissões'}
    )
    def get(self, request):
        """Gerar matriz completa de permissões"""
        users = CustomUser.objects.filter(tipo_usuario__code='INTERNO')
        groups = Group.objects.all()

        matrix = []
        for user in users:
            user_data = {
                'user_id': user.id,
                'email': user.email,
                'nome_completo': user.get_full_name(),
                'tipo_usuario': {
                    'code': user.tipo_usuario.code,
                    'name': user.tipo_usuario.name,
                    'description': user.tipo_usuario.description
                } if user.tipo_usuario else None,
                'groups': [g.name for g in user.groups.all()],
                'user_permissions': [p.codename for p in user.user_permissions.all()],
                'all_permissions': list(user.get_all_permissions()),
                'is_active': user.is_active,
                'nivel_acesso': {
                    'nivel': user.perfil_interno.nivel_acesso.nivel,
                    'code': user.perfil_interno.nivel_acesso.code,
                    'name': user.perfil_interno.nivel_acesso.name
                } if hasattr(user, 'perfil_interno') and user.perfil_interno and user.perfil_interno.nivel_acesso else None
            }
            matrix.append(user_data)

        groups_data = []
        for group in groups:
            groups_data.append({
                'name': group.name,
                'permissions': [p.codename for p in group.permissions.all()],
                'users_count': group.user_set.count()
            })

        return Response({
            'users_matrix': matrix,
            'groups': groups_data,
            'summary': {
                'total_users': len(matrix),
                'total_groups': len(groups_data),
                'active_users': len([u for u in matrix if u['is_active']])
            }
        })


class UserActivationView(APIView):
    """Ativar/desativar usuários"""
    permission_classes = [IsAdminOrDirector]

    @swagger_auto_schema(
        tags=[API_TAGS['ACCOUNT']],
        operation_summary="Ativar/desativar usuário",
        operation_description="Ativa ou desativa um usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['action'],
            properties={
                'action': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Ação a ser executada (activate ou deactivate)',
                    enum=['activate', 'deactivate']
                )
            }
        ),
        responses={
            200: 'Usuário ativado/desativado',
            400: 'Ação inválida',
            404: 'Usuário não encontrado'
        }
    )
    def post(self, request, user_id):
        """Ativar/desativar usuário"""
        try:
            user = CustomUser.objects.get(id=user_id)
            action = request.data.get('action')  # 'activate' or 'deactivate'

            if action == 'activate':
                user.is_active = True
                message = f'Usuário {user.email} ativado'
            elif action == 'deactivate':
                user.is_active = False
                message = f'Usuário {user.email} desativado'
            else:
                return Response({'error': 'Ação inválida'}, status=400)

            user.save()

            return Response({
                'message': message,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_active': user.is_active
                }
            })

        except CustomUser.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=404)
