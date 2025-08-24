# integrations/management/commands/continue_sync.py
from django.core.management.base import BaseCommand
from integrations.sync_service import BrokermintSyncService
from integrations.models import BrokermintTransaction
import time

class Command(BaseCommand):
    help = 'Continua sincronização das transações restantes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay em segundos entre requisições (padrão: 1s)'
        )
        parser.add_argument(
            '--max-batch',
            type=int,
            default=100,
            help='Máximo por execução para evitar rate limit'
        )
    
    def handle(self, *args, **options):
        service = BrokermintSyncService()
        
        # Buscar apenas as que faltam
        remaining = BrokermintTransaction.objects.filter(
            has_detailed_data=False
        )[:options['max_batch']]
        
        if not remaining:
            self.stdout.write('✅ Todas as transações já têm detalhes!')
            return
        
        self.stdout.write(f'🔄 Continuando com {remaining.count()} transações restantes...')
        
        processed = 0
        errors = 0
        
        for transaction in remaining:
            try:
                self.stdout.write(f'🔍 Processando {transaction.brokermint_id}...', ending='')
                
                # DELAY MAIOR PARA EVITAR RATE LIMIT
                time.sleep(options['delay'])
                
                details = service.client.get_transaction_details(transaction.brokermint_id)
                
                if details and isinstance(details, dict) and details.get('id'):
                    # Atualizar dados (mesmo código anterior)
                    transaction.parcel_id = details.get('Parcel ID', '')
                    transaction.county = details.get('County', '')
                    # ... outros campos ...
                    transaction.has_detailed_data = True
                    transaction.save()
                    
                    processed += 1
                    self.stdout.write(f' ✅ Parcel: {transaction.parcel_id or "N/A"}')
                else:
                    self.stdout.write(' ⚠️  Resposta vazia')
                    
            except Exception as e:
                errors += 1
                self.stdout.write(f' ❌ Erro: {str(e)}')
                
                # Pausa maior em caso de erro
                if 'rate limit' in str(e).lower() or '429' in str(e):
                    self.stdout.write('   ⏸️  Rate limit detectado, pausando 60s...')
                    time.sleep(60)
        
        self.stdout.write(f'\n✅ Processadas: {processed}, Erros: {errors}')
        
        # Status final
        total_with_details = BrokermintTransaction.objects.filter(has_detailed_data=True).count()
        total = BrokermintTransaction.objects.count()
        self.stdout.write(f'📊 Total com detalhes: {total_with_details}/{total}')