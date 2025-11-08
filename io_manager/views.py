from __future__ import annotations

import io
from typing import TYPE_CHECKING

from django.http import FileResponse
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from io_manager.bridge import ModelIOBridge
from io_manager.formats import FormatRegistry

if TYPE_CHECKING:
    from io_manager.io import ImportStrategy, ExportStrategy
    from django.db.models import Model
    from typing import Type
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "format": "binary"},
            },
            "required": ["file"],
        }
    },
    responses={
        200: OpenApiResponse(description="Import successful"),
        400: OpenApiResponse(description="Invalid format or import error"),
        404: OpenApiResponse(description="Object not found"),
        500: OpenApiResponse(description="Strategy or model not defined"),
    },
)
class GenericImportView(APIView):
    parser_classes = [MultiPartParser]
    strategy: Type[ImportStrategy] | None = None
    model: Type[Model] | None = None

    def post(self, request: Request, pk: int | None = None) -> Response:
        if not self.strategy or not self.model:
            return Response({"detail": "Strategy or model not defined"}, status=500)

        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided"}, status=400)

        instance = get_object_or_404(self.model, pk=pk) if pk else None

        self.check_object_permissions(request, instance)

        ext = file.name.split(".")[-1].lower()
        file_format = FormatRegistry.get(ext)
        if not file_format:
            return Response({"detail": f"Unsupported file format: {ext}"}, status=400)

        try:
            strategy = self.strategy(instance)
            bridge = ModelIOBridge(strategy, file_format)
            bridge.import_file(file)
        except Exception:
            return Response(
                {"detail": "An unexpected error occurred. Please contact support."},
                status=500,
            )

        return Response({"detail": "Import successful"}, status=200)

    def get_permissions(self) -> list[BasePermission]:
        return self.strategy.perms


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="file_format",
            description="File format to export data as (`csv` or `xlsx`).",
            required=False,
            type=str,
            examples=[
                OpenApiExample("CSV format", value="csv"),
                OpenApiExample("Excel format", value="xlsx"),
            ],
        ),
    ],
    responses={
        200: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "CSV Example",
                    value="original,translation\nHello,Hi\nBye,Goodbye",
                ),
            ],
        ),
        400: OpenApiResponse(description="Invalid format or export error"),
        404: OpenApiResponse(description="Object not found"),
        500: OpenApiResponse(description="Strategy not defined"),
    },
)
class GenericExportView(APIView):
    strategy: Type[ExportStrategy] | None = None
    model: Type[Model] | None = None

    def get(self, request: Request, pk: int | None = None) -> Response | FileResponse:
        if not self.strategy:
            return Response(
                {"detail": "Strategy not defined."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        fmt = request.query_params.get("file_format", "csv")

        file_format = FormatRegistry.get(fmt.lower())
        if not file_format:
            return Response(
                {"detail": f"Unsupported format '{fmt}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = get_object_or_404(self.model, pk=pk)

        self.check_object_permissions(request, instance)

        try:
            strategy = self.strategy(instance)
            bridge = ModelIOBridge(strategy, file_format)
            file_content = bridge.export_file()
        except Exception:
            return Response(
                {"detail": "An unexpected error occurred. Please contact support."},
                status=500,
            )

        filename = f"{self.model.__name__.lower()}_export.{fmt}"

        return FileResponse(
            io.BytesIO(file_content),
            as_attachment=True,
            filename=filename,
            content_type=file_format.mime,
        )

    def get_permissions(self) -> list[BasePermission]:
        return self.strategy.perms
