from django.contrib.gis.geos import (
    Polygon, LinearRing, Point
)
from rest_framework.serializers import (
    ModelSerializer, ListField, DecimalField, Serializer
)
from .models import Provider, Service


class ProviderSerializer(ModelSerializer):
    class Meta:
        pass
        model = Provider
        fields = '__all__'


class CoordinateAxisValueField(DecimalField):
    DECIMAL_PRECISION = 6

    def __init__(self, *arg, **kwargs):
        super().__init__(**dict(
            kwargs,
            min_value=-180, max_value=180,
            decimal_places=CoordinateAxisValueField.DECIMAL_PRECISION,
            max_digits=CoordinateAxisValueField.DECIMAL_PRECISION+3
        ))


class PolygonField(ListField):
    def __init__(self):
        super().__init__(
            allow_empty=False, min_length=1, max_length=2,
            child=ListField(
                allow_empty=False, min_length=4, max_length=None,
                child=ListField(
                    child=CoordinateAxisValueField(),
                    allow_empty=False, min_length=2, max_length=2
                )
            )
        )

    def to_representation(self, value):
        return super().to_representation(value)

    def to_internal_value(self, data):
        ring_coords = super().to_internal_value(data)
        rings = map(LinearRing, ring_coords)
        return Polygon(*rings)


class ServiceSerializer(ModelSerializer):
    poly = PolygonField()

    class Meta:
        model = Service
        fields = '__all__'


class LatLonSerializer(Serializer):
    lat = CoordinateAxisValueField()
    lon = CoordinateAxisValueField()

    def validate(self, data):
        return Point(
            float(data['lat']),
            float(data['lon'])
        )
