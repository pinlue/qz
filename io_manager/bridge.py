from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, BinaryIO
    from io_manager.formats import BaseFormat
    from io_manager.io import ImportStrategy, ExportStrategy


class ModelIOBridge:
    def __init__(
        self, strategy: ImportStrategy | ExportStrategy, file_format: BaseFormat
    ) -> None:
        self.strategy = strategy
        self.file_format: BaseFormat = file_format

    def import_file(self, file: BinaryIO) -> None:
        if not hasattr(self.strategy, "import_data"):
            raise TypeError("This strategy does not support import")
        data: list[dict[str, Any]] = self.file_format.read(file)
        self.strategy.import_data(data)

    def export_file(self) -> bytes:
        if not hasattr(self.strategy, "export_data"):
            raise TypeError("This strategy does not support export")
        data: list[dict[str, Any]] = self.strategy.export_data()
        return self.file_format.write(data)
