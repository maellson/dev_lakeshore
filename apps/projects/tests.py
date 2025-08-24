from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from core.models import County
from .models.incorporation import Incorporation
from ..contracts.models.contract import Contract
from .models.project import Project
from .models.phase_project import PhaseProject
from .models.task_project import TaskProject
from .models.contact import Contact
from .models.choice_types import (
    ProjectType, ProjectStatus, IncorporationType, IncorporationStatus,
    StatusContract, PaymentMethod, ProductionCell, OwnerType
)

User = get_user_model()


class IncorporationAPITests(APITestCase):
    """
    Testes para a API de Incorporações
    """
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Autenticar cliente
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar dados necessários
        self.county = County.objects.create(
            name='Test County',
            state='Test State',
            country='Test Country'
        )
        
        self.incorporation_type = IncorporationType.objects.create(
            code='CONDO',
            name='Condomínio',
            color='#FF0000',
            icon='building',
            order=1,
            is_active=True
        )
        
        self.incorporation_status = IncorporationStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#0000FF',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar uma incorporação para testes
        self.incorporation = Incorporation.objects.create(
            name='Test Incorporation',
            incorporation_type=self.incorporation_type,
            incorporation_status=self.incorporation_status,
            county=self.county,
            project_description='Test Description',
            launch_date='2025-01-01',
            created_by=self.user
        )
        
        # URLs para testes
        self.list_url = reverse('projects:incorporation-list')
        self.detail_url = reverse('projects:incorporation-detail', kwargs={'pk': self.incorporation.pk})
        self.projects_url = reverse('projects:incorporation-projects', kwargs={'pk': self.incorporation.pk})
        
    def test_list_incorporations(self):
        """Teste para listar incorporações"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Incorporation')
        
    def test_create_incorporation(self):
        """Teste para criar uma nova incorporação"""
        data = {
            'name': 'New Incorporation',
            'incorporation_type': self.incorporation_type.id,
            'incorporation_status': self.incorporation_status.id,
            'county': self.county.id,
            'project_description': 'New Description',
            'launch_date': '2025-02-01',
            'is_active': True
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Incorporation')
        self.assertEqual(Incorporation.objects.count(), 2)
        
    def test_retrieve_incorporation(self):
        """Teste para obter detalhes de uma incorporação"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Incorporation')
        self.assertEqual(response.data['project_description'], 'Test Description')
        
    def test_update_incorporation(self):
        """Teste para atualizar uma incorporação"""
        data = {
            'name': 'Updated Incorporation',
            'project_description': 'Updated Description'
        }
        
        response = self.client.patch(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Incorporation')
        self.assertEqual(response.data['project_description'], 'Updated Description')
        
        # Verificar se a atualização foi persistida no banco
        self.incorporation.refresh_from_db()
        self.assertEqual(self.incorporation.name, 'Updated Incorporation')
        
    def test_delete_incorporation(self):
        """Teste para remover uma incorporação"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Incorporation.objects.count(), 0)
        
    def test_list_incorporation_projects(self):
        """Teste para listar projetos de uma incorporação"""
        # Criar um projeto para a incorporação
        project_status = ProjectStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#00FF00',
            icon='planning',
            order=1,
            is_active=True
        )
        
        project = Project.objects.create(
            project_name='Test Project',
            incorporation=self.incorporation,
            status_project=project_status,
            address='Test Address',
            area_total=100.0,
            completion_percentage=0,
            expected_delivery_date='2025-12-31',
            created_by=self.user
        )
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['project_name'], 'Test Project')


class ProjectAPITests(APITestCase):
    """
    Testes para a API de Projetos
    """
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Autenticar cliente
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar dados necessários
        self.county = County.objects.create(
            name='Test County',
            state='Test State',
            country='Test Country'
        )
        
        self.incorporation_type = IncorporationType.objects.create(
            code='CONDO',
            name='Condomínio',
            color='#FF0000',
            icon='building',
            order=1,
            is_active=True
        )
        
        self.incorporation_status = IncorporationStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#0000FF',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar uma incorporação para testes
        self.incorporation = Incorporation.objects.create(
            name='Test Incorporation',
            incorporation_type=self.incorporation_type,
            incorporation_status=self.incorporation_status,
            county=self.county,
            project_description='Test Description',
            launch_date='2025-01-01',
            created_by=self.user
        )
        
        # Criar status de projeto
        self.project_status = ProjectStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#00FF00',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar um projeto para testes
        self.project = Project.objects.create(
            project_name='Test Project',
            incorporation=self.incorporation,
            status_project=self.project_status,
            address='Test Address',
            area_total=100.0,
            completion_percentage=0,
            expected_delivery_date='2025-12-31',
            created_by=self.user
        )
        
        # URLs para testes
        self.list_url = reverse('projects:project-list')
        self.detail_url = reverse('projects:project-detail', kwargs={'pk': self.project.pk})
        self.phases_url = reverse('projects:project-phases', kwargs={'pk': self.project.pk})
        
    def test_list_projects(self):
        """Teste para listar projetos"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['project_name'], 'Test Project')
        
    def test_create_project(self):
        """Teste para criar um novo projeto"""
        data = {
            'project_name': 'New Project',
            'incorporation': self.incorporation.id,
            'status_project': self.project_status.id,
            'address': 'New Address',
            'area_total': 200.0,
            'completion_percentage': 0,
            'expected_delivery_date': '2026-01-01'
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['project_name'], 'New Project')
        self.assertEqual(Project.objects.count(), 2)
        
    def test_retrieve_project(self):
        """Teste para obter detalhes de um projeto"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'Test Project')
        self.assertEqual(response.data['address'], 'Test Address')
        
    def test_update_project(self):
        """Teste para atualizar um projeto"""
        data = {
            'project_name': 'Updated Project',
            'address': 'Updated Address',
            'completion_percentage': 10
        }
        
        response = self.client.patch(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'Updated Project')
        self.assertEqual(response.data['address'], 'Updated Address')
        self.assertEqual(response.data['completion_percentage'], 10)
        
        # Verificar se a atualização foi persistida no banco
        self.project.refresh_from_db()
        self.assertEqual(self.project.project_name, 'Updated Project')
        
    def test_delete_project(self):
        """Teste para remover um projeto"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)
        
    def test_list_project_phases(self):
        """Teste para listar fases de um projeto"""
        # Criar uma fase para o projeto
        phase = PhaseProject.objects.create(
            phase_name='Test Phase',
            phase_code='TP-001',
            project=self.project,
            phase_status='PENDING',
            priority='MEDIUM',
            execution_order=1,
            completion_percentage=0,
            planned_start_date='2025-01-01',
            planned_end_date='2025-02-01',
            created_by=self.user
        )
        
        response = self.client.get(self.phases_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['phase_name'], 'Test Phase')


class TaskProjectAPITests(APITestCase):
    """
    Testes para a API de Tarefas de Projeto
    """
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Autenticar cliente
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar dados necessários
        self.county = County.objects.create(
            name='Test County',
            state='Test State',
            country='Test Country'
        )
        
        self.incorporation_type = IncorporationType.objects.create(
            code='CONDO',
            name='Condomínio',
            color='#FF0000',
            icon='building',
            order=1,
            is_active=True
        )
        
        self.incorporation_status = IncorporationStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#0000FF',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar uma incorporação para testes
        self.incorporation = Incorporation.objects.create(
            name='Test Incorporation',
            incorporation_type=self.incorporation_type,
            incorporation_status=self.incorporation_status,
            county=self.county,
            project_description='Test Description',
            launch_date='2025-01-01',
            created_by=self.user
        )
        
        # Criar status de projeto
        self.project_status = ProjectStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#00FF00',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar um projeto para testes
        self.project = Project.objects.create(
            project_name='Test Project',
            incorporation=self.incorporation,
            status_project=self.project_status,
            address='Test Address',
            area_total=100.0,
            completion_percentage=0,
            expected_delivery_date='2025-12-31',
            created_by=self.user
        )
        
        # Criar uma fase para o projeto
        self.phase = PhaseProject.objects.create(
            phase_name='Test Phase',
            phase_code='TP-001',
            project=self.project,
            phase_status='PENDING',
            priority='MEDIUM',
            execution_order=1,
            completion_percentage=0,
            planned_start_date='2025-01-01',
            planned_end_date='2025-02-01',
            created_by=self.user
        )
        
        # Criar uma tarefa para a fase
        self.task = TaskProject.objects.create(
            task_name='Test Task',
            task_code='TT-001',
            phase_project=self.phase,
            task_status='PENDING',
            priority='MEDIUM',
            execution_order=1,
            completion_percentage=0,
            planned_start_date='2025-01-01',
            planned_end_date='2025-01-15',
            assigned_to=self.user,
            created_by=self.user
        )
        
        # URLs para testes
        self.list_url = reverse('projects:task-list')
        self.detail_url = reverse('projects:task-detail', kwargs={'pk': self.task.pk})
        self.start_url = reverse('projects:task-start', kwargs={'pk': self.task.pk})
        self.complete_url = reverse('projects:task-complete', kwargs={'pk': self.task.pk})
        
    def test_list_tasks(self):
        """Teste para listar tarefas"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['task_name'], 'Test Task')
        
    def test_create_task(self):
        """Teste para criar uma nova tarefa"""
        data = {
            'task_name': 'New Task',
            'task_code': 'NT-001',
            'phase_project': self.phase.id,
            'task_status': 'PENDING',
            'priority': 'HIGH',
            'execution_order': 2,
            'completion_percentage': 0,
            'planned_start_date': '2025-01-16',
            'planned_end_date': '2025-01-31',
            'assigned_to': self.user.id
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['task_name'], 'New Task')
        self.assertEqual(TaskProject.objects.count(), 2)
        
    def test_retrieve_task(self):
        """Teste para obter detalhes de uma tarefa"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_name'], 'Test Task')
        self.assertEqual(response.data['task_status'], 'PENDING')
        
    def test_update_task(self):
        """Teste para atualizar uma tarefa"""
        data = {
            'task_name': 'Updated Task',
            'task_status': 'READY_TO_START',
            'completion_percentage': 10
        }
        
        response = self.client.patch(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_name'], 'Updated Task')
        self.assertEqual(response.data['task_status'], 'READY_TO_START')
        self.assertEqual(response.data['completion_percentage'], 10)
        
        # Verificar se a atualização foi persistida no banco
        self.task.refresh_from_db()
        self.assertEqual(self.task.task_name, 'Updated Task')
        
    def test_delete_task(self):
        """Teste para remover uma tarefa"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TaskProject.objects.count(), 0)
        
    def test_start_task(self):
        """Teste para iniciar uma tarefa"""
        # Atualizar a tarefa para READY_TO_START
        self.task.task_status = 'READY_TO_START'
        self.task.save()
        
        response = self.client.post(self.start_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_status'], 'IN_PROGRESS')
        self.assertIsNotNone(response.data['actual_start_date'])
        
        # Verificar se a atualização foi persistida no banco
        self.task.refresh_from_db()
        self.assertEqual(self.task.task_status, 'IN_PROGRESS')
        
    def test_complete_task(self):
        """Teste para completar uma tarefa"""
        # Atualizar a tarefa para IN_PROGRESS
        self.task.task_status = 'IN_PROGRESS'
        self.task.actual_start_date = '2025-01-01'
        self.task.save()
        
        response = self.client.post(self.complete_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_status'], 'COMPLETED')
        self.assertIsNotNone(response.data['actual_end_date'])
        
        # Verificar se a atualização foi persistida no banco
        self.task.refresh_from_db()
        self.assertEqual(self.task.task_status, 'COMPLETED')
        self.assertEqual(self.task.completion_percentage, 100)


class ContactAPITests(APITestCase):
    """
    Testes para a API de Contatos
    """
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Criar usuário para contato
        self.contact_user = User.objects.create_user(
            username='contactuser',
            email='contact@example.com',
            password='contactpassword',
            first_name='Contact',
            last_name='User'
        )
        
        # Autenticar cliente
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar dados necessários
        self.county = County.objects.create(
            name='Test County',
            state='Test State',
            country='Test Country'
        )
        
        self.incorporation_type = IncorporationType.objects.create(
            code='CONDO',
            name='Condomínio',
            color='#FF0000',
            icon='building',
            order=1,
            is_active=True
        )
        
        self.incorporation_status = IncorporationStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#0000FF',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar uma incorporação para testes
        self.incorporation = Incorporation.objects.create(
            name='Test Incorporation',
            incorporation_type=self.incorporation_type,
            incorporation_status=self.incorporation_status,
            county=self.county,
            project_description='Test Description',
            launch_date='2025-01-01',
            created_by=self.user
        )
        
        # Criar status de projeto
        self.project_status = ProjectStatus.objects.create(
            code='PLANNING',
            name='Em Planejamento',
            color='#00FF00',
            icon='planning',
            order=1,
            is_active=True
        )
        
        # Criar um projeto para testes
        self.project = Project.objects.create(
            project_name='Test Project',
            incorporation=self.incorporation,
            status_project=self.project_status,
            address='Test Address',
            area_total=100.0,
            completion_percentage=0,
            expected_delivery_date='2025-12-31',
            created_by=self.user
        )
        
        # Criar um contato para testes
        self.contact = Contact.objects.create(
            contact=self.contact_user,
            project=self.project,
            contact_role='MANAGER',
            is_active=True,
            created_by=self.user
        )
        
        # URLs para testes
        self.list_url = reverse('projects:contact-list')
        self.detail_url = reverse('projects:contact-detail', kwargs={'pk': self.contact.pk})
        self.by_project_url = reverse('projects:contact-by-project', kwargs={'project_id': self.project.pk})
        
    def test_list_contacts(self):
        """Teste para listar contatos"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['contact_name'], 'Contact User')
        
    def test_create_contact(self):
        """Teste para criar um novo contato"""
        # Criar outro usuário para contato
        new_contact_user = User.objects.create_user(
            username='newcontact',
            email='newcontact@example.com',
            password='newcontactpassword',
            first_name='New',
            last_name='Contact'
        )
        
        data = {
            'contact': new_contact_user.id,
            'project': self.project.id,
            'contact_role': 'ENGINEER',
            'is_active': True
        }
        
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 2)
        
    def test_retrieve_contact(self):
        """Teste para obter detalhes de um contato"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contact']['full_name'], 'Contact User')
        self.assertEqual(response.data['contact_role'], 'MANAGER')
        
    def test_update_contact(self):
        """Teste para atualizar um contato"""
        data = {
            'contact_role': 'SUPERVISOR',
            'is_active': False
        }
        
        response = self.client.patch(self.detail_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se a atualização foi persistida no banco
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.contact_role, 'SUPERVISOR')
        self.assertEqual(self.contact.is_active, False)
        
    def test_delete_contact(self):
        """Teste para remover um contato"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)
        
    def test_list_contacts_by_project(self):
        """Teste para listar contatos por projeto"""
        response = self.client.get(self.by_project_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['contact_name'], 'Contact User')