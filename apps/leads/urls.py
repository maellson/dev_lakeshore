# apps/leads/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'', LeadViewSet, basename='lead')


# URLs do app
app_name = 'leads'

urlpatterns = [
    # API endpoints via router
    path('', include(router.urls)),
]

"""
ENDPOINTS DISPONÍVEIS:

## LEADS ENDPOINTS
GET    /api/leads/                    - Lista leads com filtros
POST   /api/leads/                    - Criar novo lead
GET    /api/leads/{id}/               - Detalhes de lead
PATCH  /api/leads/{id}/               - Atualizar lead
DELETE /api/leads/{id}/               - Remover lead
POST   /api/leads/{id}/convert/       - Converter lead para contrato
GET    /api/leads/form-data/          - Dados para formulário web
GET    /api/leads/stats/              - Estatísticas de leads
PATCH  /api/leads/bulk-update-status/ - Atualização em massa
#GET    /api/leads/choices/  

## COUNTIES ENDPOINTS  
GET    /api/counties/                 - Lista counties
GET    /api/counties/{id}/            - Detalhes de county
GET    /api/counties/choices/         - Counties como choices
   




## FILTROS DISPONÍVEIS (?filter=value)
status=PENDING                        - Por status específico
status__in=PENDING,QUALIFIED          - Por múltiplos status
county=1                             - Por county específico
house_model=1774                     - Por modelo de casa
elevation=A                          - Por elevação
has_hoa=true                         - Por HOA
is_realtor=false                     - Por realtor
contract_value__gte=100000           - Valor mínimo
contract_value__lte=500000           - Valor máximo
created_at__date=2025-01-15          - Por data específica
created_at__date__gte=2025-01-01     - Data mínima
created_at__date__lte=2025-01-31     - Data máxima
convertible=true                     - Apenas convertíveis
age_gte=7                           - Leads com mais de 7 dias
age_lte=30                          - Leads com menos de 30 dias

## BUSCA (?search=term)
search=John                          - Busca em nome, email, phone, etc.

## ORDENAÇÃO (?ordering=field)
ordering=created_at                  - Mais antigos primeiro
ordering=-created_at                 - Mais recentes primeiro (default)
ordering=contract_value              - Menor valor primeiro
ordering=-contract_value             - Maior valor primeiro
ordering=client_full_name            - Ordem alfabética
"""
