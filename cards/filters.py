import django_filters

from cards.models import Card


class CardFilter(django_filters.FilterSet):
    original = django_filters.CharFilter(
        field_name="original",
        lookup_expr="icontains",
    )
    translation = django_filters.CharFilter(
        field_name="translation",
        lookup_expr="icontains",
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("original", "original"),
            ("translation", "translation"),
            ("created", "created"),
        )
    )

    class Meta:
        model = Card
        fields = ["original", "translation"]
