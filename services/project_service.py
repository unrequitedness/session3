from datetime import datetime, timedelta
from typing import List, Optional, Dict
from models.project import Project
from models.enums import ProjectStatus
from repositories.project_repository import ProjectRepository

class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def get_all_projects(self) -> List[Project]:
        return self.repository.get_all_projects()

    def get_projects_by_status(self, status: ProjectStatus) -> List[Project]:
        projects = self.repository.get_all_projects()
        return [p for p in projects if p.status == status]

    def get_projects_by_type(self, project_type: str) -> List[Project]:
        projects = self.repository.get_all_projects()
        return [p for p in projects if p.project_type.value == project_type]

    def calculate_project_deviation(self, project: Project) -> Optional[timedelta]:
        if project.actual_end and project.end_date:
            return project.actual_end - project.end_date
        return None

    def get_project_progress_stats(self) -> Dict:
        projects = self.repository.get_all_projects()
        total = len(projects)
        completed = len([p for p in projects if p.status in [ProjectStatus.COMPLETED, ProjectStatus.CLOSED]])
        in_progress = len([p for p in projects if p.status == ProjectStatus.IN_PROGRESS])
        delayed = len([p for p in projects if self.calculate_project_deviation(p) and self.calculate_project_deviation(p).days > 0])
        
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'delayed': delayed,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

    def update_project_progress(self, project_id: int, progress: int) -> bool:
        projects = self.repository.get_all_projects()
        for project in projects:
            if project.project_id == project_id:
                project.progress = max(0, min(100, progress))
                if progress >= 100:
                    project.status = ProjectStatus.COMPLETED
                    project.actual_end = datetime.now()
                self.repository.save_project(project)
                return True
        return False