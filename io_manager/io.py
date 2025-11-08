from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from rest_framework.permissions import BasePermission
    from django.db.models import Model


class BaseStrategy(ABC):
    def __init__(self, model: Model) -> None:
        self.model = model

    perms: list[BasePermission] = []


class ImportStrategy(BaseStrategy, ABC):
    @abstractmethod
    def import_data(self, data: list[dict[str, Any]]) -> None: ...


class ExportStrategy(BaseStrategy, ABC):
    @abstractmethod
    def export_data(self) -> list[dict[str, Any]]: ...
