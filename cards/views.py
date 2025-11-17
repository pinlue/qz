from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from cards.filters import CardFilter
from cards.models import Card
from cards.pagination import CardPagination
from cards.serializers import CardSerializer
from cards.service import CardService
from common.decorators import swagger_safe_permissions
from common.exeptions import UnRegisteredPolicy
from common.policy import PolicyRegistry
from generic_status.views import LearnMixin
from interactions.views import SaveMixin

if TYPE_CHECKING:
    from typing import Any
    from rest_framework.request import Request
    from rest_framework.permissions import BasePermission
    from django.db.models import QuerySet


@extend_schema(tags=["cards"])
class CardViewSet(SaveMixin, LearnMixin, viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter
    pagination_class = CardPagination
    serializer_class = CardSerializer
    policies = PolicyRegistry()
    service = CardService()

    def list(
        self, request: Request, module_pk: str | None = None, *args: Any, **kwargs: Any
    ) -> Response:
        data = self.service.get_cards_with_saved(
            module_id=int(module_pk), user=self.request.user
        )
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)

    def get_queryset(self) -> QuerySet[Card]:
        return Card.objects.filter(module_id=self.kwargs.get("module_pk"))

    @swagger_safe_permissions
    def get_permissions(self) -> list[BasePermission]:
        try:
            return [perm() for perm in self.policies.get(self.action)]
        except UnRegisteredPolicy:
            pass
        return super().get_permissions()

    def perform_create(self, serializer: CardSerializer) -> None:
        if not (module_pk := self.kwargs.get("module_pk")):
            raise ValidationError('Missing "module_pk" parameter in URL')
        serializer.save(module_id=module_pk)
