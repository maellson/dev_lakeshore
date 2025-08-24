# integrations/management/commands/sync_all_details.py
from django.core.management.base import BaseCommand
from integrations.sync_service import BrokermintSyncService
from integrations.models import BrokermintTransaction
import time


class Command(BaseCommand):
    help = 'Sincroniza detalhes de TODAS as transações sem dados completos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Quantas transações processar por vez (padrão: 50)'
        )
        parser.add_argument(
            '--max-total',
            type=int,
            default=None,
            help='Máximo total para processar (padrão: todas)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay em segundos entre requisições (padrão: 0.5s)'
        )

    def handle(self, *args, **options):
        service = BrokermintSyncService()

        # Buscar transações sem detalhes
        transactions_without_details = BrokermintTransaction.objects.filter(
            has_detailed_data=False
        )

        total_pending = transactions_without_details.count()

        if options['max_total']:
            transactions_without_details = transactions_without_details[:options['max_total']]
            total_to_process = min(total_pending, options['max_total'])
        else:
            total_to_process = total_pending

        self.stdout.write(
            self.style.SUCCESS(
                f'🚀 Sincronizando detalhes de {total_to_process} transações...')
        )

        if total_to_process == 0:
            self.stdout.write('✅ Todas as transações já têm detalhes!')
            return

        batch_size = options['batch_size']
        processed = 0
        errors = 0

        start_time = time.time()

        # Processar em lotes
        for i in range(0, total_to_process, batch_size):
            batch = transactions_without_details[i:i + batch_size]

            self.stdout.write(f'\n📦 Processando lote {i//batch_size + 1}...')
            delay = options['delay']

            for transaction in batch:
                try:
                    time.sleep(delay)  # Delay entre requisições
                    # Buscar detalhes individuais
                    details = service.client.get_transaction_details(
                        transaction.brokermint_id)

                    if details and isinstance(details, dict) and details.get('id'):
                        # Atualizar com dados completos
                        transaction.county = details.get('County', '')
                        transaction.legal_description = details.get(
                            'Legal description', '')
                        transaction.parcel_id = details.get('Parcel ID', '')
                        transaction.home_model = details.get('Home Model', '')
                        transaction.bedrooms = str(details.get('Bedrooms', ''))
                        transaction.full_baths = str(
                            details.get('Full baths', ''))
                        transaction.half_baths = str(
                            details.get('Half baths', ''))
                        transaction.building_sqft = str(
                            details.get('Building SQFT', ''))
                        transaction.soft_costs = str(
                            details.get('Soft Costs', ''))
                        transaction.hard_costs = str(
                            details.get('Hard Costs', ''))
                        transaction.estimated_construction_cost = str(
                            details.get('Estimated Construction Cost', ''))
                        transaction.builder_fee = str(
                            details.get('Builder Fee', ''))
                        transaction.draw_1 = str(details.get('Draw 1', ''))
                        transaction.draw_2 = str(details.get('Draw 2', ''))
                        transaction.draw_3 = str(details.get('Draw 3', ''))
                        transaction.draw_4 = str(details.get('Draw 4', ''))
                        transaction.draw_5 = str(details.get('Draw 5', ''))
                        transaction.lot = str(details.get('Lot', ''))
                        transaction.block = str(details.get('Block', ''))
                        transaction.unit = str(details.get('Unit', ''))
                        transaction.sec = str(details.get('SEC', ''))
                        transaction.twp = str(details.get('Twp', ''))
                        transaction.rge = str(details.get('Rge', ''))
                        transaction.subdivision = details.get(
                            'Subdivision', '')
                        transaction.acceptance_date = details.get(
                            'acceptance_date')
                        transaction.expiration_date = details.get(
                            'expiration_date')
                        transaction.closing_date = details.get('closing_date')
                        transaction.listing_date = details.get('listing_date')
                        transaction.buyer_agreement_date = details.get(
                            'buyer_agreement_date')
                        transaction.buyer_expiration_date = details.get(
                            'buyer_expiration_date')
                        transaction.custom_id = details.get('custom_id', '')
                        transaction.transaction_type = details.get(
                            'transaction_type', '')
                        transaction.external_id = details.get(
                            'external_id', '')
                        transaction.total_gross_commission = details.get(
                            'total_gross_commission', 0)
                        transaction.sales_volume = details.get(
                            'sales_volume', 0)
                        transaction.has_detailed_data = True
                        transaction.save()

                        processed += 1

                        if processed % 10 == 0:
                            self.stdout.write(
                                f'   ✅ {processed}/{total_to_process} processadas...')
                    else:
                        self.stdout.write(
                            f'   ❌ Detalhes não encontrados para a transação {transaction.brokermint_id}')

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        f'   ❌ Erro na transação {transaction.brokermint_id}: {str(e)}')
                    # Se muitos erros seguidos, aumentar delay
                    if errors > 5:
                        self.stdout.write(
                            '   ⏸️  Muitos erros, pausando 30s...')
                        time.sleep(30)

        end_time = time.time()

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ SINCRONIZAÇÃO CONCLUÍDA em {end_time - start_time:.2f}s')
        )
        self.stdout.write(f'   📊 Processadas: {processed}')
        self.stdout.write(f'   ❌ Erros: {errors}')
        self.stdout.write(
            f'   ⚡ Taxa: {processed/(end_time - start_time):.1f} transações/segundo')

        # Verificar resultado final
        final_count = BrokermintTransaction.objects.filter(
            has_detailed_data=True).count()
        total_count = BrokermintTransaction.objects.count()

        self.stdout.write(
            f'\n📋 RESULTADO FINAL: {final_count}/{total_count} transações com detalhes')
