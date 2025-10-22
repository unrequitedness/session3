import sqlite3
from datetime import datetime
from typing import List, Optional
from models.document import Document, DocumentVersion, ApprovalRoute
from models.enums import DocumentStatus, DocumentCategory, RouteStatus

class DocumentRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                author TEXT NOT NULL,
                version TEXT NOT NULL,
                creation_date DATE,
                description TEXT,
                file_path TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                version TEXT NOT NULL,
                author TEXT NOT NULL,
                changes TEXT,
                version_date DATE,
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS approval_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS approval_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER,
                approver TEXT NOT NULL,
                position TEXT NOT NULL,
                stage_order INTEGER,
                status TEXT DEFAULT 'pending',
                comment TEXT,
                FOREIGN KEY (route_id) REFERENCES approval_routes(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_all_documents(self) -> List[Document]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM documents')
        documents = []
        for row in c.fetchall():
            doc = Document(
                doc_id=row[0],
                name=row[1],
                category=DocumentCategory(row[2]),
                status=DocumentStatus(row[3]),
                author=row[4],
                version=row[5]
            )
            doc.creation_date = datetime.strptime(row[6], '%Y-%m-%d') if row[6] else None
            doc.description = row[7] or ""
            doc.file_path = row[8] or ""
            documents.append(doc)
        conn.close()
        return documents

    def save_document(self, document: Document):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if document.doc_id:
            c.execute('''
                UPDATE documents SET name=?, category=?, status=?, author=?, version=?,
                creation_date=?, description=?, file_path=? WHERE id=?
            ''', (
                document.name, document.category.value, document.status.value,
                document.author, document.version,
                document.creation_date.strftime('%Y-%m-%d') if document.creation_date else None,
                document.description, document.file_path, document.doc_id
            ))
        else:
            c.execute('''
                INSERT INTO documents (name, category, status, author, version, creation_date, description, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.name, document.category.value, document.status.value,
                document.author, document.version,
                document.creation_date.strftime('%Y-%m-%d') if document.creation_date else datetime.now().strftime('%Y-%m-%d'),
                document.description, document.file_path
            ))
            document.doc_id = c.lastrowid
        conn.commit()
        conn.close()

    def search_documents(self, query: str) -> List[Document]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT * FROM documents 
            WHERE name LIKE ? OR description LIKE ? OR author LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        documents = []
        for row in c.fetchall():
            doc = Document(
                doc_id=row[0],
                name=row[1],
                category=DocumentCategory(row[2]),
                status=DocumentStatus(row[3]),
                author=row[4],
                version=row[5]
            )
            documents.append(doc)
        conn.close()
        return documents