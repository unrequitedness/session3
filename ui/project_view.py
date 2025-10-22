import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from models.project import Project
from models.enums import ProjectStatus, ProjectType
from services.project_service import ProjectService
from strategies.display_strategy import TileDisplayStrategy, KanbanDisplayStrategy
from ui.modals import ProjectCardModal, ProjectStageModal

class ProjectView:
    def __init__(self, root, project_service: ProjectService):
        self.root = root
        self.project_service = project_service
        self.current_display_strategy = None
        self.current_canvas = None
        
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        self.root.title("Управление проектами")
        self.root.geometry("1200x700")
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Плиточный вид", 
                  command=self.show_tile_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Kanban доска", 
                  command=self.show_kanban_view).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Статистика", 
                  command=self.show_statistics).pack(side=tk.RIGHT, padx=5)
        
        self.display_frame = ttk.Frame(main_frame)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_projects(self):
        self.projects = self.project_service.get_all_projects()
        if not self.projects:
            self.create_sample_projects()

    def create_sample_projects(self):
        from datetime import datetime
        
        sample_projects = [
            Project(0, "Развитие дорожной сети", ProjectType.INVESTMENT, 
                   ProjectStatus.IN_PROGRESS, datetime(2024, 1, 1), datetime(2024, 12, 31),
                   "Иванов И.И.", "Проект развития дорожной инфраструктуры"),
            Project(0, "Корпоративная система", ProjectType.CORPORATE,
                   ProjectStatus.PLANNED, datetime(2024, 3, 1), datetime(2024, 8, 31),
                   "Петров П.П.", "Внедрение новой корпоративной системы"),
            Project(0, "Инвестиции в логистику", ProjectType.INVESTMENT,
                   ProjectStatus.APPROVAL, datetime(2024, 2, 1), datetime(2024, 11, 30),
                   "Сидоров С.С.", "Инвестиционный проект в логистическую инфраструктуру"),
            Project(0, "Модернизация ИТ", ProjectType.CORPORATE,
                   ProjectStatus.COMPLETED, datetime(2024, 1, 15), datetime(2024, 6, 30),
                   "Козлов К.К.", "Модернизация ИТ-инфраструктуры компании")
        ]
        
        for i, project in enumerate(sample_projects):
            project.progress = [30, 0, 45, 100][i]
            if project.progress == 100:
                project.actual_end = datetime(2024, 6, 30)
        
        self.projects = sample_projects

    def show_tile_view(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        
        strategy = TileDisplayStrategy()
        self.current_canvas = strategy.display(self.projects, self.display_frame)
        self.current_display_strategy = strategy
        
        self.current_canvas.bind('<Button-1>', self.on_tile_click)

    def show_kanban_view(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        
        strategy = KanbanDisplayStrategy()
        strategy.display(self.projects, self.display_frame)
        self.current_display_strategy = strategy

    def on_tile_click(self, event):
        if not self.current_canvas:
            return
            
        items = self.current_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if items:
            for item in items:
                tags = self.current_canvas.gettags(item)
                if tags and 'project' in tags:
                    project_id = int(tags[1])
                    self.show_project_card(project_id)
                    break

    def show_project_card(self, project_id: int):
        project = next((p for p in self.projects if p.project_id == project_id), None)
        if project:
            ProjectCardModal(self.root, project, self.project_service)
        else:
            messagebox.showerror("Ошибка", "Проект не найден")

    def show_statistics(self):
        stats = self.project_service.get_project_progress_stats()
        
        stats_text = f"""
Статистика проектов:
-------------------
Всего проектов: {stats['total']}
Завершено: {stats['completed']}
В работе: {stats['in_progress']}
С отставанием: {stats['delayed']}
Процент завершения: {stats['completion_rate']:.1f}%
        """
        
        messagebox.showinfo("Статистика проектов", stats_text)

    def show_stage_network_diagram(self, stage_name: str):
        ProjectStageModal(self.root, stage_name)