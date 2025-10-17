from django.core.exceptions import ValidationError
from rest_framework import permissions

from abstracts.permissions import IsObjPublic
from common.permissions import IsObjAdmin, IsObjOwner, partial_cls
from generic_status.permissions import HasObjRoles
from modules.models import Module

class ModuleCardsExporter:
    perms = [(IsObjPublic | IsObjAdmin | IsObjOwner | partial_cls(HasObjRoles, roles=['editor', 'viewer']))()]

    def __init__(self, module: Module):
        self.module = module

    def export_data(self):
        from cards.models import Card

        cards = Card.objects.filter(module=self.module)

        return [
            {
                'original': card.original,
                'translation': card.translation
            }
            for card in cards
        ]


class ModuleCardsImporter:
    perms = [permissions.IsAuthenticated()]

    def __init__(self, module: Module):
        self.module = module

    def import_data(self, data):
        from cards.models import Card

        cards_bulk = []
        for row in data:
            match row:
                case {"original": original, "translation": translation}:
                    cards_bulk.append(
                        Card(module=self.module, original=original, translation=translation)
                    )
                case _:
                    raise ValidationError(
                        "Each row must have both 'original' and 'translation' fields."
                    )

        if cards_bulk:
            Card.objects.bulk_create(cards_bulk)
