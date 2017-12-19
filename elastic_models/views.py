from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from elastic_models.models import Schema, Instance, schema_loaded
from elastic_models.serializers import serializer_class_factory, SchemaDetailSerializer, SchemaListSerializer


class SchemaViewSet(ReadOnlyModelViewSet):
    """ Lists and retrieves schemas """

    queryset = Schema.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SchemaDetailSerializer
        else:
            return SchemaListSerializer


class LoadSchemaMixin(object):
    """ Loads schema based on `schema_name_plural` url argument """

    def dispatch(self, request, *args, **kwargs):
        self.schema = get_object_or_404(Schema, name_plural=kwargs['schema_name_plural'])
        with schema_loaded(self.schema):
            return super().dispatch(request, *args, **kwargs)


class InstanceViewSet(LoadSchemaMixin, ModelViewSet):
    """ Lists, creates and retrieves instances for multiple per-schema endpoints """

    def get_serializer_class(self):
        return serializer_class_factory(self.schema)

    def get_queryset(self):
        return Instance.objects.filter(schema=self.schema)

    def perform_create(self, serializer):
        serializer.save(schema=self.schema)
