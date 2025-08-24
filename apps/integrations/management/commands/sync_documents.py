# integrations/management/commands/sync_documents.py
from django.core.management.base import BaseCommand
from integrations.sync_service import BrokermintSyncService
from integrations.models import BrokermintActivity, BrokermintDocument
import time

class Command(BaseCommand):
    help = 'Sincroniza documentos das atividades de assinatura'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay entre requisições em segundos'
        )
    
    def handle(self, *args, **options):
        service = BrokermintSyncService()
        
        # Buscar atividades que ainda não têm documentos sincronizados
        activities_without_docs = BrokermintActivity.objects.exclude(
            document_id__in=BrokermintDocument.objects.values_list('brokermint_id', flat=True)
        )
        
        total_activities = activities_without_docs.count()
        
        if total_activities == 0:
            self.stdout.write('✅ Todos os documentos já foram sincronizados!')
            return
        
        self.stdout.write(f'📄 Sincronizando documentos de {total_activities} atividades...')
        
        processed = 0
        errors = 0
        new_documents = 0
        
        for activity in activities_without_docs:
            try:
                self.stdout.write(
                    f'🔍 Documento {activity.document_id} da transação {activity.bm_transaction_id}...', 
                    ending=''
                )
                
                # Delay para evitar rate limit
                time.sleep(options['delay'])
                
                # Buscar detalhes do documento
                doc_data = service.client.get_document_details(
                    activity.bm_transaction_id,
                    activity.document_id
                )
                
                if doc_data and isinstance(doc_data, dict) and doc_data.get('id'):
                    # Salvar documento
                    document, created = BrokermintDocument.objects.update_or_create(
                        brokermint_id=doc_data['id'],
                        defaults={
                            'name': doc_data.get('name', ''),
                            'bm_transaction_id': doc_data.get('bm_transaction_id'),
                            'task_id': doc_data.get('task_id'),
                            'pages': doc_data.get('pages', 0),
                            'content_type': doc_data.get('content_type', ''),
                            'url': doc_data.get('url', ''),
                        }
                    )
                    
                    if created:
                        new_documents += 1
                        self.stdout.write(f' ✅ {doc_data.get("name", "N/A")} ({doc_data.get("pages", 0)} páginas)')
                        
                        # Destacar se é contrato
                        if any(word in doc_data.get('name', '').lower() for word in ['contract', 'app', 'agreement']):
                            self.stdout.write(f'   🎯 POSSÍVEL CONTRATO: {doc_data.get("name")}')
                    else:
                        self.stdout.write(' ↩️  Já existia')
                        
                    processed += 1
                else:
                    self.stdout.write(' ⚠️  Resposta vazia')
                    
            except Exception as e:
                errors += 1
                self.stdout.write(f' ❌ Erro: {str(e)}')
                
                # Pausa em caso de muitos erros
                if errors > 5 and errors % 5 == 0:
                    self.stdout.write('   ⏸️  Muitos erros, pausando 30s...')
                    time.sleep(30)
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'✅ DOCUMENTOS SINCRONIZADOS!')
        self.stdout.write(f'   📊 Processados: {processed}')
        self.stdout.write(f'   🆕 Novos: {new_documents}')
        self.stdout.write(f'   ❌ Erros: {errors}')
        
        # Status final
        total_docs = BrokermintDocument.objects.count()
        self.stdout.write(f'   💾 Total no banco: {total_docs}')