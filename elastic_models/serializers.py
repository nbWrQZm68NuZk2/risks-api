from rest_framework import serializers

from elastic_models.models import Instance, Schema, FieldDefinition


class FieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = ['name', 'label', 'type', 'blank', 'choices']

    choices = serializers.JSONField()


class SchemaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schema
        fields = ['id', 'name', 'name_plural', 'field_definitions']

    field_definitions = FieldDefinitionSerializer(many=True)


class SchemaListSerializer(SchemaDetailSerializer):
    class Meta(SchemaDetailSerializer.Meta):
        fields = ['id', 'name']


def serializer_class_factory(schema):
    """ Creates serializer class corresponding to given schema """

    static_fields = ['id', 'updated_at', 'created_at']
    schema_based_fields = list(schema.field_definitions.values_list('name', flat=True))

    class Meta:
        fields = static_fields + schema_based_fields
        read_only_fields = ['id']
        model = Instance

    class_name = str('{}Serializer'.format(schema.name.title()))
    bases = (serializers.ModelSerializer,)
    attributes = {'Meta': Meta, }

    return type(class_name, bases, attributes)
