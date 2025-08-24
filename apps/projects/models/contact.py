from django.db import models
from simple_history.models import HistoricalRecords
from projects.models.incorporation import Incorporation
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()


class Contact(models.Model):
    """
    Intermediate table between Contacts and Projects
    BUSINESS LOGIC:
    - Defines who can follow/monitor each project
    - Separates legal ownership from operational contact
    - Allows companies to have multiple contacts per project
    - Controls access permissions per project
    """

    # Main relationships
    contact = models.ForeignKey(
        'account.CustomUser',  # Contact is a user with CLIENT type
        on_delete=models.RESTRICT,
        related_name='monitored_projects',
        verbose_name="Contact Person",
        help_text="Person who will monitor this project",
        limit_choices_to=Q(tipo_usuario__code='CLIENT') & Q(is_active=True)
    )

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='project_contacts',
        verbose_name="Project"
    )

    # Relationship to owner (to validate permission)
    owner = models.ForeignKey(
        'projects.ContractOwner',
        on_delete=models.CASCADE,
        related_name='assigned_contacts',
        verbose_name="Contract Owner",
        help_text="Owner who assigned this contact"
    )

    # Contact role/responsibility
    contact_role = models.CharField(
        max_length=100,
        choices=[
            ('PRIMARY', 'Primary Contact'),
            ('TECHNICAL', 'Technical Contact'),
            ('FINANCIAL', 'Financial Contact'),
            ('LEGAL', 'Legal Representative'),
            ('PROJECT_MANAGER', 'Project Manager'),
            ('SUPERVISOR', 'Supervisor'),
        ],
        default='PRIMARY',
        verbose_name="Contact Role"
    )

    """    # Contact details
    
    # Permissions for this contact on this project
    can_view_schedule = models.BooleanField(
        default=True,
        verbose_name="Can View Schedule"
    )
    
    can_view_budget = models.BooleanField(
        default=True, 
        verbose_name="Can View Budget"
    )
    
    can_view_invoices = models.BooleanField(
        default=False,
        verbose_name="Can View Invoices"
    )
    
    can_approve_changes = models.BooleanField(
        default=False,
        verbose_name="Can Approve Changes"
    )
    
    # Notification preferences
    receives_daily_updates = models.BooleanField(
        default=True,
        verbose_name="Receives Daily Updates"
    )
    
    receives_milestone_alerts = models.BooleanField(
        default=True,
        verbose_name="Receives Milestone Alerts"
    )
    
    receives_issue_notifications = models.BooleanField(
        default=True,
        verbose_name="Receives Issue Notifications"
    )
    
    
   """

    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
    )

    # System control
    # Controle de sistema
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Created at"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name="Created By",
        help_text="User who created this contact"
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        verbose_name = "Project Contact"
        verbose_name_plural = "Project Contacts"
        unique_together = ['contact', 'project', 'contact_role']
        indexes = [
            models.Index(fields=['contact']),
            models.Index(fields=['project']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.contact.get_full_name()} → {self.project.project_name} ({self.contact_role})"
