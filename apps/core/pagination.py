# apps/core/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class CustomPageNumberPagination(PageNumberPagination):
    """
    Paginação customizada com metadados adicionais
    
    Fornece informações extras úteis para o frontend:
    - total_pages: Número total de páginas
    - total_items: Número total de itens
    - current_page: Página atual
    - page_size: Tamanho da página
    - has_next: Se há próxima página
    - has_previous: Se há página anterior
    
    USAGE:
    - Definir como pagination_class em ViewSets
    - Configurar como padrão em REST_FRAMEWORK settings
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = None  # Removido limite máximo de paginação
    
    def get_paginated_response(self, data):
        """Resposta customizada com metadados adicionais"""
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('has_next', self.page.has_next()),
            ('has_previous', self.page.has_previous()),
            ('results', data)
        ]))


class SmallPageNumberPagination(CustomPageNumberPagination):
    """Paginação para listas menores (10 itens por página)"""
    page_size = 10


class LargePageNumberPagination(CustomPageNumberPagination):
    """Paginação para listas maiores (50 itens por página)"""
    page_size = 50