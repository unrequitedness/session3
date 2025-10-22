import sqlite3
from datetime import datetime
from typing import List, Optional
from models.project import Project
from models.enums import ProjectStatus, ProjectType

class ProjectRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                actual_start DATE,
                actual_end DATE,
                manager TEXT NOT NULL,
                description TEXT,
                progress INTEGER DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS project_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                due_date DATE,
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS project_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        conn.commit()
        conn.close()

    def get_all_projects(self) -> List[Project]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT id, name, type, status, start_date, end_date, actual_start, actual_end, 
                   manager, description, progress 
            FROM projects
        ''')
        projects = []
        for row in c.fetchall():
            project = Project(
                project_id=row[0],
                name=row[1],
                project_type=ProjectType(row[2]),
                status=ProjectStatus(row[3]),
                start_date=datetime.strptime(row[4], '%Y-%m-%d'),
                end_date=datetime.strptime(row[5], '%Y-%m-%d'),
                manager=row[8],
                description=row[9] or ""
            )
            project.actual_start = datetime.strptime(row[6], '%Y-%m-%d') if row[6] else None
            project.actual_end = datetime.strptime(row[7], '%Y-%m-%d') if row[7] else None
            project.progress = row[10]
            projects.append(project)
        conn.close()
        return projects

    def save_project(self, project: Project):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if project.project_id:
            c.execute('''
                UPDATE projects SET name=?, type=?, status=?, start_date=?, end_date=?,
                actual_start=?, actual_end=?, manager=?, description=?, progress=?
                WHERE id=?
            ''', (
                project.name, project.project_type.value, project.status.value,
                project.start_date.strftime('%Y-%m-%d'), project.end_date.strftime('%Y-%m-%d'),
                project.actual_start.strftime('%Y-%m-%d') if project.actual_start else None,
                project.actual_end.strftime('%Y-%m-%d') if project.actual_end else None,
                project.manager, project.description, project.progress, project.project_id
            ))
        else:
            c.execute('''
                INSERT INTO projects (name, type, status, start_date, end_date, manager, description, progress)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.name, project.project_type.value, project.status.value,
                project.start_date.strftime('%Y-%m-%d'), project.end_date.strftime('%Y-%m-%d'),
                project.manager, project.description, project.progress
            ))
            project.project_id = c.lastrowid
        conn.commit()
        conn.close()