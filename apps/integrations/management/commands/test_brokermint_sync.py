# integrations/management/commands/test_brokermint_sync.py - VERSÃO ATUALIZADA
from django.core.management.base import BaseCommand
from integrations.sync_service import BrokermintSyncService
from integrations.models import BrokermintTransaction, BrokermintActivity, BrokermintDocument
import time


class Command(BaseCommand):
    help = 'Testa sincronização otimizada do Brokermint'

    def add_arguments(self, parser):
        parser.add_argument(
            '--step',
            type=str,
            choices=['minimal', 'signatures',
                     'details', 'all'],  # ← NOVOS STEPS
            default='all',
            help='Qual etapa executar'
        )
        parser.add_argument(
            '--transaction-id',
            type=int,
            help='ID específico para testar detalhes'
        )

    def handle(self, *args, **options):
        service = BrokermintSyncService()

        self.stdout.write(
            self.style.SUCCESS('🚀 Testando sincronização OTIMIZADA...')
        )

        if options['step'] in ['minimal', 'all']:
            self.test_minimal_sync(service)

        if options['step'] in ['signatures', 'all']:
            self.test_signatures_sync(service)

        if options['step'] in ['details', 'all']:
            self.test_details_on_demand(service, options.get('transaction_id'))

        self.show_summary()

    def test_minimal_sync(self, service):
        self.stdout.write('\n📋 TESTE: Sincronização mínima de transações...')

        start_time = time.time()
        result = service.sync_minimal_transactions()  # ← NOVO MÉTODO
        end_time = time.time()

        self.stdout.write(
            f'✅ Sync mínima em {end_time - start_time:.2f}s'
        )
        self.stdout.write(
            f'   📊 {len(result)} transações novas identificadas'
        )

    def test_signatures_sync(self, service):
        self.stdout.write('\n🎯 TESTE: Verificação de assinaturas...')

        start_time = time.time()
        result = service.sync_only_signature_activities(
            hours_back=24)  # ← NOVO MÉTODO
        end_time = time.time()

        self.stdout.write(
            f'✅ Assinaturas verificadas em {end_time - start_time:.2f}s'
        )
        self.stdout.write(
            f'   📊 {len(result["new_activities"])} atividades, {len(result["signed_contracts"])} contratos assinados'
        )

        if result["signed_contracts"]:
            self.stdout.write(
                self.style.WARNING(
                    f'🎉 CONTRATOS ASSINADOS: {result["signed_contracts"]}')
            )

    def test_details_on_demand(self, service, transaction_id=None):
        self.stdout.write('\n🔍 TESTE: Detalhes sob demanda...')

        if not transaction_id:
            # Pegar primeira transação sem detalhes
            transaction = BrokermintTransaction.objects.filter(
                has_detailed_data=False
            ).first()

            if transaction:
                transaction_id = transaction.brokermint_id
            else:
                self.stdout.write('   ℹ️  Todas as transações já têm detalhes')
                return

        start_time = time.time()
        result = service.get_transaction_details_on_demand(
            transaction_id)  # ← NOVO MÉTODO
        end_time = time.time()

        if result:
            self.stdout.write(
                f'✅ Detalhes carregados em {end_time - start_time:.2f}s'
            )
            self.stdout.write(
                f'   📊 Transação {transaction_id}: Parcel ID = {result.parcel_id or "N/A"}'
            )
        else:
            self.stdout.write(f'❌ Erro ao carregar transação {transaction_id}')

    def show_summary(self):
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RESUMO FINAL:'))

        # Contar registros
        transactions_count = BrokermintTransaction.objects.count()
        detailed_count = BrokermintTransaction.objects.filter(
            has_detailed_data=True).count()
        activities_count = BrokermintActivity.objects.count()
        documents_count = BrokermintDocument.objects.count()

        self.stdout.write(f'   🏢 Transações: {transactions_count} total')
        self.stdout.write(
            f'   📋 Com detalhes: {detailed_count}/{transactions_count}')
        self.stdout.write(f'   📝 Atividades: {activities_count}')
        self.stdout.write(f'   📄 Documentos: {documents_count}')

        # Mostrar algumas transações com Parcel ID
        transactions_with_parcel = BrokermintTransaction.objects.exclude(
            parcel_id=''
        ).values_list('brokermint_id', 'parcel_id', 'address')[:5]

        if transactions_with_parcel:
            self.stdout.write('\n🎯 Transações com Parcel ID (primeiras 5):')
            for tx_id, parcel_id, address in transactions_with_parcel:
                self.stdout.write(f'   • {tx_id}: {parcel_id} - {address}')

        self.stdout.write(
            '\n✅ Teste concluído! Verifique o admin para mais detalhes.')
