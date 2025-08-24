# apps/projects/management/commands/populate_model_m01_cic.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from projects.models import (
    ModelProject, ModelPhase, ModelTask, CostSubGroup
)
from projects.models.choice_types import ProjectType
from core.models import County
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula o modelo de projeto M01 - CIC com suas fases e tarefas'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('🏗️  Criando modelo M01 - CIC...\n')
            
            # Obter dependências necessárias
            admin_user = User.objects.filter(is_superuser=True).first()
            project_type = ProjectType.objects.get(code='SIMPLE_HOUSE')
            county = County.objects.get(id=52)  # Bradford, FL
            
            # Criar ModelProject
            model_project = self.create_model_project(project_type, county, admin_user)
            
            # Criar as 4 fases
            phase_1 = self.create_phase_1(model_project, admin_user)
            phase_2 = self.create_phase_2(model_project, admin_user)  
            phase_3 = self.create_phase_3(model_project, admin_user)
            phase_4 = self.create_phase_4(model_project, admin_user)
            
            # Configurar dependências entre fases
            self.setup_phase_dependencies(phase_1, phase_2, phase_3, phase_4)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Modelo M01 - CIC criado com sucesso!\n'
                    f'📊 4 fases criadas\n'
                    f'📋 {ModelTask.objects.filter(model_phase__project_model=model_project).count()} tarefas criadas\n'
                )
            )

    def create_model_project(self, project_type, county, admin_user):
        """Cria o ModelProject M01 - CIC"""
        model_project, created = ModelProject.objects.get_or_create(
            code='M01',
            defaults={
                'name': 'M01 - CIC',
                'project_type': project_type,
                'county': county,
                'builders_fee': Decimal('25000.00'),
                'area_construida_padrao': Decimal('150.00'),  # ~150m² típico
                'especificacoes_padrao': 'Casa individual padrão CIC - Construção em alvenaria com acabamento padrão',
                'custo_base_estimado': Decimal('120000.00'),  # Estimativa baseada nos cost groups
                'custo_por_m2': Decimal('800.00'),
                'duracao_construcao_dias': 120,  # ~4 meses
                'requisitos_especiais': 'Seguir padrões de construção do condado de Bradford, FL',
                'regulamentacoes_county': 'Building codes do condado Bradford - Florida Building Code aplicável',
                'versao': '1.0',
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(f'✅ ModelProject criado: {model_project.name}')
        else:
            self.stdout.write(f'ℹ️  ModelProject já existe: {model_project.name}')
            
        return model_project

    def create_phase_1(self, model_project, admin_user):
        """Cria Phase 1 com 29 tarefas"""
        phase = ModelPhase.objects.create(
            project_model=model_project,
            phase_name='Phase 1 - Site Preparation & Foundation',
            phase_code='PH01',
            phase_description='Preparação do terreno e execução da fundação',
            phase_objectives='Preparar o lote e executar fundação completa',
            execution_order=1,
            estimated_duration_days=30,
            is_mandatory=True,
            requires_inspection=True,
            initial_requirements='Lote limpo e documentação aprovada',
            completion_criteria='Fundação concluída e aprovada na inspeção',
            deliverables='Laje pronta para próxima fase',
            created_by=admin_user
        )
        
        # Tarefas da Phase 1
        tasks_phase_1 = [
            ('T001', 'Stake Lot', 'PREPARATION', 4),
            ('T002', 'Clear Lot', 'PREPARATION', 8),
            ('T003', 'Silt Fence', 'PREPARATION', 4),
            ('T004', 'Doc Box', 'ADMINISTRATIVE', 2),
            ('T005', 'Stake House', 'PREPARATION', 4),
            ('T006', 'Portable', 'PREPARATION', 2),
            ('T007', 'Loads', 'MATERIAL', 4),
            ('T008', 'Pad', 'PREPARATION', 8),
            ('T009', 'Hub and Tack', 'PREPARATION', 4),
            ('T010', 'Compact Test', 'INSPECTION', 2),
            ('T011', 'Form', 'PREPARATION', 8),
            ('T012', 'Underground Electrical', 'SUBCONTRACTED', 16),
            ('T013', 'Underground Plumbing', 'SUBCONTRACTED', 16),
            ('T014', 'UP Inspection', 'INSPECTION', 2),
            ('T015', 'Trusses Order', 'MATERIAL', 2),
            ('T016', 'Slab Prep', 'PREPARATION', 8),
            ('T017', 'Slab Inspection', 'INSPECTION', 2),
            ('T018', 'Foundation Materials', 'MATERIAL', 4),
            ('T019', 'Slab Pouring', 'INTERNAL_SERVICE', 12),
            ('T020', 'Trusses ETA', 'ADMINISTRATIVE', 1),
            ('T021', 'Blocks', 'MATERIAL', 4),
            ('T022', 'Precast', 'MATERIAL', 4),
            ('T023', 'Wood Dumpster', 'PREPARATION', 2),
            ('T024', 'Masonry Assembly', 'SUBCONTRACTED', 24),
            ('T025', 'Lumber', 'MATERIAL', 4),
            ('T026', 'Trusses', 'MATERIAL', 4),
            ('T027', 'Lintel Inspection', 'INSPECTION', 2),
            ('T028', 'Mark Straps', 'PREPARATION', 4),
            ('T029', 'Lintel Pouring', 'INTERNAL_SERVICE', 8),
        ]
        
        self.create_tasks_for_phase(phase, tasks_phase_1)
        self.stdout.write(f'✅ Phase 1 criada com {len(tasks_phase_1)} tarefas')
        return phase

    def create_phase_2(self, model_project, admin_user):
        """Cria Phase 2 com 30 tarefas"""
        phase = ModelPhase.objects.create(
            project_model=model_project,
            phase_name='Phase 2 - Framing & Systems',
            phase_code='PH02', 
            phase_description='Estrutura, cobertura e sistemas básicos',
            phase_objectives='Executar estrutura e instalar sistemas básicos',
            execution_order=2,
            estimated_duration_days=35,
            is_mandatory=True,
            requires_inspection=True,
            initial_requirements='Phase 1 concluída e aprovada',
            completion_criteria='Estrutura fechada e sistemas instalados',
            deliverables='Casa fechada com sistemas funcionais',
            created_by=admin_user
        )
        
        # Tarefas da Phase 2
        tasks_phase_2 = [
            ('T030', 'Framing and Roof Assembly', 'INTERNAL_SERVICE', 24),
            ('T031', 'Structural Frame Inspection', 'INSPECTION', 2),
            ('T032', 'Sub-siding Inspection', 'INSPECTION', 2),
            ('T033', 'Sheating Inspection', 'INSPECTION', 2),
            ('T034', 'Windows and Doors Material', 'MATERIAL', 4),
            ('T035', 'TUG Install', 'SUBCONTRACTED', 8),
            ('T036', 'Septic Install & Connection', 'SUBCONTRACTED', 16),
            ('T037', 'Dry in', 'INTERNAL_SERVICE', 16),
            ('T038', 'Rough Plumbing', 'SUBCONTRACTED', 16),
            ('T039', 'Termite Treatment', 'SUBCONTRACTED', 4),
            ('T040', 'Windows and Exit Doors', 'SUBCONTRACTED', 12),
            ('T041', 'TUG Inspection', 'INSPECTION', 2),
            ('T042', 'Rough AC', 'SUBCONTRACTED', 16),
            ('T043', 'Rough Electric', 'SUBCONTRACTED', 16),
            ('T044', 'DOH', 'ADMINISTRATIVE', 2),
            ('T045', 'Septic Cover', 'INTERNAL_SERVICE', 4),
            ('T046', 'Rough Ac Inspection', 'INSPECTION', 2),
            ('T047', 'Rough Electric Inspection', 'INSPECTION', 2),
            ('T048', 'Dry in Inspection', 'INSPECTION', 2),
            ('T049', 'Rough Plumbing Inspection', 'INSPECTION', 2),
            ('T050', 'Lath', 'SUBCONTRACTED', 8),
            ('T051', 'Framing Inspection', 'INSPECTION', 2),
            ('T052', 'Shingles and Roof Vents', 'SUBCONTRACTED', 12),
            ('T053', 'Insulation and Polyseal', 'SUBCONTRACTED', 8),
            ('T054', 'Lath Inspection', 'INSPECTION', 2),
            ('T055', 'Insulation Inspection', 'INSPECTION', 2),
            ('T056', 'Stucco', 'SUBCONTRACTED', 16),
            ('T057', 'Drywall and Texture', 'SUBCONTRACTED', 16),
        ]
        
        self.create_tasks_for_phase(phase, tasks_phase_2)
        self.stdout.write(f'✅ Phase 2 criada com {len(tasks_phase_2)} tarefas')
        return phase

    def create_phase_3(self, model_project, admin_user):
        """Cria Phase 3 com 47 tarefas"""
        phase = ModelPhase.objects.create(
            project_model=model_project,
            phase_name='Phase 3 - Finishing & Utilities',
            phase_code='PH03',
            phase_description='Acabamentos internos e externos, utilidades finais',
            phase_objectives='Finalizar acabamentos e conectar utilidades',
            execution_order=3,
            estimated_duration_days=45,
            is_mandatory=True,
            requires_inspection=True,
            initial_requirements='Phase 2 concluída e aprovada',
            completion_criteria='Casa finalizada e utilidades conectadas',
            deliverables='Casa pronta para habitação',
            created_by=admin_user
        )
        
        # Tarefas da Phase 3 (47 tarefas)
        tasks_phase_3 = [
            ('T058', 'Tile Material', 'MATERIAL', 4),
            ('T059', 'Interior Paint', 'SUBCONTRACTED', 16),
            ('T060', 'Exterior Paint', 'SUBCONTRACTED', 12),
            ('T061', 'Underground Electrical', 'SUBCONTRACTED', 8),
            ('T062', 'Tile', 'SUBCONTRACTED', 16),
            ('T063', 'Garage Door', 'SUBCONTRACTED', 8),
            ('T064', 'Soffit', 'SUBCONTRACTED', 8),
            ('T065', 'Vinyl', 'SUBCONTRACTED', 12),
            ('T066', 'Blown in Insulation', 'SUBCONTRACTED', 4),
            ('T067', 'Electronic Door Lock', 'SUBCONTRACTED', 2),
            ('T068', 'House Number', 'SUBCONTRACTED', 2),
            ('T069', 'Final Roof Inspection', 'INSPECTION', 2),
            ('T070', 'Trim Set Material', 'MATERIAL', 4),
            ('T071', 'Cabinets and Granite', 'SUBCONTRACTED', 16),
            ('T072', 'Trim Set', 'SUBCONTRACTED', 12),
            ('T073', 'Plumbing Trim', 'SUBCONTRACTED', 8),
            ('T074', 'Driveway Cut', 'SUBCONTRACTED', 4),
            ('T075', 'Electrical Meter', 'SUBCONTRACTED', 4),
            ('T076', 'Blower Door Test', 'INSPECTION', 2),
            ('T077', 'Final Utilities Inspection', 'INSPECTION', 2),
            ('T078', 'AC Trim', 'SUBCONTRACTED', 8),
            ('T079', 'Electric Trim', 'SUBCONTRACTED', 8),
            ('T080', 'Driveway Preparation', 'PREPARATION', 8),
            ('T081', 'Pre-Power Inspection', 'INSPECTION', 2),
            ('T082', 'Driveway Internal Inspection', 'INSPECTION', 2),
            ('T083', 'Turn On Ac and Vacuum', 'SUBCONTRACTED', 4),
            ('T084', 'Hot Check', 'INSPECTION', 2),
            ('T085', 'Driveway Pouring', 'SUBCONTRACTED', 8),
            ('T086', 'Shelves and Mirror', 'SUBCONTRACTED', 4),
            ('T087', 'Shutters and Brackets Install', 'SUBCONTRACTED', 4),
            ('T088', 'Final Plumbing Inspection', 'INSPECTION', 2),
            ('T089', 'Final AC Inspection', 'INSPECTION', 2),
            ('T090', 'Final Electric Inspection', 'INSPECTION', 2),
            ('T091', 'Final Grading / Site Drainage', 'SUBCONTRACTED', 8),
            ('T092', 'SOD', 'SUBCONTRACTED', 8),
            ('T093', 'Quality Assurance 1', 'QUALITY_CONTROL', 4),
            ('T094', 'Final Touches', 'INTERNAL_SERVICE', 8),
            ('T095', 'Final Driveway Inspection', 'INSPECTION', 2),
            ('T096', 'Quality Assurance 2', 'QUALITY_CONTROL', 4),
            ('T097', 'Final Paint', 'SUBCONTRACTED', 8),
            ('T098', 'Final Clean', 'CLEANUP', 4),
            ('T099', 'Appliances Install', 'SUBCONTRACTED', 8),
            ('T100', 'Building Final Inspection', 'INSPECTION', 4),
            ('T101', 'CO', 'ADMINISTRATIVE', 2),
            ('T102', 'Garden', 'SUBCONTRACTED', 8),
            ('T103', 'Shower Glass Door', 'SUBCONTRACTED', 4),
            ('T104', 'FCC', 'ADMINISTRATIVE', 2),
        ]
        
        self.create_tasks_for_phase(phase, tasks_phase_3)
        self.stdout.write(f'✅ Phase 3 criada com {len(tasks_phase_3)} tarefas')
        return phase

    def create_phase_4(self, model_project, admin_user):
        """Cria Phase 4 com 3 tarefas"""
        phase = ModelPhase.objects.create(
            project_model=model_project,
            phase_name='Phase 4 - Final Delivery',
            phase_code='PH04',
            phase_description='Limpeza final e entrega',
            phase_objectives='Finalizar projeto e entregar ao cliente',
            execution_order=4,
            estimated_duration_days=10,
            is_mandatory=True,
            requires_inspection=False,
            initial_requirements='Phase 3 concluída e CO emitido',
            completion_criteria='Cliente satisfeito e projeto entregue',
            deliverables='Casa entregue ao cliente',
            created_by=admin_user
        )
        
        # Tarefas da Phase 4
        tasks_phase_4 = [
            ('T105', 'Final Clean Touch up', 'CLEANUP', 4),
            ('T106', 'Internal Walkthrough', 'QUALITY_CONTROL', 2),
            ('T107', 'Walkthrough', 'ADMINISTRATIVE', 2),
        ]
        
        self.create_tasks_for_phase(phase, tasks_phase_4)
        self.stdout.write(f'✅ Phase 4 criada com {len(tasks_phase_4)} tarefas')
        return phase

    def create_tasks_for_phase(self, phase, tasks_data):
        """Cria tarefas para uma fase específica"""
        for order, (task_code, task_name, task_type, duration_hours) in enumerate(tasks_data, 1):
            
            # Associar cost_subgroup baseado no tipo de tarefa
            cost_subgroup = self.get_cost_subgroup_for_task(task_name)
            
            ModelTask.objects.create(
                model_phase=phase,
                task_name=task_name,
                task_code=task_code,
                task_type=task_type,
                detailed_description=f'Executar {task_name.lower()} conforme especificações do projeto',
                task_objective=f'Completar {task_name.lower()} dentro do prazo e qualidade esperados',
                estimated_duration_hours=Decimal(str(duration_hours)),
                execution_order=order,
                is_mandatory=True,
                allows_parallel=task_type != 'INSPECTION',
                requires_specialization=task_type in ['SUBCONTRACTED', 'INSPECTION'],
                skill_category='SPECIALIZED' if task_type == 'SUBCONTRACTED' else 'BASIC',
                required_people=2 if task_type == 'SUBCONTRACTED' else 1,
                cost_subgroup=cost_subgroup,
                estimated_labor_cost=Decimal(str(duration_hours * 50)),  # $50/hora estimado
                created_by=phase.created_by
            )

    def get_cost_subgroup_for_task(self, task_name):
        """Associa tarefa com subgrupo de custo apropriado"""
        task_name_lower = task_name.lower()
        
        # Mapeamento baseado em palavras-chave
        if any(word in task_name_lower for word in ['foundation', 'slab', 'concrete', 'pad']):
            return CostSubGroup.objects.filter(name__icontains='Foundation').first()
        elif any(word in task_name_lower for word in ['plumbing', 'septic']):
            return CostSubGroup.objects.filter(name__icontains='Plumbing').first()
        elif any(word in task_name_lower for word in ['electric', 'electrical']):
            return CostSubGroup.objects.filter(name__icontains='Electric').first()
        elif any(word in task_name_lower for word in ['masonry', 'blocks']):
            return CostSubGroup.objects.filter(name__icontains='Masonry').first()
        elif any(word in task_name_lower for word in ['roof', 'trusses', 'framing', 'lumber']):
            return CostSubGroup.objects.filter(name__icontains='Roofing').first()
        elif any(word in task_name_lower for word in ['windows', 'doors']):
            return CostSubGroup.objects.filter(name__icontains='Windows').first() or CostSubGroup.objects.filter(name__icontains='Doors').first()
        elif any(word in task_name_lower for word in ['paint', 'stucco', 'tile', 'drywall']):
            return CostSubGroup.objects.filter(name__icontains='Finishing').first()
        elif any(word in task_name_lower for word in ['driveway', 'grading', 'sod']):
            return CostSubGroup.objects.filter(name__icontains='Exterior').first()
        elif any(word in task_name_lower for word in ['clean']):
            return CostSubGroup.objects.filter(name__icontains='Final Clean').first()
        
        return None  # Sem associação específica

    def setup_phase_dependencies(self, phase_1, phase_2, phase_3, phase_4):
        """Configura dependências sequenciais entre fases"""
        phase_2.prerequisite_phases.add(phase_1)
        phase_3.prerequisite_phases.add(phase_2)
        phase_4.prerequisite_phases.add(phase_3)
        
        self.stdout.write('✅ Dependências entre fases configuradas')