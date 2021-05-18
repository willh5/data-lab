import django_filters
from .models import *
from django_filters import DateFilter



class LocationFilter(django_filters.FilterSet):
    class Meta:
        model = Location
        fields = '__all__'


class DataFilter(django_filters.FilterSet):
    start_date=DateFilter(field_name="start", lookup_expr='gte')
    end_date=DateFilter(field_name="end", lookup_expr='lte')

    class Meta:
        model = Data
        fields = '__all__'
        exclude = ['timescale', 'value', 'start', 'end']