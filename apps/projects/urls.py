# apps/projects/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IncorporationViewSet,
    ContractViewSet,
    ProjectViewSet,
    PhaseProjectViewSet,
    TaskProjectViewSet,
    ContactViewSet,
    ModelProjectViewSet,
    ModelPhaseViewSet,
    ModelTaskViewSet,
    CostGroupViewSet,
    CostSubGroupViewSet,
    ProductionCellViewSet,


    # NOVAS ViewSets - Choice Types
    ProjectTypeViewSet,
    ProjectStatusViewSet,
    IncorporationTypeViewSet,
    IncorporationStatusViewSet,
    StatusContractViewSet,
    PaymentMethodViewSet,
    OwnerTypeViewSet,

    # NOVAS ViewSets - Contract Management
    ContractOwnerViewSet,
    ContractProjectViewSet,

    # NOVAS ViewSets - Task Resources
    #TaskResourceViewSet,

)

# Router para ViewSets
router = DefaultRouter()
# Endpoints principais
router.register(r'incorporations', IncorporationViewSet,
                basename='incorporation')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'phases', PhaseProjectViewSet, basename='phase')
router.register(r'tasks', TaskProjectViewSet, basename='task')
router.register(r'contacts', ContactViewSet, basename='contact')

# Endpoints para Model Templates
router.register(r'model-projects', ModelProjectViewSet,
                basename='model-project')
router.register(r'model-phases', ModelPhaseViewSet, basename='model-phase')
router.register(r'model-tasks', ModelTaskViewSet, basename='model-task')

# Endpoints para Cost Management
router.register(r'cost-groups', CostGroupViewSet, basename='cost-group')
router.register(r'cost-subgroups', CostSubGroupViewSet,
                basename='cost-subgroup')

# Endpoints para Production Cells
router.register(r'production-cells', ProductionCellViewSet,
                basename='production-cell')

# NOVOS ENDPOINTS - CHOICE TYPES

router.register(r'project-types', ProjectTypeViewSet, basename='project-type')
router.register(r'project-status', ProjectStatusViewSet,
                basename='project-status')
router.register(r'incorporation-types', IncorporationTypeViewSet,
                basename='incorporation-type')
router.register(r'incorporation-status',
                IncorporationStatusViewSet, basename='incorporation-status')
router.register(r'contract-status', StatusContractViewSet,
                basename='contract-status')
router.register(r'payment-methods', PaymentMethodViewSet,
                basename='payment-method')
router.register(r'owner-types', OwnerTypeViewSet, basename='owner-type')

# NOVOS ENDPOINTS - CONTRACT MANAGEMENT
router.register(r'contract-owners', ContractOwnerViewSet,
                basename='contract-owner')
router.register(r'contract-projects', ContractProjectViewSet,
                basename='contract-project')

# NOVOS ENDPOINTS - TASK RESOURCES
#router.register(r'task-resources', TaskResourceViewSet, basename='task-resource')

# URLs do app
app_name = 'projects'

urlpatterns = [
    # API endpoints via router
    path('', include(router.urls)),
]

