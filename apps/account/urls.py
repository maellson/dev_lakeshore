from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    UserProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    user_permissions_view,
    verify_token_view,
    choices_view,
    # Novas views para verificação de email
    VerifyEmailView,
    ResendEmailVerificationView,
    registration_choices_view,
    DynamicRegisterView,  # Renamed for clarity
    AllUsersListView,  # Renamed for clarity
    user_types_and_fields_view  # Renamed for clarity
)
from .admin_views import (
    UserNivelAcessoView,
    UserListByLevelView,
    HierarchyDashboardView,
    list_all_permissions_view
)

from .user_management_views import (
    UserGroupAddView,
    UserGroupRemoveView,
    GroupManagementView,
    UserPermissionAddView,
    UserPermissionRemoveView,
    PermissionsMatrixView,
    UserActivationView
)
# from core.views import auth_endpoints_view

app_name = 'account'

urlpatterns = [
    # =====================================================
    # AUTENTICAÇÃO JWT
    # =====================================================
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', verify_token_view, name='verify_token'),


    # =====================================================
    # REGISTRO DE USUÁRIOS
    # =====================================================
    path('register/<str:tipo_usuario>/', DynamicRegisterView.as_view(), name='dynamic_register'),
    path('user-types/', user_types_and_fields_view, name='user_types'),
    path('registration-help/', registration_choices_view, name='registration_help'),



    # =====================================================
    # GESTÃO DE USUÁRIOS
    # =====================================================
    path('users/', AllUsersListView.as_view(), name='all_users_list'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('permissions/', user_permissions_view, name='user_permissions'),
    path('logout/', LogoutView.as_view(), name='logout'),


    # =====================================================
    # RECUPERAÇÃO DE SENHA
    # =====================================================
    path('password-reset/', PasswordResetRequestView.as_view(),
         name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

     # =====================================================
    # VERIFICAÇÃO DE EMAIL
    # =====================================================
    path('verify-email/<uuid:token>/',
         VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendEmailVerificationView.as_view(),
         name='resend_verification'),


    # =====================================================
    # APIs ADMINISTRATIVAS (Nível 4+)
    # =====================================================
    path('admin/users/<int:user_id>/nivel-acesso/',
         UserNivelAcessoView.as_view(), name='user_nivel_acesso'),
    path('admin/users/', UserListByLevelView.as_view(), name='user_list_by_level'),
    path('admin/hierarchy/', HierarchyDashboardView.as_view(),
         name='hierarchy_dashboard'),
    path('admin/permissions/', list_all_permissions_view, name='list_permissions'),

    # =====================================================
    # GESTÃO DE GRUPOS E PERMISSÕES
    # ====================================================
    path('admin/users/<int:user_id>/groups/', UserGroupAddView.as_view(), name='user_group_add'),
    path('admin/users/<int:user_id>/groups/<str:group_name>/', UserGroupRemoveView.as_view(), name='user_group_remove'),
    path('admin/groups/', GroupManagementView.as_view(), name='groups_management'),
    path('admin/users/<int:user_id>/permissions/', UserPermissionAddView.as_view(), name='user_permission_add'),
    path('admin/users/<int:user_id>/permissions/<str:permission_codename>/', UserPermissionRemoveView.as_view(), name='user_permission_remove'),
    path('admin/permissions-matrix/', PermissionsMatrixView.as_view(), name='permissions_matrix'),
    path('admin/users/<int:user_id>/activation/', UserActivationView.as_view(), name='user_activation'),

    
    # =====================================================
    # UTILITÁRIOS (existentes)
    # =====================================================

    path('choices/', choices_view, name='choices'),
   


]
