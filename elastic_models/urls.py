from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from elastic_models import views

elastic_models_router = DefaultRouter()
elastic_models_router.register(r'schemas', views.SchemaViewSet, base_name='schemas')
elastic_models_router.register(r'instances/(?P<schema_name_plural>\w+)', views.InstanceViewSet,
                               base_name='instances')

urlpatterns = [
    url(r'^', include(elastic_models_router.urls)),
]
