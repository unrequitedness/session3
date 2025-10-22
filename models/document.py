from datetime import datetime
from typing import List, Optional
from .enums import DocumentStatus, DocumentCategory

class Document:
    def __init__(self, doc_id: int, name: str, category: DocumentCategory, status: DocumentStatus,
                 author: str, version: str = "1.0"):
        self.doc_id = doc_id
        self.name = name
        self.category = category
        self.status = status
        self.author = author
        self.version = version
        self.creation_date = datetime.now()
        self.description = ""
        self.comments = []
        self.file_path = ""
        self.previous_versions = []

class DocumentVersion:
    def __init__(self, version: str, doc_id: int, author: str, changes: str):
        self.version = version
        self.doc_id = doc_id
        self.author = author
        self.changes = changes
        self.version_date = datetime.now()

class ApprovalRoute:
    def __init__(self, route_id: int, name: str, status: str):
        self.route_id = route_id
        self.name = name
        self.status = status
        self.stages = []

class ApprovalStage:
    def __init__(self, stage_id: int, approver: str, position: str, order: int):
        self.stage_id = stage_id
        self.approver = approver
        self.position = position
        self.order = order
        self.status = "pending"
        self.comment = ""