import django_filters

from .models import Upload


class UploadFilter(django_filters.FilterSet):
    class Meta:
        model = Upload
        fields = ['email', 'first_name', 'last_name']
