import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(field_name='salary', lookup_expr='gte')
    max_salary = django_filters.NumberFilter(field_name='salary', lookup_expr='lte')
    location__city = django_filters.CharFilter(field_name='location__city', lookup_expr='icontains')
    location__country = django_filters.CharFilter(field_name='location__country', lookup_expr='icontains')

    class Meta:
        model = Job
        fields = [
            'job_type',
            'experience_level',
            'location__city',
            'location__country',
            'min_salary',
            'max_salary',
        ]