import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Callable, List

class StatusBadge(ttk.Frame):
    def __init__(self, parent, status: str, color: str):
        super().__init__(parent)
        self.status_label = ttk.Label(self, text=status, background=color, 
                                    foreground="white", padding=2, borderwidth=1, relief="solid")
        self.status_label.pack()

class ProgressWidget(ttk.Frame):
    def __init__(self, parent, progress: int, show_percentage: bool = True):
        super().__init__(parent)
        self.progress_bar = ttk.Progressbar(self, value=progress, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        if show_percentage:
            self.percentage_label = ttk.Label(self, text=f"{progress}%")
            self.percentage_label.pack(side=tk.RIGHT)

class DateRangeWidget(ttk.Frame):
    def __init__(self, parent, on_date_change: Callable = None):
        super().__init__(parent)
        self.on_date_change = on_date_change
        
        ttk.Label(self, text="С:").pack(side=tk.LEFT)
        self.start_date = ttk.Entry(self, width=10)
        self.start_date.pack(side=tk.LEFT, padx=5)
        self.start_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Label(self, text="По:").pack(side=tk.LEFT, padx=(10, 0))
        self.end_date = ttk.Entry(self, width=10)
        self.end_date.pack(side=tk.LEFT, padx=5)
        self.end_date.insert(0, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        
        if on_date_change:
            self.start_date.bind('<FocusOut>', self._on_date_change)
            self.end_date.bind('<FocusOut>', self._on_date_change)

    def _on_date_change(self, event):
        if self.on_date_change:
            self.on_date_change()

    def get_dates(self) -> tuple:
        try:
            start = datetime.strptime(self.start_date.get(), '%Y-%m-%d')
            end = datetime.strptime(self.end_date.get(), '%Y-%m-%d')
            return start, end
        except ValueError:
            return None, None

class FilterWidget(ttk.Frame):
    def __init__(self, parent, filters: List[str], on_filter_change: Callable):
        super().__init__(parent)
        self.on_filter_change = on_filter_change
        self.filter_vars = {}
        
        ttk.Label(self, text="Фильтры:").pack(side=tk.LEFT)
        
        for filter_name in filters:
            var = tk.BooleanVar(value=True)
            self.filter_vars[filter_name] = var
            
            cb = ttk.Checkbutton(self, text=filter_name, variable=var, 
                               command=self._on_filter_change)
            cb.pack(side=tk.LEFT, padx=5)

    def _on_filter_change(self):
        if self.on_filter_change:
            active_filters = [name for name, var in self.filter_vars.items() if var.get()]
            self.on_filter_change(active_filters)

    def get_active_filters(self) -> List[str]:
        return [name for name, var in self.filter_vars.items() if var.get()]

class SearchBox(ttk.Frame):
    def __init__(self, parent, on_search: Callable, placeholder: str = "Поиск..."):
        super().__init__(parent)
        self.on_search = on_search
        
        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.search_var, width=40)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.insert(0, placeholder)
        
        self.search_button = ttk.Button(self, text="Найти", command=self._perform_search)
        self.search_button.pack(side=tk.RIGHT)
        
        self.entry.bind('<Return>', lambda e: self._perform_search())

    def _perform_search(self):
        if self.on_search:
            self.on_search(self.search_var.get())

class PaginationWidget(ttk.Frame):
    def __init__(self, parent, total_items: int, page_size: int, on_page_change: Callable):
        super().__init__(parent)
        self.total_items = total_items
        self.page_size = page_size
        self.on_page_change = on_page_change
        self.current_page = 1
        
        self.setup_pagination()

    def setup_pagination(self):
        total_pages = max(1, (self.total_items + self.page_size - 1) // self.page_size)
        
        self.prev_button = ttk.Button(self, text="←", width=3,
                                    command=lambda: self.change_page(self.current_page - 1))
        self.prev_button.pack(side=tk.LEFT, padx=2)
        
        self.page_label = ttk.Label(self, text=f"{self.current_page} / {total_pages}")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(self, text="→", width=3,
                                    command=lambda: self.change_page(self.current_page + 1))
        self.next_button.pack(side=tk.LEFT, padx=2)
        
        self.update_buttons()

    def change_page(self, new_page: int):
        total_pages = max(1, (self.total_items + self.page_size - 1) // self.page_size)
        if 1 <= new_page <= total_pages:
            self.current_page = new_page
            self.page_label.config(text=f"{self.current_page} / {total_pages}")
            self.update_buttons()
            
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def update_buttons(self):
        total_pages = max(1, (self.total_items + self.page_size - 1) // self.page_size)
        self.prev_button.state(['!disabled' if self.current_page > 1 else 'disabled'])
        self.next_button.state(['!disabled' if self.current_page < total_pages else 'disabled'])