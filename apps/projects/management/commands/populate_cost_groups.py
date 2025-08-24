# apps/projects/management/commands/populate_cost_groups.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from projects.models import CostGroup, CostSubGroup
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula grupos de custo e subgrupos com dados padrão da construção civil'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️  Limpando dados existentes...')
            CostSubGroup.objects.all().delete()
            CostGroup.objects.all().delete()
            self.stdout.write(self.style.WARNING('Dados existentes removidos.'))

        # Dados organizados hierarquicamente
        cost_data = {
            "01 - CONTRACT": {
                "description": "Taxas contratuais e garantias básicas",
                "subgroups": {
                    "01.00": {"name": "Builder's Fee", "value": "25000.00"},
                    "01.01": {"name": "Warranty Fee", "value": "1000.00"},
                }
            },
            "02 - PERMIT": {
                "description": "Licenças, projetos e documentação legal",
                "subgroups": {
                    "02.00": {"name": "Surveying", "value": "1540.00"},
                    "02.01": {"name": "Architectural Plans", "value": "750.00"},
                    "02.02": {"name": "Truss Engineering", "value": "250.00"},
                    "02.03": {"name": "Electric Connection", "value": "650.00"},
                    "02.04": {"name": "Sewer Connection", "value": "10500.00"},
                    "02.05": {"name": "Water Connection", "value": "0.00"},
                    "02.06": {"name": "Building Fees", "value": "13000.00"},
                    "02.08": {"name": "Energy Calculation", "value": "200.00"},
                    "02.09": {"name": "NOC", "value": "20.00"},
                    "02.10": {"name": "Insurances", "value": "550.00"},
                }
            },
            "03 - UTILITIES": {
                "description": "Serviços públicos e utilitários",
                "subgroups": {
                    "03.00": {"name": "Electric Usage", "value": "500.00"},
                    "03.01": {"name": "Water Usage", "value": "1000.00"},
                }
            },
            "04 - LAND PREPARATION": {
                "description": "Preparação do terreno e infraestrutura inicial",
                "subgroups": {
                    "04.00": {"name": "Lot Clearing", "value": "3500.00"},
                    "04.01": {"name": "Pad", "value": "500.00"},
                    "04.02": {"name": "Loads", "value": "4000.00"},
                    "04.03": {"name": "Compact Test", "value": "155.00"},
                    "04.04": {"name": "Portable", "value": "750.00"},
                    "04.05": {"name": "Dumpsters", "value": "2000.00"},
                    "04.06": {"name": "Site Preparation", "value": "400.00"},
                }
            },
            "05 - FOUNDATION": {
                "description": "Fundação e estrutura base",
                "subgroups": {
                    "05.00": {"name": "Foundation Material", "value": "820.00"},
                    "05.01": {"name": "Slab Concrete", "value": "9200.00"},
                    "05.02": {"name": "Slab Labor", "value": "2570.00"},
                    "05.03": {"name": "Slab Grading", "value": "330.00"},
                }
            },
            "06 - PLUMBING": {
                "description": "Sistema hidráulico completo",
                "subgroups": {
                    "06.00": {"name": "Underground Plumbing", "value": "3400.00"},
                    "06.01": {"name": "Rough Plumbing", "value": "3400.00"},
                    "06.02": {"name": "Plumbing Trim", "value": "1700.00"},
                    "06.03": {"name": "Plumbing Materials", "value": "450.00"},
                }
            },
            "07 - ELECTRIC": {
                "description": "Sistema elétrico completo",
                "subgroups": {
                    "07.00": {"name": "Underground Electric", "value": "2920.00"},
                    "07.01": {"name": "Rough Electric", "value": "2920.00"},
                    "07.02": {"name": "Electric Trim", "value": "1460.00"},
                    "07.03": {"name": "Fixtures", "value": "450.00"},
                }
            },
            "08 - MASONRY ASSEMBLY": {
                "description": "Alvenaria e estruturas de blocos",
                "subgroups": {
                    "08.00": {"name": "Blocks", "value": "5200.00"},
                    "08.01": {"name": "Precast", "value": "2045.00"},
                    "08.02": {"name": "Masonry Assembly Labor", "value": "3430.00"},
                    "08.03": {"name": "Lintel Concrete", "value": "1825.00"},
                    "08.04": {"name": "Lintel Labor and Pump", "value": "450.00"},
                }
            },
            "09 - ROOFING AND FRAMING": {
                "description": "Estrutura do telhado e cobertura",
                "subgroups": {
                    "09.00": {"name": "Trusses", "value": "4850.00"},
                    "09.01": {"name": "Lumber", "value": "5300.00"},
                    "09.02": {"name": "Hardware", "value": "600.00"},
                    "09.03": {"name": "Roofing and Framing Labor", "value": "5135.00"},
                    "09.04": {"name": "Bora Care/Termite Treatment", "value": "260.00"},
                    "09.05": {"name": "Dry in", "value": "5040.00"},
                    "09.06": {"name": "Shingles", "value": "2160.00"},
                }
            },
            "10 - WINDOWS": {
                "description": "Janelas e aberturas",
                "subgroups": {
                    "10.00": {"name": "Windows Material", "value": "2500.00"},
                    "10.01": {"name": "Windows and Exterior Doors installation", "value": "1500.00"},
                    "10.02": {"name": "Shutters Material", "value": "125.00"},
                    "10.03": {"name": "Shutters Labor", "value": "25.00"},
                }
            },
            "11 - DOORS": {
                "description": "Portas e acabamentos",
                "subgroups": {
                    "11.00": {"name": "Front Door Material", "value": "915.00"},
                    "11.01": {"name": "Front Door Labor", "value": "150.00"},
                    "11.02": {"name": "Interior Doors", "value": "2100.00"},
                    "11.03": {"name": "Casing, Baseboards and Trim Set Material", "value": "980.00"},
                    "11.04": {"name": "Interior Doors, Casings and Baseboards installation", "value": "1050.00"},
                    "11.05": {"name": "Garage Door installation", "value": "1800.00"},
                    "11.06": {"name": "Door Knob and Door Stop", "value": "450.00"},
                    "11.07": {"name": "Door Knob and Door Stop installation", "value": "50.00"},
                }
            },
            "12 - MECHANICAL": {
                "description": "Sistema mecânico (HVAC)",
                "subgroups": {
                    "12.00": {"name": "Rough Mechanical", "value": "5680.00"},
                    "12.01": {"name": "Mechanical Trim", "value": "1420.00"},
                    "12.02": {"name": "Mechanical Variance", "value": "0.00"},
                }
            },
            "13 - FINISHING": {
                "description": "Acabamentos internos e externos",
                "subgroups": {
                    "13.00": {"name": "Stucco", "value": "3500.00"},
                    "13.01": {"name": "Drywall", "value": "7900.00"},
                    "13.02": {"name": "Insulation", "value": "1300.00"},
                    "13.03": {"name": "Painting", "value": "4000.00"},
                    "13.04": {"name": "Soffit", "value": "1150.00"},
                    "13.05": {"name": "Tile Material", "value": "810.00"},
                    "13.06": {"name": "Vinyl Material", "value": "3190.00"},
                    "13.07": {"name": "Tile Labor", "value": "1100.00"},
                    "13.08": {"name": "Vinyl Labor", "value": "1305.00"},
                    "13.09": {"name": "Cabinets and Countertop", "value": "6900.00"},
                    "13.10": {"name": "Blower Door Test", "value": "200.00"},
                    "13.11": {"name": "Shower Glass Door installation", "value": "800.00"},
                    "13.12": {"name": "Appliances", "value": "2650.00"},
                    "13.13": {"name": "Appliances installation", "value": "300.00"},
                }
            },
            "14 - EXTERIOR FINISHING": {
                "description": "Acabamentos externos e paisagismo",
                "subgroups": {
                    "14.00": {"name": "Driveway", "value": "5100.00"},
                    "14.02": {"name": "Final Grading", "value": "500.00"},
                    "14.03": {"name": "Sod installation", "value": "3500.00"},
                    "14.04.00": {"name": "Hose", "value": "255.00"},
                    "14.04.01": {"name": "Timer", "value": "140.00"},
                    "14.04.02": {"name": "Plants", "value": "250.00"},
                    "14.04.03": {"name": "Sprinklers", "value": "105.00"},
                    "14.04.04": {"name": "Garden Faucet", "value": "10.00"},
                    "14.05": {"name": "Driveway Cut", "value": "350.00"},
                    "14.06": {"name": "Chipping", "value": "50.00"},
                    "14.07": {"name": "Landscaping Install", "value": "220.00"},
                }
            },
            "15 - SPECIALTIES": {
                "description": "Itens especiais e acessórios",
                "subgroups": {
                    "15.00": {"name": "Shelves", "value": "350.00"},
                    "15.01": {"name": "Shelves, Mirrors and Bath Kit installation", "value": "350.00"},
                    "15.02": {"name": "Mirrors", "value": "200.00"},
                    "15.03": {"name": "Bath Kit", "value": "75.00"},
                    "15.04": {"name": "Electronic Lock", "value": "85.00"},
                    "15.05": {"name": "House Numbers", "value": "50.00"},
                    "15.06": {"name": "Trim, Door Lock installation", "value": "50.00"},
                    "15.07": {"name": "House Numbers installation", "value": "30.00"},
                }
            },
            "16 - FINAL CLEAN": {
                "description": "Limpeza final e entrega",
                "subgroups": {
                    "16.00": {"name": "Final Clean", "value": "300.00"},
                }
            },
            "17 - VARIANCES": {
                "description": "Variações e ajustes",
                "subgroups": {
                    "17.00": {"name": "Variances", "value": "0.00"},
                }
            },
            "18 - LOT VARIANCES": {
                "description": "Variações específicas do lote",
                "subgroups": {
                    # Alguns itens já estão em outras categorias, mantendo apenas os específicos
                }
            },
        }

        # Obter usuário para created_by (usa o primeiro superuser)
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()
        except User.DoesNotExist:
            admin_user = None

        self.stdout.write('🚀 Iniciando população de grupos de custo...')
        
        created_groups = 0
        created_subgroups = 0
        
        with transaction.atomic():
            for group_name, group_data in cost_data.items():
                # Criar ou obter CostGroup
                cost_group, group_created = CostGroup.objects.get_or_create(
                    name=group_name,
                    defaults={
                        'description': group_data['description'],
                        'created_by': admin_user,
                        'is_active': True
                    }
                )
                
                if group_created:
                    created_groups += 1
                    self.stdout.write(f'✅ Grupo criado: {group_name}')
                else:
                    self.stdout.write(f'ℹ️  Grupo já existe: {group_name}')
                
                # Criar subgrupos
                for subgroup_code, subgroup_data in group_data['subgroups'].items():
                    subgroup, subgroup_created = CostSubGroup.objects.get_or_create(
                        cost_group=cost_group,
                        name=f"{subgroup_code} - {subgroup_data['name']}",
                        defaults={
                            'description': f"Subgrupo {subgroup_code}: {subgroup_data['name']}",
                            'value_stimated': Decimal(subgroup_data['value']),
                            'created_by': admin_user,
                            'is_active': True
                        }
                    )
                    
                    if subgroup_created:
                        created_subgroups += 1
                        self.stdout.write(f'  ➕ Subgrupo criado: {subgroup_code} - {subgroup_data["name"]} (${subgroup_data["value"]})')
        
        # Resumo final
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 População concluída com sucesso!\n'
                f'📊 Grupos criados: {created_groups}\n'
                f'📋 Subgrupos criados: {created_subgroups}\n'
                f'💾 Total de grupos: {CostGroup.objects.count()}\n'
                f'💾 Total de subgrupos: {CostSubGroup.objects.count()}'
            )
        )