from django.contrib import admin

# Register your models here.
from elastic_models.models import Schema, FieldDefinition


class FieldDefinitionInline(admin.StackedInline):
    model = FieldDefinition
    fields = ['name', 'label', 'type', 'blank', 'choices']
    extra = 1


class SchemaAdmin(admin.ModelAdmin):
    inlines = [FieldDefinitionInline]


admin.site.register(Schema, SchemaAdmin)