"""
ENDPOINTS DISPONÍVEIS:

## INCORPORATIONS ENDPOINTS
GET    /api/projects/incorporations/                    - Lista incorporações com filtros
POST   /api/projects/incorporations/                    - Criar nova incorporação
GET    /api/projects/incorporations/{id}/               - Detalhes de incorporação
PATCH  /api/projects/incorporations/{id}/               - Atualizar incorporação
DELETE /api/projects/incorporations/{id}/               - Remover incorporação
GET    /api/projects/incorporations/{id}/projects/      - Listar projetos da incorporação
GET    /api/projects/incorporations/{id}/contracts/     - Listar contratos da incorporação
GET    /api/projects/incorporations/stats/              - Estatísticas de incorporações
GET    /api/projects/incorporations/dashboard/          - Dashboard de incorporações
GET    /api/projects/incorporations/export/             - Exportar incorporações (CSV/Excel)

## CONTRACTS ENDPOINTS
GET    /api/projects/contracts/                         - Lista contratos com filtros
POST   /api/projects/contracts/                         - Criar novo contrato
GET    /api/projects/contracts/{id}/                    - Detalhes de contrato
PATCH  /api/projects/contracts/{id}/                    - Atualizar contrato
DELETE /api/projects/contracts/{id}/                    - Remover contrato
GET    /api/projects/contracts/{id}/projects/           - Listar projetos do contrato
GET    /api/projects/contracts/{id}/owners/             - Listar proprietários do contrato
GET    /api/projects/contracts/stats/                   - Estatísticas de contratos
GET    /api/projects/contracts/dashboard/               - Dashboard de contratos
GET    /api/projects/contracts/export/                  - Exportar contratos (CSV/Excel)

## PROJECTS ENDPOINTS
GET    /api/projects/projects/                          - Lista projetos com filtros
POST   /api/projects/projects/                          - Criar novo projeto
GET    /api/projects/projects/{id}/                     - Detalhes de projeto
PATCH  /api/projects/projects/{id}/                     - Atualizar projeto
DELETE /api/projects/projects/{id}/                     - Remover projeto
GET    /api/projects/projects/{id}/phases/              - Listar fases do projeto
GET    /api/projects/projects/{id}/tasks/               - Listar tarefas do projeto
GET    /api/projects/projects/stats/                    - Estatísticas de projetos
GET    /api/projects/projects/dashboard/                - Dashboard de projetos
GET    /api/projects/projects/export/                   - Exportar projetos (CSV/Excel)

## PHASES ENDPOINTS
GET    /api/projects/phases/                            - Lista fases com filtros
POST   /api/projects/phases/                            - Criar nova fase
GET    /api/projects/phases/{id}/                       - Detalhes de fase
PATCH  /api/projects/phases/{id}/                       - Atualizar fase
DELETE /api/projects/phases/{id}/                       - Remover fase
GET    /api/projects/phases/{id}/tasks/                 - Listar tarefas da fase
POST   /api/projects/phases/{id}/start/                 - Iniciar fase
POST   /api/projects/phases/{id}/complete/              - Completar fase
POST   /api/projects/phases/{id}/schedule-inspection/   - Agendar inspeção
GET    /api/projects/phases/export/                     - Exportar fases (CSV/Excel)

## TASKS ENDPOINTS
GET    /api/projects/tasks/                             - Lista tarefas com filtros
POST   /api/projects/tasks/                             - Criar nova tarefa
GET    /api/projects/tasks/{id}/                        - Detalhes de tarefa
PATCH  /api/projects/tasks/{id}/                        - Atualizar tarefa
DELETE /api/projects/tasks/{id}/                        - Remover tarefa
POST   /api/projects/tasks/{id}/start/                  - Iniciar tarefa
POST   /api/projects/tasks/{id}/pause/                  - Pausar tarefa
POST   /api/projects/tasks/{id}/resume/                 - Retomar tarefa
POST   /api/projects/tasks/{id}/complete/               - Completar tarefa
GET    /api/projects/tasks/stats/                       - Estatísticas de tarefas
GET    /api/projects/tasks/export/                      - Exportar tarefas (CSV/Excel)

## CONTACTS ENDPOINTS
GET    /api/projects/contacts/                          - Lista contatos com filtros
POST   /api/projects/contacts/                          - Criar novo contato
GET    /api/projects/contacts/{id}/                     - Detalhes de contato
PATCH  /api/projects/contacts/{id}/                     - Atualizar contato
DELETE /api/projects/contacts/{id}/                     - Remover contato
GET    /api/projects/contacts/by-project/{project_id}/  - Listar contatos por projeto
GET    /api/projects/contacts/by-owner/{owner_id}/      - Listar contatos por proprietário
GET    /api/projects/contacts/by-user/{user_id}/        - Listar contatos por usuário
GET    /api/projects/contacts/export/                   - Exportar contatos (CSV/Excel)

## MODEL PROJECTS ENDPOINTS (NOVOS)
GET    /api/projects/model-projects/                    - Lista modelos de projeto com filtros
POST   /api/projects/model-projects/                    - Criar novo modelo de projeto
GET    /api/projects/model-projects/{id}/               - Detalhes de modelo de projeto
PATCH  /api/projects/model-projects/{id}/               - Atualizar modelo de projeto
DELETE /api/projects/model-projects/{id}/               - Remover modelo de projeto
GET    /api/projects/model-projects/{id}/phases/        - Listar fases do modelo
POST   /api/projects/model-projects/{id}/duplicate/     - Duplicar modelo para outro county
GET    /api/projects/model-projects/stats/              - Estatísticas de modelos de projeto
GET    /api/projects/model-projects/export/             - Exportar modelos (CSV/Excel)

## MODEL PHASES ENDPOINTS (NOVOS)
GET    /api/projects/model-phases/                      - Lista fases de modelo com filtros
POST   /api/projects/model-phases/                      - Criar nova fase de modelo
GET    /api/projects/model-phases/{id}/                 - Detalhes de fase de modelo
PATCH  /api/projects/model-phases/{id}/                 - Atualizar fase de modelo
DELETE /api/projects/model-phases/{id}/                 - Remover fase de modelo
GET    /api/projects/model-phases/{id}/tasks/           - Listar tarefas da fase
POST   /api/projects/model-phases/{id}/duplicate/       - Duplicar fase para outro modelo
GET    /api/projects/model-phases/stats/                - Estatísticas de fases de modelo
GET    /api/projects/model-phases/export/               - Exportar fases (CSV/Excel)

## MODEL TASKS ENDPOINTS (NOVOS)
GET    /api/projects/model-tasks/                       - Lista tarefas de modelo com filtros
POST   /api/projects/model-tasks/                       - Criar nova tarefa de modelo
GET    /api/projects/model-tasks/{id}/                  - Detalhes de tarefa de modelo
PATCH  /api/projects/model-tasks/{id}/                  - Atualizar tarefa de modelo
DELETE /api/projects/model-tasks/{id}/                  - Remover tarefa de modelo
POST   /api/projects/model-tasks/{id}/duplicate/        - Duplicar tarefa para outra fase
GET    /api/projects/model-tasks/stats/                 - Estatísticas de tarefas de modelo
GET    /api/projects/model-tasks/export/                - Exportar tarefas (CSV/Excel)

## COST GROUPS ENDPOINTS (NOVOS)
GET    /api/projects/cost-groups/                       - Lista grupos de custo com filtros
POST   /api/projects/cost-groups/                       - Criar novo grupo de custo
GET    /api/projects/cost-groups/{id}/                  - Detalhes de grupo de custo
PATCH  /api/projects/cost-groups/{id}/                  - Atualizar grupo de custo
DELETE /api/projects/cost-groups/{id}/                  - Remover grupo de custo
GET    /api/projects/cost-groups/{id}/subgroups/        - Listar subgrupos do grupo
GET    /api/projects/cost-groups/stats/                 - Estatísticas de grupos de custo
GET    /api/projects/cost-groups/export/                - Exportar grupos (CSV/Excel)

## COST SUBGROUPS ENDPOINTS (NOVOS)
GET    /api/projects/cost-subgroups/                    - Lista subgrupos de custo com filtros
POST   /api/projects/cost-subgroups/                    - Criar novo subgrupo de custo
GET    /api/projects/cost-subgroups/{id}/               - Detalhes de subgrupo de custo
PATCH  /api/projects/cost-subgroups/{id}/               - Atualizar subgrupo de custo
DELETE /api/projects/cost-subgroups/{id}/               - Remover subgrupo de custo
GET    /api/projects/cost-subgroups/stats/              - Estatísticas de subgrupos de custo
GET    /api/projects/cost-subgroups/export/             - Exportar subgrupos (CSV/Excel)

## PRODUCTION CELLS ENDPOINTS (NOVOS)
GET    /api/projects/production-cells/                  - Lista células de produção com filtros
POST   /api/projects/production-cells/                  - Criar nova célula de produção
GET    /api/projects/production-cells/{id}/             - Detalhes de célula de produção
PATCH  /api/projects/production-cells/{id}/             - Atualizar célula de produção
DELETE /api/projects/production-cells/{id}/             - Remover célula de produção
GET    /api/projects/production-cells/stats/            - Estatísticas de células de produção
GET    /api/projects/production-cells/export/           - Exportar células (CSV/Excel)


NOVOS ENDPOINTS ADICIONADOS:

## CHOICE TYPES ENDPOINTS (NOVOS)
GET    /api/projects/project-types/                     - Lista tipos de projeto
POST   /api/projects/project-types/                     - Criar novo tipo
GET    /api/projects/project-types/{id}/                - Detalhes do tipo
PATCH  /api/projects/project-types/{id}/                - Atualizar tipo
DELETE /api/projects/project-types/{id}/                - Remover tipo
GET    /api/projects/project-types/stats/               - Estatísticas

GET    /api/projects/project-status/                    - Lista status de projeto
POST   /api/projects/project-status/                    - Criar novo status
GET    /api/projects/project-status/{id}/               - Detalhes do status
PATCH  /api/projects/project-status/{id}/               - Atualizar status
DELETE /api/projects/project-status/{id}/               - Remover status
GET    /api/projects/project-status/stats/              - Estatísticas

GET    /api/projects/incorporation-types/               - Lista tipos de incorporação
POST   /api/projects/incorporation-types/               - Criar novo tipo
GET    /api/projects/incorporation-types/{id}/          - Detalhes do tipo
PATCH  /api/projects/incorporation-types/{id}/          - Atualizar tipo
DELETE /api/projects/incorporation-types/{id}/          - Remover tipo

GET    /api/projects/incorporation-status/              - Lista status de incorporação
POST   /api/projects/incorporation-status/              - Criar novo status
GET    /api/projects/incorporation-status/{id}/         - Detalhes do status
PATCH  /api/projects/incorporation-status/{id}/         - Atualizar status
DELETE /api/projects/incorporation-status/{id}/         - Remover status

GET    /api/projects/contract-status/                   - Lista status de contrato
POST   /api/projects/contract-status/                   - Criar novo status
GET    /api/projects/contract-status/{id}/              - Detalhes do status
PATCH  /api/projects/contract-status/{id}/              - Atualizar status
DELETE /api/projects/contract-status/{id}/              - Remover status

GET    /api/projects/payment-methods/                   - Lista métodos de pagamento
POST   /api/projects/payment-methods/                   - Criar novo método
GET    /api/projects/payment-methods/{id}/              - Detalhes do método
PATCH  /api/projects/payment-methods/{id}/              - Atualizar método
DELETE /api/projects/payment-methods/{id}/              - Remover método

GET    /api/projects/owner-types/                       - Lista tipos de proprietário
POST   /api/projects/owner-types/                       - Criar novo tipo
GET    /api/projects/owner-types/{id}/                  - Detalhes do tipo
PATCH  /api/projects/owner-types/{id}/                  - Atualizar tipo
DELETE /api/projects/owner-types/{id}/                  - Remover tipo

## CONTRACT MANAGEMENT ENDPOINTS (NOVOS)
GET    /api/projects/contract-owners/                   - Lista proprietários com filtros
POST   /api/projects/contract-owners/                   - Criar novo proprietário
GET    /api/projects/contract-owners/{id}/              - Detalhes de proprietário
PATCH  /api/projects/contract-owners/{id}/              - Atualizar proprietário
DELETE /api/projects/contract-owners/{id}/              - Remover proprietário
GET    /api/projects/contract-owners/by-contract/{contract_id}/ - Por contrato
GET    /api/projects/contract-owners/by-client/{client_id}/     - Por cliente
GET    /api/projects/contract-owners/stats/             - Estatísticas

GET    /api/projects/contract-projects/                 - Lista projetos de contratos
POST   /api/projects/contract-projects/                 - Vincular projeto a contrato
GET    /api/projects/contract-projects/{id}/            - Detalhes da vinculação
PATCH  /api/projects/contract-projects/{id}/            - Atualizar vinculação
DELETE /api/projects/contract-projects/{id}/            - Remover vinculação
GET    /api/projects/contract-projects/by-contract/{contract_id}/ - Por contrato
GET    /api/projects/contract-projects/by-project/{project_id}/   - Por projeto
GET    /api/projects/contract-projects/stats/           - Estatísticas

## TASK RESOURCES ENDPOINTS (NOVOS)
GET    /api/projects/task-resources/                    - Lista recursos com filtros
POST   /api/projects/task-resources/                    - Criar novo recurso
GET    /api/projects/task-resources/{id}/               - Detalhes de recurso
PATCH  /api/projects/task-resources/{id}/               - Atualizar recurso
DELETE /api/projects/task-resources/{id}/               - Remover recurso
GET    /api/projects/task-resources/by-task/{task_id}/  - Por tarefa
GET    /api/projects/task-resources/stats/              - Estatísticas




## FILTROS DISPONÍVEIS (?filter=value)
Incorporations:
- incorporation_type=1                                  - Por tipo específico
- incorporation_status=PLANNING                         - Por status específico
- county=1                                              - Por county específico
- is_active=true                                        - Apenas ativos
- created_at__date=2025-01-15                           - Por data específica
- created_at__date__gte=2025-01-01                      - Data mínima
- created_at__date__lte=2025-01-31                      - Data máxima
- launch_date__gte=2025-01-01                           - Data de lançamento mínima

Contracts:
- status_contract=ACTIVE                                - Por status específico
- incorporation=1                                        - Por incorporação específica
- lead=1                                                - Por lead específico
- payment_method=1                                       - Por método de pagamento
- management_company=L. Lira                            - Por empresa de gestão
- sign_date__gte=2025-01-01                             - Data de assinatura mínima
- contract_value__gte=100000                            - Valor mínimo

Projects:
- incorporation=1                                        - Por incorporação específica
- model_project=1                                        - Por modelo de projeto
- status_project=IN_PROGRESS                             - Por status específico
- production_cell=1                                      - Por célula de produção
- completion_percentage__gte=50                          - Percentual mínimo de conclusão
- expected_delivery_date__gte=2025-01-01                 - Data de entrega mínima
- sale_value__gte=100000                                 - Valor de venda mínimo

Phases:
- project=1                                              - Por projeto específico
- phase_status=IN_PROGRESS                               - Por status específico
- priority=HIGH                                          - Por prioridade
- requires_inspection=true                               - Apenas que requerem inspeção
- technical_responsible=1                                - Por responsável técnico
- completion_percentage__gte=50                          - Percentual mínimo de conclusão

Tasks:
- phase_project=1                                        - Por fase específica
- task_status=IN_PROGRESS                                - Por status específico
- priority=HIGH                                          - Por prioridade
- assigned_to=1                                          - Por responsável
- requires_approval=true                                 - Apenas que requerem aprovação
- completion_percentage__gte=50                          - Percentual mínimo de conclusão

### Model Projects:
- project_type=1                                         - Por tipo de projeto específico
- county=1                                               - Por county específico
- is_active=true                                         - Apenas ativos
- builders_fee__gte=10000                                - Taxa mínima do construtor
- custo_base_estimado__gte=50000                         - Custo base mínimo

### Model Phases:
- project_model=1                                        - Por modelo de projeto específico
- execution_order=1                                      - Por ordem de execução
- is_mandatory=true                                      - Apenas obrigatórias
- requires_inspection=true                               - Apenas que requerem inspeção

### Model Tasks:
- model_phase=1                                          - Por fase de modelo específica
- task_type=PREPARATION                                  - Por tipo de tarefa
- requires_specialization=true                           - Apenas que requerem especialização
- skill_category=SPECIALIZED                             - Por categoria de habilidade

### Cost Groups (NOVOS):
- is_active=true                                         - Apenas ativos
- created_at__date=2025-01-15                           - Por data específica

### Cost SubGroups (NOVOS):
- cost_group=1                                           - Por grupo de custo específico
- value_stimated__gte=1000                              - Valor estimado mínimo
- is_active=true                                         - Apenas ativos

### Production Cells (NOVOS):
- is_active=true                                         - Apenas ativas
- created_at__date=2025-01-15                           - Por data específica


## BUSCA (?search=term)
search=Condomínio                                       - Busca em nome, descrição, etc.

## ORDENAÇÃO (?ordering=field)
ordering=created_at                                     - Mais antigos primeiro
ordering=-created_at                                    - Mais recentes primeiro
ordering=name                                           - Ordem alfabética
ordering=completion_percentage                          - Menor percentual primeiro
ordering=-completion_percentage                         - Maior percentual primeiro
"""
