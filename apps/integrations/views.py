# integrations/views.py - ÚNICO ARQUIVO DE VIEWS
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import BrokermintDocument
from .serializers import BrokermintDocumentSerializer, DocumentRefreshSerializer
from .sync_service import BrokermintSyncService


class BrokermintDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para documentos do Brokermint"""
    queryset = BrokermintDocument.objects.all()
    serializer_class = BrokermintDocumentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Refresh Document URL",
        operation_description="Atualiza URL do documento Brokermint",
        responses={200: DocumentRefreshSerializer()}
    )
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Atualiza URL do documento"""
        document = self.get_object()

        try:
            service = BrokermintSyncService()
            doc_data = service.client.get_document_details(
                document.bm_transaction_id,
                document.brokermint_id
            )

            if doc_data and doc_data.get('url'):
                document.url = doc_data['url']
                document.save()

                return Response({
                    'success': True,
                    'message': f'URL atualizada: {document.name}',
                    'document': self.get_serializer(document).data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Não foi possível obter nova URL'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
