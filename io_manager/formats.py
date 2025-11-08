from __future__ import annotations

import csv
import io
from abc import ABC, abstractmethod
from typing import BinaryIO, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import Type, Any


class BaseFormat(ABC):
    name: str | None = None
    mime: str | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.name:
            FormatRegistry.register(cls.name, cls)

    @staticmethod
    @abstractmethod
    def read(file: BinaryIO, **kwargs: Any) -> list[dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def write(data: list[dict[str, Any]], **kwargs: Any) -> bytes: ...


class FormatRegistry:
    _formats: dict[str, Type[BaseFormat]] = {}

    @classmethod
    def register(cls, name: str, format_cls: Type[BaseFormat]) -> None:
        cls._formats[name] = format_cls

    @classmethod
    def get(cls, name: str) -> BaseFormat:
        if name not in cls._formats:
            raise ValueError(f"Format {name} not registered")
        return cls._formats[name]()


class CSVFormat(BaseFormat):
    name = "csv"
    mime = "text/csv"

    @staticmethod
    def read(file: BinaryIO, encoding: str = "utf-8") -> list[dict[str, Any]]:
        try:
            raw = file.read()
            if isinstance(raw, bytes):
                decoded = raw.decode(encoding)
            else:
                decoded = str(raw)
            reader = csv.DictReader(io.StringIO(decoded))
            return [row for row in reader]
        except Exception as e:
            raise ValueError(f"CSV read error: {e}")

    @staticmethod
    def write(data: list[dict[str, Any]], encoding: str = "utf-8") -> bytes:
        output = io.StringIO()
        if data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return output.getvalue().encode(encoding)


class XLSXFormat(BaseFormat):
    name = "xlsx"
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    @staticmethod
    def read(file: BinaryIO, sheet_name: int = 0) -> list[dict[str, Any]]:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            return df.to_dict(orient="records")
        except Exception as e:
            raise ValueError(f"XLSX read error: {e}")

    @staticmethod
    def write(data: list[dict[str, Any]], sheet_name: str = "Sheet1") -> bytes:
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        return output.getvalue()
