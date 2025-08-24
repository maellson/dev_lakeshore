# ERP Lakeshore

![Lakeshore ERP](https://via.placeholder.com/800x200?text=Lakeshore+ERP)

## Sobre o Projeto

O ERP Lakeshore é um sistema de gestão empresarial completo desenvolvido para empresas de construção e incorporação imobiliária. O sistema gerencia todo o ciclo de vida de projetos imobiliários, desde a captação de leads até a entrega final do projeto, incluindo contratos, gestão financeira e acompanhamento de obras.

### Principais Funcionalidades

- **Gestão de Leads**: Captura e qualificação de potenciais clientes
- **Gestão de Contratos**: Criação e acompanhamento de contratos com clientes
- **Gestão de Projetos**: Planejamento, execução e monitoramento de projetos de construção
- **Gestão Financeira**: Controle de custos, pagamentos e ROI dos projetos
- **Portal do Cliente**: Interface para clientes acompanharem seus projetos
- **Notificações**: Sistema de alertas e notificações para eventos importantes
- **Integrações**: Conexão com sistemas externos

## Tecnologias Utilizadas

### Backend
- **Python 3.11**: Linguagem de programação principal
- **Django 5.0.1**: Framework web de alto nível
- **Django REST Framework 3.14.0**: Para construção de APIs RESTful
- **PostgreSQL**: Banco de dados relacional
- **Gunicorn**: Servidor WSGI HTTP para Unix

### Segurança e Autenticação
- **Django REST Framework SimpleJWT**: Autenticação via tokens JWT
- **Django CORS Headers**: Gerenciamento de CORS (Cross-Origin Resource Sharing)

### Ferramentas de Desenvolvimento
- **Black**: Formatador de código Python
- **Django Extensions**: Utilitários para desenvolvimento
- **Django Debug Toolbar**: Ferramenta de análise de performance (opcional)

### Infraestrutura
- **Docker**: Containerização da aplicação
- **AWS ECS**: Serviço de orquestração de containers
- **AWS ECR**: Registro de containers Docker

## Estrutura do Projeto

O projeto é organizado em múltiplos aplicativos Django, cada um responsável por uma área funcional específica:

- **account**: Gerenciamento de usuários, perfis e permissões
- **client_portal**: Portal para acesso de clientes
- **contracts**: Gerenciamento de contratos
- **core**: Funcionalidades centrais e compartilhadas
- **financial**: Gestão financeira
- **integrations**: Integrações com sistemas externos
- **leads**: Gestão de leads e potenciais clientes
- **notifications**: Sistema de notificações
- **projects**: Gerenciamento de projetos de construção
- **purchases**: Gestão de compras e fornecedores
- **tasks**: Gerenciamento de tarefas

## Requisitos

- Python 3.11+
- PostgreSQL
- Docker (opcional, mas recomendado)
- AWS CLI (para deploy)

## Instalação e Configuração

### Instalação Local

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd erp_lakeshore
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (crie um arquivo .env na raiz do projeto)

5. Execute as migrações:
```bash
python manage.py migrate
```

6. Popule dados iniciais:
```bash
python manage.py populate_initial_data
python manage.py setup_permissions
python manage.py create_superuser_custom
```

### Configuração com Docker

1. Construa a imagem Docker:
```bash
docker build -f docker/Dockerfile -t django_lakeshore .
```

2. Execute o container:
```bash
docker run -p 8000:8000 django_lakeshore
```

Ou, preferencialmente, use Docker Compose:

```bash
cd docker/
docker-compose up
```

## Execução

### Desenvolvimento Local

```bash
python manage.py runserver
```

### Usando Docker Compose (Recomendado)

```bash
cd docker/
docker-compose up
```

Acesse o sistema em: http://localhost:8000

### Comandos Úteis

#### Limpar o banco de dados
```bash
python manage.py flush --settings=erp_lakeshore.settings
```

#### Executar migrações no Docker
```bash
docker exec -it [CONTAINER_ID] python manage.py migrate
```

#### Criar superusuário no Docker
```bash
docker exec -it [CONTAINER_ID] python manage.py createsuperuser
```

## Deploy

O sistema está configurado para deploy na AWS utilizando ECS (Elastic Container Service).

### Deploy Manual

1. Faça login no ECR:
```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 460044121130.dkr.ecr.us-east-2.amazonaws.com
```

2. Construa a imagem para a arquitetura correta:
```bash
docker build --platform linux/amd64 -f docker/Dockerfile -t django_lakeshore .
```

3. Tagueie a imagem:
```bash
docker tag django_lakeshore:latest 460044121130.dkr.ecr.us-east-2.amazonaws.com/erp-lakeshore:latest
```

4. Envie a imagem para o ECR:
```bash
docker push 460044121130.dkr.ecr.us-east-2.amazonaws.com/erp-lakeshore:latest
```

5. Atualize o serviço ECS:
```bash
aws ecs update-service --cluster erp-lakeshore --service erp-lakeshore-task-service --region us-east-2
```

### Deploy Automatizado

Use o script de deploy fornecido:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Configuração Inicial do Sistema

Após a instalação, é necessário configurar os dados iniciais do sistema:

1. Tipos básicos (TipoUsuario, Idioma, etc.):
```bash
python manage.py populate_initial_data
```

2. Grupos e permissões:
```bash
python manage.py setup_permissions
```

3. Superusuário:
```bash
python manage.py create_superuser_custom
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

---

Desenvolvido por Lakeshore Construction & Development
