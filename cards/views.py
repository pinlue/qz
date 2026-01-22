from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from cards.filters import CardFilter
from cards.models import Card
from cards.pagination import CardPagination
from cards.serializers import CardSerializer, CardCreateSerializer
from common.decorators import swagger_safe_permissions
from common.exeptions import UnRegisteredPolicy
from common.policy import PolicyRegistry
from generic_status.views import LearnMixin
from interactions.views import SaveMixin

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission
    from django.db.models import QuerySet


@extend_schema(tags=["cards"])
class CardViewSet(SaveMixin, LearnMixin, viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter
    pagination_class = CardPagination
    saves_serializer_class = CardSerializer
    policies = PolicyRegistry()

    def get_queryset(self) -> QuerySet[Card]:
        return Card.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CardCreateSerializer
        elif self.action in {"retrieve", "list", "update", "partial_update"}:
            return CardSerializer
        return super().get_serializer_class()

    @swagger_safe_permissions
    def get_permissions(self) -> list[BasePermission]:
        try:
            return [perm() for perm in self.policies.get(self.action)]
        except UnRegisteredPolicy:
            pass
        return super().get_permissions()
