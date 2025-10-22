from abc import ABC, abstractmethod
from typing import List, Dict
from models.document import Document
from models.enums import DocumentStatus

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, documents: List[Document], query: str) -> List[Document]:
        pass

class SimpleSearchStrategy(SearchStrategy):
    def search(self, documents: List[Document], query: str) -> List[Document]:
        query = query.lower()
        results = []
        for doc in documents:
            if (query in doc.name.lower() or 
                query in doc.author.lower() or 
                query in doc.description.lower()):
                results.append(doc)
        return results

class AdvancedSearchStrategy(SearchStrategy):
    def search(self, documents: List[Document], query: str) -> List[Document]:
        if not query:
            return documents
            
        operators = self._parse_operators(query)
        results = documents
        
        if 'status:' in operators:
            status_value = operators['status:'].upper()
            results = [d for d in results if d.status.value.upper() == status_value]
            
        if 'author:' in operators:
            author_value = operators['author:'].lower()
            results = [d for d in results if author_value in d.author.lower()]
            
        if 'category:' in operators:
            category_value = operators['category:'].lower()
            results = [d for d in results if category_value in d.category.value.lower()]
            
        simple_query = operators.get('simple', '')
        if simple_query:
            simple_strategy = SimpleSearchStrategy()
            results = simple_strategy.search(results, simple_query)
            
        return results

    def _parse_operators(self, query: str) -> Dict[str, str]:
        operators = {}
        parts = query.split()
        simple_parts = []
        
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                operators[key.lower() + ':'] = value.strip('"\'')
            else:
                simple_parts.append(part)
                
        if simple_parts:
            operators['simple'] = ' '.join(simple_parts)
            
        return operators