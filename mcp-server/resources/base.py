from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class BaseResource(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def get_data(self) -> Any:
        pass
    
    def log_access(self, operation: str, details: Dict[str, Any] = None) -> None:
        log_data = {"resource": self.name, "operation": operation}
        if details:
            log_data.update(details)
        self.logger.info("Resource accessed", extra=log_data)