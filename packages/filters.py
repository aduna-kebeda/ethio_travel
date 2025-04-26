from django_filters import rest_framework as filters
from django_filters.filters import CharFilter
from .models import Package

class JSONFieldFilter(CharFilter):
    def filter(self, qs, value):
        if value not in (None, ''):
            return qs.filter(**{f"{self.field_name}__contains": value})
        return qs

class PackageFilter(filters.FilterSet):
    category = JSONFieldFilter()
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    region = filters.CharFilter(lookup_expr='icontains')
    difficulty = filters.ChoiceFilter(choices=Package.DIFFICULTY_CHOICES)
    status = filters.ChoiceFilter(choices=Package.STATUS_CHOICES)

    class Meta:
        model = Package
        fields = ['category', 'region', 'featured', 'difficulty', 'status', 'min_price', 'max_price']
        filter_overrides = {
            'JSONField': {
                'filter_class': JSONFieldFilter,
            },
        } 