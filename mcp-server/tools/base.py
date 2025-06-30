from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        pass
    
    def log_execution(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        log_data = {"tool": self.name, "operation": operation}
        if details:
            log_data.update(details)
        self.logger.info("Tool execution", extra=log_data)