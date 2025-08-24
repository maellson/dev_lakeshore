# Imports dos models principais

from .incorporation import Incorporation
from ...contracts.models.contract import Contract
from ...contracts.models.contract_owner import ContractOwner
from .project import Project
from .contact import Contact
from .model_project import ModelProject
from .contract_project import ContractProject
from .cost_group import CostGroup
from .cost_subgroup import CostSubGroup
from .model_phase import ModelPhase
from .model_task import ModelTask
from .phase_project import PhaseProject
from .task_project import TaskProject
from .task_resource import TaskResource
from .task_specification import TaskSpecification
from .projects_360 import Projects360


# Lista de todos os models para facilitar importações
__all__ = [
    # Models principais

    'Incorporation',
    'Contract',
    'ContractOwner',
    'Project',
    'Contact',
    'ModelProject',
    'ContractProject',
    'CostGroup',
    'CostSubGroup'

    # Models de processo (comentados até serem criados)
    'ModelPhase',
    'ModelTask',
    'PhaseProject',
    'TaskProject',
    'Projects360',



    # Models de recursos (comentados até serem melhorados)
    'TaskResource',
    'TaskSpecification'
]
