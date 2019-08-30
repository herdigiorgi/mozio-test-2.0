from django.urls import reverse
from rest_framework.test import APITestCase
from random import randint
from faker import Faker
from rest_framework.serializers import ListSerializer
from django.contrib.gis.geos import (
    Polygon, LinearRing, Point
)
from mozio.models import Service, Provider
from mozio.search_service import (
    ServiceRedisStorage, search_services
)


class ServiceSearchTests(APITestCase):

    def setUp(self):
        self.cache = ServiceRedisStorage(redis_db=randint(1, 15))
        self.faker = Faker()
        self.provider = Provider.objects.create(
            name=self.faker.company(),
            email=self.faker.email(),
            cur=self.faker.currency_code()
        )
        self.service1 = Service.objects.create(
            provider=self.provider,
            name=self.faker.job(),
            price=randint(10, 100)/5,
            poly=Polygon(LinearRing((0, 0), (0, 5), (5, 5), (5, 0), (0, 0)))
        )
        self.search = lambda point: search_services(point, self.cache)
        self.search_list = lambda point: list(self.search(point).instance)

    def tearDown(self):
        self.cache.clean()

    def test_search_single_intersection(self):
        search_point = Point(4.5, 4.5)
        self.assertEqual(
            ListSerializer,
            type(self.search(search_point)),
            "smoke test the fist uncached test")
        self.assertEqual(
            ListSerializer,
            type(self.search(search_point)),
            "smoke test the second cached test")
        r = self.search_list(search_point)
        self.assertEqual(1, len(r))
        self.assertEqual(self.service1.poly, r[0].poly)
        self.assertEqual([], self.search_list(Point(6, 6)))

    def test_api_endpoint(self):
        def make_req():
            return self.client.get('/service/search/?lat=4&lon=5')
        res1 = make_req()
        self.assertEqual(res1.status_code, 200)
        res2 = make_req()
        self.assertEqual(res2.status_code, 200)
        expected_poly = [[
            ['0.000000', '0.000000'], ['0.000000', '5.000000'], 
            ['5.000000', '5.000000'], ['5.000000', '0.000000'], 
            ['0.000000', '0.000000']
        ]]
        self.assertEqual(1, len(res1.data))
        self.assertEqual(1, len(res2.data))
        self.assertEqual(expected_poly, res1.data[0].get('poly'))
        self.assertEqual(expected_poly, res2.data[0].get('poly'))
        
