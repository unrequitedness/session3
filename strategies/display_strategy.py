from abc import ABC, abstractmethod
from typing import List
import tkinter as tk
from tkinter import ttk
from models.project import Project
from models.enums import ProjectStatus, ProjectType

class DisplayStrategy(ABC):
    @abstractmethod
    def display(self, projects: List[Project], container):
        pass

class TileDisplayStrategy(DisplayStrategy):
    def display(self, projects: List[Project], container):
        canvas = tk.Canvas(container, bg="white")
        scrollbar_y = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        colors = {
            ProjectType.INVESTMENT: "orange",
            ProjectType.CORPORATE: "green"
        }
        status_colors = {
            ProjectStatus.CREATED: "beige",
            ProjectStatus.PLANNED: "yellow",
            ProjectStatus.IN_PROGRESS: "green",
            ProjectStatus.APPROVAL: "orange",
            ProjectStatus.APPROVAL_WAITING: "purple",
            ProjectStatus.VERIFICATION: "red",
            ProjectStatus.REQUIRES_REFINEMENT: "pink",
            ProjectStatus.FROZEN: "lightblue",
            ProjectStatus.COMPLETED: "blue",
            ProjectStatus.CLOSED: "darkblue",
            ProjectStatus.ARCHIVED: "darkgreen",
            ProjectStatus.CANCELLED: "gray"
        }
        
        x, y = 20, 20
        tile_width, tile_height = 200, 100
        
        for project in projects:
            main_color = colors.get(project.project_type, "white")
            status_color = status_colors.get(project.status, "white")
            
            canvas.create_rectangle(x, y, x + tile_width, y + tile_height, 
                                   fill=main_color, outline="black")
            canvas.create_rectangle(x, y, x + tile_width, y + 20, 
                                   fill=status_color, outline="black")
            canvas.create_text(x + tile_width/2, y + 10, text=project.status.value, 
                              font=("Arial", 8, "bold"))
            canvas.create_text(x + tile_width/2, y + 40, text=project.name, 
                              font=("Arial", 10, "bold"))
            canvas.create_text(x + tile_width/2, y + 60, text=project.manager, 
                              font=("Arial", 8))
            canvas.create_text(x + tile_width/2, y + 80, text=f"Прогресс: {project.progress}%", 
                              font=("Arial", 8))
            
            x += tile_width + 20
            if x > 600:
                x = 20
                y += tile_height + 20
        
        canvas.configure(scrollregion=canvas.bbox("all"))
        return canvas

class KanbanDisplayStrategy(DisplayStrategy):
    def display(self, projects: List[Project], container):
        for widget in container.winfo_children():
            widget.destroy()
        
        columns = {
            "Бэклог": [p for p in projects if p.status in [ProjectStatus.CREATED, ProjectStatus.PLANNED]],
            "В работе": [p for p in projects if p.status in [ProjectStatus.IN_PROGRESS, ProjectStatus.APPROVAL]],
            "На проверке": [p for p in projects if p.status in [ProjectStatus.VERIFICATION, ProjectStatus.APPROVAL_WAITING]],
            "Завершено": [p for p in projects if p.status in [ProjectStatus.COMPLETED, ProjectStatus.CLOSED]]
        }
        
        for col_name, col_projects in columns.items():
            col_frame = ttk.LabelFrame(container, text=f"{col_name} ({len(col_projects)})")
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            for project in col_projects:
                project_frame = ttk.Frame(col_frame, relief="solid", borderwidth=1)
                project_frame.pack(fill=tk.X, padx=2, pady=2)
                
                ttk.Label(project_frame, text=project.name, font=("Arial", 9, "bold")).pack(anchor="w")
                ttk.Label(project_frame, text=f"Руководитель: {project.manager}").pack(anchor="w")
                ttk.Label(project_frame, text=f"Прогресс: {project.progress}%").pack(anchor="w")
                
                progress = ttk.Progressbar(project_frame, value=project.progress, maximum=100)
                progress.pack(fill=tk.X, padx=5, pady=2)
        
        return container