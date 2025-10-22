import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
from models.document import Document
from models.enums import DocumentCategory, DocumentStatus
from services.document_service import DocumentService
from strategies.search_strategy import SimpleSearchStrategy, AdvancedSearchStrategy

class DocumentView:
    def __init__(self, root, document_service: DocumentService):
        self.root = root
        self.document_service = document_service
        self.current_search_strategy = SimpleSearchStrategy()
        
        self.setup_ui()
        self.load_documents()

    def setup_ui(self):
        self.root.title("Управление документами")
        self.root.geometry("1000x600")
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_documents())
        
        ttk.Button(search_frame, text="Найти", 
                  command=self.search_documents).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Расширенный поиск", 
                  command=self.toggle_advanced_search).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Новый документ", 
                  command=self.create_new_document).pack(side=tk.RIGHT, padx=5)
        
        self.advanced_frame = ttk.Frame(main_frame)
        
        self.setup_advanced_search()
        
        self.tree = ttk.Treeview(main_frame, columns=('name', 'category', 'status', 'author', 'version'), show='headings')
        self.tree.heading('name', text='Название')
        self.tree.heading('category', text='Категория')
        self.tree.heading('status', text='Статус')
        self.tree.heading('author', text='Автор')
        self.tree.heading('version', text='Версия')
        
        self.tree.column('name', width=200)
        self.tree.column('category', width=150)
        self.tree.column('status', width=120)
        self.tree.column('author', width=150)
        self.tree.column('version', width=80)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', self.on_document_double_click)

    def setup_advanced_search(self):
        ttk.Label(self.advanced_frame, text="Статус:").grid(row=0, column=0, padx=5, pady=2)
        self.status_combo = ttk.Combobox(self.advanced_frame, values=[s.value for s in DocumentStatus])
        self.status_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.advanced_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=2)
        self.category_combo = ttk.Combobox(self.advanced_frame, values=[c.value for c in DocumentCategory])
        self.category_combo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(self.advanced_frame, text="Автор:").grid(row=1, column=0, padx=5, pady=2)
        self.author_entry = ttk.Entry(self.advanced_frame)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(self.advanced_frame, text="Применить фильтры", 
                  command=self.apply_advanced_filters).grid(row=1, column=4, padx=5, pady=2)

    def load_documents(self):
        self.documents = self.document_service.get_all_documents()
        if not self.documents:
            self.create_sample_documents()
        self.display_documents(self.documents)

    def create_sample_documents(self):
        sample_docs = [
            Document(1, "Положение о дорожной деятельности", DocumentCategory.REGULATORY, 
                    DocumentStatus.PUBLISHED, "Иванов И.И.", "1.0"),
            Document(2, "Шаблон служебной записки", DocumentCategory.TEMPLATES,
                    DocumentStatus.PUBLISHED, "Петров П.П.", "2.1"),
            Document(3, "Приказ №123", DocumentCategory.ORDERS,
                    DocumentStatus.APPROVED, "Сидоров С.С.", "1.0"),
            Document(4, "Методика оценки проектов", DocumentCategory.REGULATORY,
                    DocumentStatus.DRAFT, "Козлов К.К.", "1.0")
        ]
        
        for doc in sample_docs:
            doc.description = f"Описание документа {doc.name}"
        
        self.documents = sample_docs

    def display_documents(self, documents: List[Document]):
        self.tree.delete(*self.tree.get_children())
        for doc in documents:
            self.tree.insert('', 'end', values=(
                doc.name, doc.category.value, doc.status.value, 
                doc.author, doc.version
            ))

    def search_documents(self):
        query = self.search_entry.get().strip()
        if not query:
            self.display_documents(self.documents)
            return
            
        results = self.current_search_strategy.search(self.documents, query)
        self.display_documents(results)

    def toggle_advanced_search(self):
        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
        else:
            self.advanced_frame.pack(fill=tk.X, padx=10, pady=5)
            self.current_search_strategy = AdvancedSearchStrategy()

    def apply_advanced_filters(self):
        search_params = {}
        
        if self.status_combo.get():
            search_params['status'] = self.status_combo.get()
        if self.category_combo.get():
            search_params['category'] = self.category_combo.get()
        if self.author_entry.get():
            search_params['author'] = self.author_entry.get()
            
        results = self.document_service.search_documents_advanced(search_params)
        self.display_documents(results)

    def create_new_document(self):
        from ui.modals import DocumentModal
        DocumentModal(self.root, self.document_service, self)

    def on_document_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            doc_name = item['values'][0]
            document = next((d for d in self.documents if d.name == doc_name), None)
            if document:
                from ui.modals import DocumentModal
                DocumentModal(self.root, self.document_service, self, document)

    def refresh_documents(self):
        self.load_documents()