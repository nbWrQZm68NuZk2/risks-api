# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django_hstore.fields
import elastic_models.helpers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FieldDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('type', models.CharField(max_length=10, choices=[('number', 'Number'), ('text', 'Text'), ('enum', 'Enum'), ('date', 'Date')])),
                ('name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('blank', models.BooleanField(default=False)),
                ('choices', jsonfield.fields.JSONField(blank=True, validators=[elastic_models.helpers.list_of_strings_validator])),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('data', django_hstore.fields.DictionaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('name_plural', models.CharField(max_length=255, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='instance',
            name='schema',
            field=models.ForeignKey(to='elastic_models.Schema'),
        ),
        migrations.AddField(
            model_name='fielddefinition',
            name='schema',
            field=models.ForeignKey(related_name='field_definitions', to='elastic_models.Schema'),
        ),
        migrations.AlterUniqueTogether(
            name='fielddefinition',
            unique_together=set([('schema', 'name')]),
        ),
    ]
