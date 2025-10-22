from datetime import datetime, timedelta
from typing import List, Optional
from .enums import ProjectStatus, ProjectType

class Project:
    def __init__(self, project_id: int, name: str, project_type: ProjectType, status: ProjectStatus,
                 start_date: datetime, end_date: datetime, manager: str, description: str = ""):
        self.project_id = project_id
        self.name = name
        self.project_type = project_type
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.manager = manager
        self.description = description
        self.actual_start = None
        self.actual_end = None
        self.progress = 0
        self.milestones = []
        self.documents = []
        self.comments = []

class ProjectStage:
    def __init__(self, stage_id: int, name: str, project_id: int, status: ProjectStatus,
                 start_date: datetime, end_date: datetime):
        self.stage_id = stage_id
        self.name = name
        self.project_id = project_id
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.tasks = []

class Milestone:
    def __init__(self, milestone_id: int, name: str, due_date: datetime, completed: bool = False):
        self.milestone_id = milestone_id
        self.name = name
        self.due_date = due_date
        self.completed = completed