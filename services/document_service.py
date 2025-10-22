from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models.document import Document, DocumentVersion, ApprovalRoute
from models.enums import DocumentStatus, DocumentCategory, RouteStatus
from repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def create_document(self, name: str, category: DocumentCategory, author: str) -> Document:
        document = Document(
            doc_id=0,
            name=name,
            category=category,
            status=DocumentStatus.DRAFT,
            author=author,
            version="1.0"
        )
        self.repository.save_document(document)
        return document

    def publish_document(self, doc_id: int) -> bool:
        documents = self.repository.get_all_documents()
        for doc in documents:
            if doc.doc_id == doc_id:
                doc.status = DocumentStatus.PUBLISHED
                self.repository.save_document(doc)
                return True
        return False

    def create_new_version(self, doc_id: int, author: str, changes: str) -> Optional[Document]:
        documents = self.repository.get_all_documents()
        for doc in documents:
            if doc.doc_id == doc_id:
                current_version = float(doc.version)
                new_version = str(current_version + 0.1)
                
                doc.version = new_version
                doc.status = DocumentStatus.UPDATING
                self.repository.save_document(doc)
                return doc
        return None

    def get_document_history(self, doc_id: int) -> List[DocumentVersion]:
        documents = self.repository.get_all_documents()
        history = []
        for doc in documents:
            if doc.doc_id == doc_id:
                version = DocumentVersion(
                    version=doc.version,
                    doc_id=doc.doc_id,
                    author=doc.author,
                    changes=f"Версия {doc.version}"
                )
                history.append(version)
        return history

    def search_documents_advanced(self, search_params: Dict) -> List[Document]:
        documents = self.repository.get_all_documents()
        results = documents
        
        if 'status' in search_params:
            results = [d for d in results if d.status.value == search_params['status']]
        if 'category' in search_params:
            results = [d for d in results if d.category.value == search_params['category']]
        if 'author' in search_params:
            results = [d for d in results if search_params['author'].lower() in d.author.lower()]
        if 'date_from' in search_params:
            results = [d for d in results if d.creation_date >= search_params['date_from']]
        if 'date_to' in search_params:
            results = [d for d in results if d.creation_date <= search_params['date_to']]
            
        return results

    def get_documents_by_category(self, category: DocumentCategory) -> List[Document]:
        documents = self.repository.get_all_documents()
        return [d for d in documents if d.category == category]