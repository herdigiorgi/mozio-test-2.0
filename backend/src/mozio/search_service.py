from io import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from app.settings import REDIS as REDIS_SETTINGS
from django.contrib.gis.geos import Point
from abc import ABC, abstractmethod
from redis import Redis
from .models import Service
from .serializers import (
    CoordinateAxisValueField, ServiceSerializer
)

DEFAULT_PRECISION = CoordinateAxisValueField.DECIMAL_PRECISION / 2


class ServiceKeyValueStorage(ABC):

    def __init__(self, ttl=600, precision=DEFAULT_PRECISION):
        self.ttl = ttl
        self.precision = precision

    def float_to_key(self, num: float) -> str:
        precision = max(
            self.precision,
            CoordinateAxisValueField.DECIMAL_PRECISION)
        return "{0:.{p}f}".format(num, p=precision)

    def point_to_key(self, point: Point) -> str:
        x_key = self.float_to_key(point.x)
        y_key = self.float_to_key(point.y)
        return "{},{}".format(x_key, y_key)

    def __getitem__(self, key: Point) -> ServiceSerializer:
        return self.get_item(self.point_to_key(key))

    def __setitem__(self, key: Point, value: [Service]):
        return self.set_item(self.point_to_key(key), value, self.ttl)

    @abstractmethod
    def get_item(self, key: str) -> ServiceSerializer:
        pass

    @abstractmethod
    def set_item(self, key: str, value: [Service], ttl):
        pass

    @abstractmethod
    def clean(self):
        pass


class ServiceRedisStorage(ServiceKeyValueStorage):
    def __init__(self, redis_db=REDIS_SETTINGS['db'], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = Redis(
            host=REDIS_SETTINGS['host'],
            port=REDIS_SETTINGS['port'],
            db=kwargs.get('redis_db', redis_db))

    def get_item(self, key: str) -> ServiceSerializer:
        ret = self.redis.get(key)
        if ret is None:
            return []
        stream = BytesIO(ret)
        parsed_ret = JSONParser().parse(stream)
        serializer = ServiceSerializer(data=parsed_ret, many=True)
        serializer.is_valid()

        def to_model(dic):
            return Service(**dic)

        data = list(map(to_model, serializer.validated_data))
        return ServiceSerializer(data, many=True)

    def set_item(self, key: str, value: [Service], ttl):
        if not value:
            return
        serializer = ServiceSerializer(value, many=True)
        json = JSONRenderer().render(serializer.data)
        self.redis.set(key, json, ex=ttl)

    def clean(self):
        self.redis.flushall()


default_cache = ServiceRedisStorage()


def search_services(point: Point,
                    cache: ServiceKeyValueStorage = default_cache
                    ) -> ServiceSerializer:
    cache_result = cache[point]
    if cache_result:
        return cache_result
    else:
        db_result = Service.objects.all().filter(
            poly__intersects=point
        )
        cache[point] = db_result
        return ServiceSerializer(db_result, many=True)
