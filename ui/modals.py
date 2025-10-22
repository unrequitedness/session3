import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional
from models.project import Project
from models.document import Document
from models.enums import ProjectStatus, DocumentStatus, DocumentCategory
from services.project_service import ProjectService
from services.document_service import DocumentService
from services.validation_service import ValidationService

class ProjectCardModal:
    def __init__(self, parent, project: Project, project_service: ProjectService):
        self.modal = tk.Toplevel(parent)
        self.project = project
        self.project_service = project_service
        
        self.setup_modal()

    def setup_modal(self):
        self.modal.title(f"Карточка проекта - {self.project.name}")
        self.modal.geometry("600x500")
        self.modal.transient(self.modal.master)
        self.modal.grab_set()
        
        main_frame = ttk.Frame(self.modal)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text=self.project.name, 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="✕", 
                  command=self.modal.destroy).pack(side=tk.RIGHT)
        
        info_frame = ttk.LabelFrame(main_frame, text="Основная информация")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.create_info_rows(info_frame)
        
        progress_frame = ttk.LabelFrame(main_frame, text="Прогресс выполнения")
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text=f"Выполнено: {self.project.progress}%").pack(anchor="w")
        progress_bar = ttk.Progressbar(progress_frame, value=self.project.progress, maximum=100)
        progress_bar.pack(fill=tk.X, pady=5)
        
        deviation = self.project_service.calculate_project_deviation(self.project)
        if deviation:
            deviation_label = f"Отклонение от сроков: {deviation.days} дней"
            color = "red" if deviation.days > 0 else "green"
            ttk.Label(progress_frame, text=deviation_label, foreground=color).pack(anchor="w")
        
        documents_frame = ttk.LabelFrame(main_frame, text="Документы проекта")
        documents_frame.pack(fill=tk.X, pady=5)
        
        documents_list = ttk.Treeview(documents_frame, columns=('name', 'type'), show='tree', height=4)
        documents_list.heading('#0', text='Документы')
        documents_list.column('#0', width=200)
        documents_list.pack(fill=tk.X, padx=5, pady=5)
        
        for doc in self.project.documents:
            documents_list.insert('', 'end', text=doc.name)

    def create_info_rows(self, parent):
        rows = [
            ("Код проекта:", f"PRJ-{self.project.project_id:03d}"),
            ("Тип:", self.project.project_type.value),
            ("Статус:", self.project.status.value),
            ("Руководитель:", self.project.manager),
            ("Плановое начало:", self.project.start_date.strftime('%d.%m.%Y')),
            ("Плановое окончание:", self.project.end_date.strftime('%d.%m.%Y')),
        ]
        
        if self.project.actual_start:
            rows.append(("Фактическое начало:", self.project.actual_start.strftime('%d.%m.%Y')))
        if self.project.actual_end:
            rows.append(("Фактическое окончание:", self.project.actual_end.strftime('%d.%m.%Y')))
        
        for i, (label, value) in enumerate(rows):
            ttk.Label(parent, text=label, font=("Arial", 9, "bold")).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(parent, text=value).grid(row=i, column=1, sticky="w", padx=5, pady=2)

