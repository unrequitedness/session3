import unittest
import os
import tempfile
from datetime import datetime, timedelta
from models.project import Project
from models.enums import ProjectStatus, ProjectType
from repositories.project_repository import ProjectRepository
from services.project_service import ProjectService
from services.validation_service import ValidationService

class TestProjects(unittest.TestCase):
    def setUp(self):
        self.test_db = tempfile.mktemp()
        self.repository = ProjectRepository(self.test_db)
        self.service = ProjectService(self.repository)
        
        self.sample_project = Project(
            project_id=0,
            name="Тестовый проект",
            project_type=ProjectType.INVESTMENT,
            status=ProjectStatus.IN_PROGRESS,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            manager="Тестовый менеджер"
        )

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)

    def test_project_creation(self):
        project = self.sample_project
        self.assertEqual(project.name, "Тестовый проект")
        self.assertEqual(project.project_type, ProjectType.INVESTMENT)
        self.assertEqual(project.status, ProjectStatus.IN_PROGRESS)
        self.assertEqual(project.manager, "Тестовый менеджер")

    def test_project_save_and_retrieve(self):
        self.repository.save_project(self.sample_project)
        projects = self.repository.get_all_projects()
        
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "Тестовый проект")
        self.assertEqual(projects[0].project_type, ProjectType.INVESTMENT)

    def test_project_deviation_calculation(self):
        project = self.sample_project
        project.actual_end = datetime(2025, 1, 15)
        
        deviation = self.service.calculate_project_deviation(project)
        self.assertIsNotNone(deviation)
        self.assertGreater(deviation.days, 0)

    def test_project_progress_update(self):
        self.repository.save_project(self.sample_project)
        success = self.service.update_project_progress(self.sample_project.project_id, 75)
        
        self.assertTrue(success)
        projects = self.repository.get_all_projects()
        self.assertEqual(projects[0].progress, 75)

    def test_project_stats_calculation(self):
        projects = [
            Project(0, "Проект 1", ProjectType.INVESTMENT, ProjectStatus.COMPLETED,
                   datetime(2024, 1, 1), datetime(2024, 6, 30), "Менеджер 1"),
            Project(0, "Проект 2", ProjectType.CORPORATE, ProjectStatus.IN_PROGRESS,
                   datetime(2024, 2, 1), datetime(2024, 8, 31), "Менеджер 2"),
            Project(0, "Проект 3", ProjectType.INVESTMENT, ProjectStatus.PLANNED,
                   datetime(2024, 3, 1), datetime(2024, 9, 30), "Менеджер 3")
        ]
        
        for project in projects:
            project.progress = 100 if project.status == ProjectStatus.COMPLETED else 50
            self.repository.save_project(project)
        
        stats = self.service.get_project_progress_stats()
        
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['in_progress'], 1)
        self.assertEqual(stats['completion_rate'], 33.3)

    def test_date_validation(self):
        start_date = datetime(2024, 1, 1).date()
        end_date = datetime(2024, 12, 31).date()
        
        is_valid, message = ValidationService.validate_dates(start_date, end_date)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")

    def test_invalid_date_validation(self):
        start_date = datetime(2024, 12, 31).date()
        end_date = datetime(2024, 1, 1).date()
        
        is_valid, message = ValidationService.validate_dates(start_date, end_date)
        self.assertFalse(is_valid)
        self.assertIn("не может быть позже", message)

    def test_project_filtering_by_status(self):
        projects = [
            Project(0, "Проект 1", ProjectType.INVESTMENT, ProjectStatus.COMPLETED,
                   datetime(2024, 1, 1), datetime(2024, 6, 30), "Менеджер 1"),
            Project(0, "Проект 2", ProjectType.CORPORATE, ProjectStatus.IN_PROGRESS,
                   datetime(2024, 2, 1), datetime(2024, 8, 31), "Менеджер 2")
        ]
        
        for project in projects:
            self.repository.save_project(project)
        
        completed_projects = self.service.get_projects_by_status(ProjectStatus.COMPLETED)
        self.assertEqual(len(completed_projects), 1)
        self.assertEqual(completed_projects[0].name, "Проект 1")

    def test_project_filtering_by_type(self):
        projects = [
            Project(0, "Инвест проект", ProjectType.INVESTMENT, ProjectStatus.IN_PROGRESS,
                   datetime(2024, 1, 1), datetime(2024, 6, 30), "Менеджер 1"),
            Project(0, "Корп проект", ProjectType.CORPORATE, ProjectStatus.IN_PROGRESS,
                   datetime(2024, 2, 1), datetime(2024, 8, 31), "Менеджер 2")
        ]
        
        for project in projects:
            self.repository.save_project(project)
        
        investment_projects = self.service.get_projects_by_type("Инвестиционный")
        self.assertEqual(len(investment_projects), 1)
        self.assertEqual(investment_projects[0].name, "Инвест проект")

if __name__ == '__main__':
    unittest.main()