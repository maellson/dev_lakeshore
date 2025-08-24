# integrations/management/commands/sync_activities.py
from django.core.management.base import BaseCommand
from integrations.sync_service import BrokermintSyncService
from integrations.models import BrokermintTransaction, BrokermintActivity
import time

class Command(BaseCommand):
    help = 'Sincroniza atividades de assinatura específicas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--transaction-ids',
            nargs='+',
            type=int,
            help='IDs específicos para verificar atividades'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Quantas transações verificar por vez'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Verificar TODAS as transações (pode demorar)'
        )
    
    def handle(self, *args, **options):
        service = BrokermintSyncService()
        
        if options['transaction_ids']:
            # IDs específicos fornecidos
            transaction_ids = options['transaction_ids']
            self.stdout.write(f'🎯 Verificando atividades de {len(transaction_ids)} transações específicas...')
            
        elif options['all']:
            # TODAS as transações
            transaction_ids = list(
                BrokermintTransaction.objects.values_list('brokermint_id', flat=True)
            )
            self.stdout.write(f'🌐 Verificando atividades de TODAS as {len(transaction_ids)} transações...')
            
        else:
            # Apenas transações sem atividades verificadas
            transaction_ids = list(
                BrokermintTransaction.objects.filter(
                    last_activity_check__isnull=True
                ).values_list('brokermint_id', flat=True)[:100]
            )
            self.stdout.write(f'📋 Verificando atividades de {len(transaction_ids)} transações não verificadas...')
        
        if not transaction_ids:
            self.stdout.write('✅ Nenhuma transação para verificar!')
            return
        
        # Processar em lotes para evitar timeout da API
        batch_size = options['batch_size']
        total_activities = 0
        total_signed_contracts = 0
        
        for i in range(0, len(transaction_ids), batch_size):
            batch = transaction_ids[i:i + batch_size]
            
            self.stdout.write(f'\n📦 Verificando lote {i//batch_size + 1} ({len(batch)} transações)...')
            
            try:
                # REQUISIÇÃO PARA API DE ATIVIDADES
                activities_data = service.client.get_signature_activities(batch)
                
                self.stdout.write(f'   📨 API retornou {len(activities_data)} atividades')
                
                for activity_data in activities_data:
                    # Salvar atividade
                    activity, created = BrokermintActivity.objects.update_or_create(
                        brokermint_id=activity_data['id'],
                        defaults={
                            'content': activity_data.get('content', ''),
                            'bm_transaction_id': activity_data.get('bm_transaction_id'),
                            'created_at_brokermint': activity_data.get('created_at'),
                            'originator_id': activity_data.get('originator_id'),
                            'document_id': activity_data.get('document_id'),
                            'event_label': activity_data.get('event_label', ''),
                            'signers': activity_data.get('metadata', {}).get('signers', []),
                        }
                    )
                    
                    if created:
                        total_activities += 1
                        total_signed_contracts += 1
                        
                        self.stdout.write(
                            f'   🎉 ASSINATURA ENCONTRADA: Transação {activity.bm_transaction_id}, '
                            f'Documento {activity.document_id}, '
                            f'Signatários: {", ".join(activity.signers)}'
                        )
                        
                        # Marcar transação como tendo assinatura
                        BrokermintTransaction.objects.filter(
                            brokermint_id=activity.bm_transaction_id
                        ).update(
                            has_signature_activity=True,
                            is_contract_signed=True
                        )
                
                # Marcar transações como verificadas
                from django.utils import timezone
                BrokermintTransaction.objects.filter(
                    brokermint_id__in=batch
                ).update(last_activity_check=timezone.now())
                
                # Delay entre lotes
                if i + batch_size < len(transaction_ids):
                    time.sleep(1)
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Erro no lote: {str(e)}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'✅ ATIVIDADES SINCRONIZADAS!')
        self.stdout.write(f'   📊 Total encontradas: {total_activities}')
        self.stdout.write(f'   🎉 Contratos assinados: {total_signed_contracts}')
        
        # Status final
        total_activities_db = BrokermintActivity.objects.count()
        self.stdout.write(f'   💾 Total no banco: {total_activities_db}')