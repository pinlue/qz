import django_filters

from folders.models import Folder


class FolderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    modules_count__gt = django_filters.NumberFilter(
        field_name="modules_count", lookup_expr="gt"
    )
    modules_count__lt = django_filters.NumberFilter(
        field_name="modules_count", lookup_expr="lt"
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("created", "created"),
            (
                "modules_count",
                "modules_count",
            ),
        )
    )

    class Meta:
        model = Folder
        fields = ["name"]