class ProjectStageModal:
    def __init__(self, parent, stage_name: str):
        self.modal = tk.Toplevel(parent)
        self.stage_name = stage_name
        self.setup_modal()

    def setup_modal(self):
        self.modal.title(f"Сетевой график - {self.stage_name}")
        self.modal.geometry("800x600")
        
        main_frame = ttk.Frame(self.modal)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text=f"Сетевой график этапа: {self.stage_name}", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        canvas = tk.Canvas(main_frame, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_network_graph(canvas)

    def draw_network_graph(self, canvas):
        tasks = [
            ("Анализ требований", 5),
            ("Проектирование", 7),
            ("Разработка", 14),
            ("Тестирование", 5),
            ("Внедрение", 3)
        ]
        
        x, y = 50, 50
        for i, (task, duration) in enumerate(tasks):
            canvas.create_rectangle(x, y, x + 120, y + 40, fill="lightblue", outline="black")
            canvas.create_text(x + 60, y + 20, text=f"{task}\n{duration} дн.")
            
            if i < len(tasks) - 1:
                canvas.create_line(x + 120, y + 20, x + 150, y + 20, arrow=tk.LAST)
            
            y += 80

class DocumentModal:
    def __init__(self, parent, document_service: DocumentService, document_view, document: Document = None):
        self.modal = tk.Toplevel(parent)
        self.document_service = document_service
        self.document_view = document_view
        self.document = document
        self.is_edit = document is None
        
        self.setup_modal()

    def setup_modal(self):
        title = "Новый документ" if self.is_edit else f"Документ - {self.document.name}"
        self.modal.title(title)
        self.modal.geometry("500x400")
        self.modal.transient(self.modal.master)
        self.modal.grab_set()
        
        main_frame = ttk.Frame(self.modal)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Название документа:").pack(anchor="w", pady=2)
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(main_frame, text="Категория:").pack(anchor="w", pady=2)
        self.category_combo = ttk.Combobox(main_frame, values=[c.value for c in DocumentCategory])
        self.category_combo.pack(fill=tk.X, pady=2)
        
        ttk.Label(main_frame, text="Автор:").pack(anchor="w", pady=2)
        self.author_entry = ttk.Entry(main_frame, width=50)
        self.author_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(main_frame, text="Описание:").pack(anchor="w", pady=2)
        self.desc_text = tk.Text(main_frame, height=4, width=50)
        self.desc_text.pack(fill=tk.X, pady=2)
        
        if not self.is_edit:
            ttk.Label(main_frame, text="Статус:").pack(anchor="w", pady=2)
            self.status_combo = ttk.Combobox(main_frame, values=[s.value for s in DocumentStatus])
            self.status_combo.pack(fill=tk.X, pady=2)
            self.status_combo.set(self.document.status.value)
            
            ttk.Label(main_frame, text=f"Версия: {self.document.version}").pack(anchor="w", pady=2)
        
        if self.document:
            self.name_entry.insert(0, self.document.name)
            self.category_combo.set(self.document.category.value)
            self.author_entry.insert(0, self.document.author)
            self.desc_text.insert('1.0', self.document.description)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        if self.is_edit:
            ttk.Button(button_frame, text="Создать", command=self.create_document).pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Button(button_frame, text="Сохранить", command=self.update_document).pack(side=tk.RIGHT, padx=5)
            if self.document.status == DocumentStatus.DRAFT:
                ttk.Button(button_frame, text="Опубликовать", command=self.publish_document).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Отмена", command=self.modal.destroy).pack(side=tk.RIGHT, padx=5)

    def create_document(self):
        name = self.name_entry.get().strip()
        category_name = self.category_combo.get()
        author = self.author_entry.get().strip()
        description = self.desc_text.get('1.0', 'end-1c').strip()
        
        is_valid, message = ValidationService.validate_document_data(name, author)
        if not is_valid:
            messagebox.showerror("Ошибка", message)
            return
        
        try:
            category = next(c for c in DocumentCategory if c.value == category_name)
            document = self.document_service.create_document(name, category, author)
            document.description = description
            self.document_service.repository.save_document(document)
            
            messagebox.showinfo("Успех", "Документ создан успешно")
            self.modal.destroy()
            self.document_view.refresh_documents()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании документа: {str(e)}")

    def update_document(self):
        if not self.document:
            return
            
        self.document.name = self.name_entry.get().strip()
        self.document.author = self.author_entry.get().strip()
        self.document.description = self.desc_text.get('1.0', 'end-1c').strip()
        
        try:
            self.document.status = next(s for s in DocumentStatus if s.value == self.status_combo.get())
            self.document_service.repository.save_document(self.document)
            
            messagebox.showinfo("Успех", "Документ обновлен успешно")
            self.modal.destroy()
            self.document_view.refresh_documents()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении документа: {str(e)}")

    def publish_document(self):
        if self.document and self.document_service.publish_document(self.document.doc_id):
            messagebox.showinfo("Успех", "Документ опубликован")
            self.modal.destroy()
            self.document_view.refresh_documents()
        else:
            messagebox.showerror("Ошибка", "Не удалось опубликовать документ")