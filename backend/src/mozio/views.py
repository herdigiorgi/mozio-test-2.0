from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
import coreapi
from .models import Provider, Service
from .serializers import (
    ProviderSerializer, ServiceSerializer, LatLonSerializer
)
from .search_service import search_services
from rest_framework.schemas import AutoSchema
from drf_yasg.inspectors import CoreAPICompatInspector, FieldInspector, NotHandled, SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema


class ProviderViewSet(ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class SearchAutoSchema(SwaggerAutoSchema):
    def should_page(self):
        return False

    def get_query_serializer(self):
        return LatLonSerializer()


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    search_schema = AutoSchema(manual_fields=[
        coreapi.Field(
            'lat',
            required=True,
            location='query',
            type='number',
            description='Geographical latitude from -180 to 180'
        ),
        coreapi.Field(
            'lon',
            required=True,
            location='query',
            type='number',
            description='Geographical latitude from -180 to 180',
            example="90.124"
        )  
    ])

    @swagger_auto_schema(auto_schema=SearchAutoSchema)
    @action(detail=False, methods=['get'], schema=search_schema)
    def search(self, request):
        "search description"
        qs = LatLonSerializer(data=request.query_params)
        qs.is_valid(raise_exception=True)
        result = search_services(qs.validated_data)
        return Response(result.data)
