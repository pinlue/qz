from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from io_manager.bridge import ModelIOBridge
from io_manager.formats import FormatRegistry


class GenericImportView(APIView):
    parser_classes = [MultiPartParser]
    strategy = None
    model = None

    def post(self, request, pk=None):
        if not self.strategy or not self.model:
            return Response({"detail": "Strategy or model not defined."}, status=500)

        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=400)

        instance = get_object_or_404(self.model, pk=pk) if pk else None

        ext = file.name.split(".")[-1].lower()
        file_format = FormatRegistry.get(ext)
        if not file_format:
            return Response({"detail": f"Unsupported file format: {ext}"}, status=400)

        try:
            strategy = self.strategy(instance)
            bridge = ModelIOBridge(strategy, file_format)
            bridge.import_file(file)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        return Response({"detail": "Import successful."}, status=200)


class GenericExportView(APIView):
    strategy = None
    model = None

    def get(self, request, pk=None):
        if not self.strategy:
            return Response(
                {"detail": "Strategy not defined."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        fmt = request.query_params.get("file_format", "csv")

        file_format = FormatRegistry.get(fmt)
        if not file_format:
            return Response(
                {"detail": f"Unsupported format '{fmt}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = get_object_or_404(self.model, pk=pk)

        try:
            strategy = self.strategy(instance)
            bridge = ModelIOBridge(strategy, file_format)
            file_content = bridge.export_file()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        content_type = (
            "text/csv"
            if fmt == "csv"
            else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response = HttpResponse(file_content, content_type=content_type)
        filename = f"{self.model.__name__.lower()}_export.{fmt}"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
