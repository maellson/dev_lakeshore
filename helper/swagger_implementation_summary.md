# Resumo de Implementação do Swagger

## Objetivo
Organizar o Swagger/ReDoc por seções usando tags do DRF-YASG para melhorar a navegação e usabilidade da documentação da API.

## Situação Atual
- O app Account já tem uma implementação parcial de tags do Swagger na classe `UserProfileView`
- O app Projects tem um atributo `swagger_tags` na classe `ProjectViewSet`, mas não tem decoradores `@swagger_auto_schema` nos métodos
- Nenhum dos outros apps tem implementação de tags do Swagger

## Próximos Passos

### 1. Criar Arquivo de Constantes
Criar o arquivo `apps/core/swagger_tags.py` com as constantes para as tags:

```python
API_TAGS = {
    'ACCOUNT': '👥 Account & Users',
    'PROJECTS': '🏗️ Projects & Construction',
    'FINANCIAL': '💰 Financial Management',
    'PURCHASES': '🛒 Purchases & Suppliers',
    'CLIENT_PORTAL': '📋 Client Portal',
    'NOTIFICATIONS': '🔔 Notifications & Tasks',
    'LEADS': '🎯 Leads & Sales',
    'CORE': '⚙️ Core & Settings',
}
```

### 2. Implementar Tags por App

#### Account App
- Atualizar a classe `UserProfileView` para usar a constante `API_TAGS['ACCOUNT']` em vez da string hardcoded
- Adicionar decoradores `@swagger_auto_schema` em todas as outras views do app

#### Projects App
- Atualizar o atributo `swagger_tags` da classe `ProjectViewSet` para usar a constante `API_TAGS['PROJECTS']`
- Adicionar decoradores `@swagger_auto_schema` em todos os métodos da classe
- Fazer o mesmo para as outras classes do app

#### Leads App
- Adicionar decoradores `@swagger_auto_schema` em todas as views do app, usando a constante `API_TAGS['LEADS']`

#### Core App
- Adicionar decoradores `@swagger_auto_schema` em todas as views do app, usando a constante `API_TAGS['CORE']`

#### Financial App
- Adicionar decoradores `@swagger_auto_schema` em todas as views do app, usando a constante `API_TAGS['FINANCIAL']`

#### Purchases App
- Adicionar decoradores `@swagger_auto_schema` em todas as views do app, usando a constante `API_TAGS['PURCHASES']`

#### Client Portal App
- Adicionar decoradores `@swagger_auto_schema` em todas as views do app, usando a constante `API_TAGS['CLIENT_PORTAL']`

#### Notifications & Tasks App
- Adicionar decoradores `@swagger_auto_schema` em todas as views do app, usando a constante `API_TAGS['NOTIFICATIONS']`

### 3. Melhorar Descrição do Schema View
Atualizar a descrição do `schema_view` no arquivo `erp_lakeshore/urls.py` para incluir seções organizadas com os mesmos emojis e nomes das tags.

## Padrão de Implementação

Para cada view, seguir o padrão:

```python
from core.swagger_tags import API_TAGS

@swagger_auto_schema(
    tags=[API_TAGS['TAG_NAME']],
    operation_summary="Título curto da operação",
    operation_description="Descrição detalhada da operação",
    responses={
        200: ResponseSerializer(),
        400: 'Descrição do erro',
        # outros códigos de resposta
    }
)
def method(self, request, *args, **kwargs):
    # implementação existente
```

Para ViewSets, decorar cada método individualmente (list, retrieve, create, update, partial_update, destroy) e também os métodos de action.

## Benefícios Esperados
- Documentação da API organizada em seções colapsáveis por funcionalidade
- Navegação mais intuitiva no Swagger e ReDoc
- Descrições claras e consistentes para todas as operações
- Melhor experiência para desenvolvedores que consomem a API