🎯 ETAPA 2: SISTEMA DE PERMISSIONS
2.1 Expandir Account Models:

Criar Permission customizada (além das do Django)
Criar Role que agrupa permissions
Relacionar CustomUser com Role
Manter PerfilInterno.permissoes_especiais para casos únicos

2.2 Permissions por Módulo:

Projects: view_project, edit_project, delete_project, view_all_projects
Contracts: view_contract, edit_contract, approve_contract
Financial: view_budget, edit_budget, approve_payments
Reports: view_reports, export_data
Admin: manage_users, system_settings

2.3 Hierarquia de Roles:

Admin: Todas as permissions
Manager: Permissions de gestão (sem admin)
Supervisor: Permissions operacionais
Employee: Permissions básicas
Client: Permissions limitadas do portal