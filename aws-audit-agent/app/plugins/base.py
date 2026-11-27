from abc import ABC, abstractmethod
from app.models import AuditContext, Evidence

class AuditPlugin(ABC):
    name: str
    @abstractmethod
    def collect(self, context: AuditContext) -> list[Evidence]:
        raise NotImplementedError
