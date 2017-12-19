from datetime import date
from rest_framework import status
from rest_framework.test import APITestCase

from elastic_models.models import Schema, Instance, schema_loaded
from elastic_models.serializers import FieldDefinitionSerializer

AQUARIUM_FIELD_DEFINITIONS = [{
        'name': 'volume',
        'type': 'number',
    },
    {
        'name': 'temperature',
        'type': 'number',
        'blank': True
    },
    {
        'name': 'water',
        'type': 'enum',
        'choices': ['saltwater', 'freshwater']
    },
    {
        'name': 'origin',
        'type': 'text',
    },
    {
        'name': 'next_water_change',
        'label': 'Next water change',
        'type': 'date',
    }

]

CAR_FIELD_DEFINITIONS = [{
        'name': 'make',
        'type': 'enum',
        'choices': ['BMW', 'Fiat', 'Volkswagen']
    },
    {
        'name': 'mileage',
        'type': 'number',
    },
    {
        'name': 'feautres',
        'type': 'text',
        'blank': True
    },
    {
        'name': 'first_registration_date',
        'label': 'First registration date',
        'type': 'date',
    }

]


class SchemasDefinedMixin(object):
    def setUp(self):
        super().setUp()
        self.aquarium_schema = Schema.objects.create(name='aquarium')
        for field_definition in AQUARIUM_FIELD_DEFINITIONS:
            self.aquarium_schema.field_definitions.create(**field_definition)

        self.car_schema = Schema.objects.create(name='car')
        for field_definition in CAR_FIELD_DEFINITIONS:
            self.car_schema.field_definitions.create(**field_definition)


class SchemaApiTestCase(SchemasDefinedMixin, APITestCase):

    def test_list_schemas(self):
        response = self.client.get('/schemas/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_schema(self):
        response = self.client.get('/schemas/{}/'.format(self.aquarium_schema.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FieldDefinitionsTestCase(SchemasDefinedMixin, APITestCase):

    def test_number_field_representation(self):
        field = self.aquarium_schema.field_definitions.get(name='volume')
        data = FieldDefinitionSerializer(field).data
        self.assertDictEqual(data, {
            'name': 'volume',
            'label': 'Volume',
            'type': 'number',
            'blank': False,
            'choices': list()
        })

    def test_number_field_hstore_definition(self):
        field = self.aquarium_schema.field_definitions.get(name='volume')
        data = field.get_hstore_definition()

        self.assertEqual(data['class'], 'IntegerField')
        self.assertEqual(data['name'], 'volume')
        self.assertEqual(data['kwargs']['blank'], False)

    def test_blank_number_field_hstore_definition(self):
        field = self.aquarium_schema.field_definitions.get(name='temperature')
        data = field.get_hstore_definition()

        self.assertEqual(data['class'], 'IntegerField')
        self.assertEqual(data['name'], 'temperature')
        self.assertEqual(data['kwargs']['blank'], True)
        self.assertEqual(data['kwargs']['null'], True)

    def test_text_field_representation(self):
        field = self.aquarium_schema.field_definitions.get(name='origin')
        data = FieldDefinitionSerializer(field).data
        self.assertDictEqual(data, {
            'name': 'origin',
            'label': 'Origin',
            'type': 'text',
            'blank': False,
            'choices': list()
        })

    def test_text_field_hstore_definition(self):
        field = self.aquarium_schema.field_definitions.get(name='origin')
        data = field.get_hstore_definition()

        self.assertEqual(data['class'], 'TextField')
        self.assertEqual(data['name'], 'origin')
        self.assertEqual(data['kwargs']['blank'], False)

    def test_enum_field_representation(self):
        field = self.aquarium_schema.field_definitions.get(name='water')
        data = FieldDefinitionSerializer(field).data
        self.assertDictEqual(data, {
            'name': 'water',
            'label': 'Water',
            'type': 'enum',
            'blank': False,
            'choices': ['saltwater', 'freshwater']
        })

    def test_enum_field_hstore_definition(self):
        field = self.aquarium_schema.field_definitions.get(name='water')
        data = field.get_hstore_definition()

        self.assertEqual(data['class'], 'CharField')
        self.assertEqual(data['name'], 'water')
        self.assertEqual(data['kwargs']['blank'], False)
        self.assertEqual(data['kwargs']['choices'], [['saltwater', 'saltwater'], ['freshwater', 'freshwater']])

    def test_date_field_representation(self):
        field = self.aquarium_schema.field_definitions.get(name='next_water_change')
        data = FieldDefinitionSerializer(field).data
        self.assertDictEqual(data, {
            'name': 'next_water_change',
            'label': 'Next water change',
            'type': 'date',
            'blank': False,
            'choices': list()
        })

    def test_date_field_hstore_definition(self):
        field = self.aquarium_schema.field_definitions.get(name='next_water_change')
        data = field.get_hstore_definition()

        self.assertEqual(data['class'], 'DateField')
        self.assertEqual(data['name'], 'next_water_change')
        self.assertEqual(data['kwargs']['blank'], False)


class InstanceApiTestCase(SchemasDefinedMixin, APITestCase):

    def test_list_instances(self):
        Instance.objects.create(schema=self.aquarium_schema,
                                data={'volume': 100, 'temperature': None, 'water': 'freshwater',
                                      'origin': 'South America', 'next_water_change': '2018-02-01'})
        Instance.objects.create(schema=self.aquarium_schema,
                                data={'volume': 200, 'temperature': None, 'water': 'saltwater', 'origin': 'Africa',
                                      'next_water_change': '2019-02-01'})

        response = self.client.get('/instances/aquariums/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_instance(self):
        data = {'volume': 100, 'temperature': None, 'water': 'freshwater', 'origin': 'South America',
                'next_water_change': '2018-02-01'}

        response = self.client.post('/instances/aquariums/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        with schema_loaded(self.aquarium_schema):
            instance = Instance.objects.last()
            self.assertEqual(instance.volume, 100)
            self.assertEqual(instance.water, 'freshwater')
            self.assertEqual(instance.origin, 'South America')
            self.assertEqual(instance.next_water_change, date(2018, 2, 1))

    def test_validate_integer(self):
        invalid_data = {'volume': 'xxx', 'water': 'freshwater', 'origin': 'South America',
                        'next_water_change': '2018-02-01'}

        response = self.client.post('/instances/aquariums/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('volume', response.data)

    def test_validate_choice(self):
        invalid_data = {'volume': 100, 'water': 'blackwater', 'origin': 'South America',
                        'next_water_change': '2018-02-01'}

        response = self.client.post('/instances/aquariums/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('water', response.data)

    def test_validate_required(self):
        invalid_data = {'volume': None, 'water': 'freshwater', 'origin': 'South America',
                        'next_water_change': '2018-02-01'}

        response = self.client.post('/instances/aquariums/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('volume', response.data)

    def test_validate_date(self):
        invalid_data = {'volume': 100, 'water': 'blackwater', 'origin': 'South America',
                        'next_water_change': '01-02-2018'}

        response = self.client.post('/instances/aquariums/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('next_water_change', response.data)
