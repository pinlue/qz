import csv
import io
from typing import BinaryIO

import pandas as pd


class FormatRegistry:
    _formats = {}

    @classmethod
    def register(cls, name, format_cls):
        cls._formats[name] = format_cls

    @classmethod
    def get(cls, name):
        return cls._formats[name]()


class BaseFormat:
    name = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name:
            FormatRegistry.register(cls.name, cls)


class CSVFormat(BaseFormat):
    name = "csv"

    @staticmethod
    def read(file: BinaryIO, encoding: str = 'utf-8') -> list[dict[str, str]]:
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
    def write(data: list[dict], encoding: str = 'utf-8') -> bytes:
        output = io.StringIO()
        if data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return output.getvalue().encode(encoding)


class XLSXFormat(BaseFormat):
    name = "xlsx"

    @staticmethod
    def read(file: BinaryIO, sheet_name=0) -> list[dict]:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            return df.to_dict(orient='records')
        except Exception as e:
            raise ValueError(f"XLSX read error: {e}")

    @staticmethod
    def write(data: list[dict], sheet_name='Sheet1') -> bytes:
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        return output.getvalue()
