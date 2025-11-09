from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from rest_framework import permissions

from abstracts.permissions import IsObjPublic
from common.permissions import IsObjAdmin, IsObjOwner, partial_cls
from generic_status.permissions import HasObjRoles
from io_manager.io import ExportStrategy, ImportStrategy

if TYPE_CHECKING:
    from typing import Any
    from rest_framework.permissions import BasePermission


class ModuleCardsExporter(ExportStrategy):
    perms: list[BasePermission] = [
        (
            IsObjPublic
            | IsObjAdmin
            | IsObjOwner
            | partial_cls(HasObjRoles, roles=["editor", "viewer"])
        )()
    ]

    def export_data(self) -> list[dict[str, str]]:
        from cards.models import Card

        cards = Card.objects.filter(module=self.model)
        return [
            {"original": card.original, "translation": card.translation}
            for card in cards
        ]


class ModuleCardsImporter(ImportStrategy):
    perms: list[BasePermission] = [permissions.IsAuthenticated()]

    def import_data(self, data: list[dict[str, Any]]) -> None:
        from cards.models import Card

        cards_bulk: list[Card] = []
        for row in data:
            match row:
                case {"original": original, "translation": translation}:
                    cards_bulk.append(
                        Card(
                            module=self.model,
                            original=original,
                            translation=translation,
                        )
                    )
                case _:
                    raise ValidationError(
                        'Each row must have both "original" and "translation" fields.'
                    )

        if cards_bulk:
            Card.objects.bulk_create(cards_bulk)
