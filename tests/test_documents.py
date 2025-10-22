import unittest
import os
import tempfile
from datetime import datetime
from models.document import Document
from models.enums import DocumentStatus, DocumentCategory
from repositories.document_repository import DocumentRepository
from services.document_service import DocumentService
from services.validation_service import ValidationService
from strategies.search_strategy import SimpleSearchStrategy, AdvancedSearchStrategy

class TestDocuments(unittest.TestCase):
    def setUp(self):
        self.test_db = tempfile.mktemp()
        self.repository = DocumentRepository(self.test_db)
        self.service = DocumentService(self.repository)
        
        self.sample_document = Document(
            doc_id=0,
            name="Тестовый документ",
            category=DocumentCategory.REGULATORY,
            status=DocumentStatus.DRAFT,
            author="Тестовый автор",
            version="1.0"
        )

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)

    def test_document_creation(self):
        document = self.sample_document
        self.assertEqual(document.name, "Тестовый документ")
        self.assertEqual(document.category, DocumentCategory.REGULATORY)
        self.assertEqual(document.status, DocumentStatus.DRAFT)
        self.assertEqual(document.author, "Тестовый автор")
        self.assertEqual(document.version, "1.0")

    def test_document_save_and_retrieve(self):
        self.repository.save_document(self.sample_document)
        documents = self.repository.get_all_documents()
        
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].name, "Тестовый документ")
        self.assertEqual(documents[0].category, DocumentCategory.REGULATORY)

    def test_document_publishing(self):
        self.repository.save_document(self.sample_document)
        success = self.service.publish_document(self.sample_document.doc_id)
        
        self.assertTrue(success)
        documents = self.repository.get_all_documents()
        self.assertEqual(documents[0].status, DocumentStatus.PUBLISHED)

    def test_document_version_creation(self):
        self.repository.save_document(self.sample_document)
        new_doc = self.service.create_new_version(
            self.sample_document.doc_id, 
            "Новый автор", 
            "Изменения в документе"
        )
        
        self.assertIsNotNone(new_doc)
        self.assertEqual(new_doc.version, "1.1")
        self.assertEqual(new_doc.status, DocumentStatus.UPDATING)

    def test_document_search(self):
        documents = [
            Document(0, "Положение о деятельности", DocumentCategory.REGULATORY, 
                    DocumentStatus.PUBLISHED, "Иванов И.И.", "1.0"),
            Document(0, "Шаблон документа", DocumentCategory.TEMPLATES,
                    DocumentStatus.PUBLISHED, "Петров П.П.", "2.0"),
            Document(0, "Приказ №1", DocumentCategory.ORDERS,
                    DocumentStatus.APPROVED, "Сидоров С.С.", "1.0")
        ]
        
        for doc in documents:
            self.repository.save_document(doc)
        
        strategy = SimpleSearchStrategy()
        results = strategy.search(documents, "Положение")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Положение о деятельности")

    def test_advanced_document_search(self):
        documents = [
            Document(0, "Документ 1", DocumentCategory.REGULATORY, 
                    DocumentStatus.PUBLISHED, "Иванов", "1.0"),
            Document(0, "Документ 2", DocumentCategory.TEMPLATES,
                    DocumentStatus.DRAFT, "Петров", "1.0"),
            Document(0, "Документ 3", DocumentCategory.REGULATORY,
                    DocumentStatus.APPROVED, "Иванов", "2.0")
        ]
        
        strategy = AdvancedSearchStrategy()
        results = strategy.search(documents, 'status:опубликован author:Иванов')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Документ 1")

    def test_document_validation(self):
        is_valid, message = ValidationService.validate_document_data(
            "Валидное название", "Валидный автор"
        )
        self.assertTrue(is_valid)
        self.assertEqual(message, "")

    def test_invalid_document_validation(self):
        is_valid, message = ValidationService.validate_document_data("", "Автор")
        self.assertFalse(is_valid)
        self.assertIn("Название документа обязательно", message)
        
        is_valid, message = ValidationService.validate_document_data("Название", "")
        self.assertFalse(is_valid)
        self.assertIn("Автор документа обязателен", message)

    def test_document_filtering_by_category(self):
        documents = [
            Document(0, "Док 1", DocumentCategory.REGULATORY, DocumentStatus.PUBLISHED, "Автор 1", "1.0"),
            Document(0, "Док 2", DocumentCategory.TEMPLATES, DocumentStatus.PUBLISHED, "Автор 2", "1.0"),
            Document(0, "Док 3", DocumentCategory.REGULATORY, DocumentStatus.DRAFT, "Автор 3", "1.0")
        ]
        
        for doc in documents:
            self.repository.save_document(doc)
        
        regulatory_docs = self.service.get_documents_by_category(DocumentCategory.REGULATORY)
        self.assertEqual(len(regulatory_docs), 2)
        self.assertTrue(all(doc.category == DocumentCategory.REGULATORY for doc in regulatory_docs))

    def test_document_history(self):
        self.repository.save_document(self.sample_document)
        history = self.service.get_document_history(self.sample_document.doc_id)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].version, "1.0")

    def test_phone_validation(self):
        self.assertTrue(ValidationService.validate_phone("+7 (123) 456-7890"))
        self.assertTrue(ValidationService.validate_phone("1234567890"))
        self.assertFalse(ValidationService.validate_phone(""))
        self.assertFalse(ValidationService.validate_phone("abc"))

    def test_email_validation(self):
        self.assertTrue(ValidationService.validate_email("test@example.com"))
        self.assertTrue(ValidationService.validate_email("user.name@domain.co.uk"))
        self.assertFalse(ValidationService.validate_email("invalid-email"))
        self.assertFalse(ValidationService.validate_email("@domain.com"))

if __name__ == '__main__':
    unittest.main()