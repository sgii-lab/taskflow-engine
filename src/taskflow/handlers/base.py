from abc import ABC, abstractmethod
from typing import Any


class BaseHandler(ABC):
    """
    Abstract interface for all TaskFlow handlers.
    """

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the handler's operation.

        Returns:
            Any: The handler execution result.
        """
        raise NotImplementedError