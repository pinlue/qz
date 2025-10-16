from django.core.exceptions import ValidationError

from modules.models import Module

class ModuleCardsExporter:
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
