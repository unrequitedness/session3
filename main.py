import tkinter as tk
from tkinter import ttk
from repositories.project_repository import ProjectRepository
from repositories.document_repository import DocumentRepository
from services.project_service import ProjectService
from services.document_service import DocumentService
from ui.project_view import ProjectView
from ui.document_view import DocumentView

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.setup_app()
        
        self.project_repository = ProjectRepository("projects.db")
        self.document_repository = DocumentRepository("documents.db")
        
        self.project_service = ProjectService(self.project_repository)
        self.document_service = DocumentService(self.document_repository)
        
        self.setup_ui()

    def setup_app(self):
        self.root.title("Система управления проектами и документами")
        self.root.geometry("1200x700")
        
        style = ttk.Style()
        style.theme_use('clam')

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        project_frame = ttk.Frame(self.notebook)
        document_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(project_frame, text="Управление проектами")
        self.notebook.add(document_frame, text="Управление документами")
        
        self.project_view = ProjectView(project_frame, self.project_service)
        self.document_view = DocumentView(document_frame, self.document_service)
        
        self.setup_menu()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Проекты", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Документы", command=lambda: self.notebook.select(1))
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def show_about(self):
        about_text = """
Система управления проектами и документами
Версия 1.0

Функциональность:
- Управление инвестиционными и корпоративными проектами
- Управление корпоративными документами
- Система согласования документов
- Отслеживание прогресса проектов
        """
        tk.messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()