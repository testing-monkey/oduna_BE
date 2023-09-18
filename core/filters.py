from django_filters import rest_framework as filters


class CoreFilterBackend(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()
    updated = filters.DateFromToRangeFilter("updated_at")

    class Meta:
        exclude = ["is_deleted", "deleted_at", "updated_at"]

   