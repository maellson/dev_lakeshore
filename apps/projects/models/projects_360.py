# apps/projects/models/projects_360.py
from django.db import models
from .project import Project

class Projects360(Project):
    """
    Modelo proxy para view consolidada de projetos
    Read-only - apenas para visualização no admin
    """
    
    class Meta:
        proxy = True
        verbose_name = "Projects 360° View"
        verbose_name_plural = "Projects 360° Views"
        
    def __str__(self):
        return f"360° - {self.project_name}"