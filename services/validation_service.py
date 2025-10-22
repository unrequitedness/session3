import re
from datetime import datetime, date
from typing import Tuple, Optional

class ValidationService:
    @staticmethod
    def validate_phone(phone: str) -> bool:
        pattern = r'^[0-9+\(\)\- #]{1,20}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_dates(start_date: date, end_date: date) -> Tuple[bool, str]:
        if start_date > end_date:
            return False, "Дата начала не может быть позже даты окончания"
        if start_date < date.today():
            return False, "Дата начала не может быть в прошлом"
        return True, ""

    @staticmethod
    def validate_project_dates(planned_start: date, planned_end: date, 
                             actual_start: Optional[date], actual_end: Optional[date]) -> Tuple[bool, str]:
        if planned_start > planned_end:
            return False, "Плановые даты некорректны"
        if actual_start and actual_end:
            if actual_start > actual_end:
                return False, "Фактические даты некорректны"
        return True, ""

    @staticmethod
    def validate_document_data(name: str, author: str) -> Tuple[bool, str]:
        if not name or len(name.strip()) == 0:
            return False, "Название документа обязательно"
        if not author or len(author.strip()) == 0:
            return False, "Автор документа обязателен"
        if len(name) > 200:
            return False, "Название документа слишком длинное"
        return True, ""