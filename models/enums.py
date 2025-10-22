from enum import Enum

class ProjectStatus(Enum):
    CREATED = "Создан"
    PLANNED = "Запланирован"
    IN_PROGRESS = "В процессе"
    APPROVAL = "На согласовании"
    APPROVAL_WAITING = "На утверждении"
    VERIFICATION = "На проверке"
    REQUIRES_REFINEMENT = "Требует доработки"
    FROZEN = "Заморожен"
    COMPLETED = "Завершен"
    CLOSED = "Закрыт"
    ARCHIVED = "Архивирован"
    CANCELLED = "Отменен"

class ProjectType(Enum):
    INVESTMENT = "Инвестиционный"
    CORPORATE = "Корпоративный"

class DocumentStatus(Enum):
    DRAFT = "Черновик"
    APPROVAL = "На согласовании"
    APPROVED = "Согласован"
    APPROVAL_WAITING = "На утверждении"
    APPROVED_FINAL = "Утвержден"
    PUBLISHED = "Опубликован"
    ARCHIVED = "В архиве"
    RECALLED = "Отозван"
    VERIFICATION = "На проверке"
    REFINEMENT = "На доработке"
    UPDATING = "На обновлении"
    UPDATED = "Обновлен"
    DELETED = "Удален"
    EXPIRED = "Истекший срок действия"
    PUBLICATION_WAITING = "Ожидание публикации"

class DocumentCategory(Enum):
    REGULATORY = "Регламентирующие документы"
    ARCHIVE = "Архив"
    ORDERS = "Приказы и распоряжения"
    TRAINING = "Материалы по обучениям"
    TEMPLATES = "Шаблоны"
    MEMOS = "Служебные записки"

class RouteStatus(Enum):
    DRAFT = "Черновик"
    APPROVAL = "На согласовании"
    EDITING = "На редактировании"
    REJECTED = "Отклонена"
    APPROVED = "Утверждена"
    ACTIVE = "Введена в действие"