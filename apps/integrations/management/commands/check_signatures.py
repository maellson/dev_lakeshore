# integrations/management/commands/check_signatures.py
from django.core.management.base import BaseCommand
from integrations.sync_service import BrokermintSyncService

class Command(BaseCommand):
    help = 'Verifica assinaturas de transações específicas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--transactions',
            nargs='+',
            type=int,
            help='IDs das transações para verificar'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Horas atrás para verificar (padrão: 24h)'
        )
    
    def handle(self, *args, **options):
        service = BrokermintSyncService()
        
        if options['transactions']:
            # Verificação específica
            self.stdout.write(f"🎯 Verificando transações: {options['transactions']}")
            result = service.sync_only_signature_activities(transaction_ids=options['transactions'])
        else:
            # Verificação geral
            self.stdout.write(f"🔍 Verificando últimas {options['hours']} horas...")
            result = service.sync_only_signature_activities(hours_back=options['hours'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ {len(result['new_activities'])} assinaturas, {len(result['signed_contracts'])} contratos assinados"
            )
        )