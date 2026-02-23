import tempfile
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer

ROUTE_URL = reverse("airport:route-list")


def sample_airport(**params):
    defaults = {
        "name": "Boryspil International Airport",
        "closest_big_city": "Kyiv",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_airport(
            name="Boryspil International Airport",
            closest_big_city="Kyiv",
        ),
        "destination": sample_airport(
            name="Barcelona–El Prat Airport",
            closest_big_city="Barcelona",
        ),
        "distance": 2390,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


class UnauthenticatedAndAuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        self.kyiv_airport = sample_airport(
            name="Boryspil International Airport",
            closest_big_city="Kyiv",
        )
        self.paris_airport = sample_airport(
            name="Charles de Gaulle Airport",
            closest_big_city="Paris",
        )
        self.barcelona_airport = sample_airport(
            name="Barcelona–El Prat Airport",
            closest_big_city="Barcelona",
        )

        self.route1 = sample_route(source=self.kyiv_airport, destination=self.barcelona_airport)
        self.route2 = sample_route(source=self.kyiv_airport, destination=self.paris_airport)
        self.route3 = sample_route(source=self.paris_airport, destination=self.barcelona_airport)

    def test_list_routes(self):
        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_filter_routes_by_source_name(self):
        res = self.client.get(
            ROUTE_URL, {"source_name": "boryspil"}
        )

        serializer1 = RouteListSerializer(self.route1)
        serializer2 = RouteListSerializer(self.route2)
        serializer3 = RouteListSerializer(self.route3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_routes_by_destination_name(self):
        res = self.client.get(
            ROUTE_URL, {"destination_name": "prat"}
        )

        serializer1 = RouteListSerializer(self.route1)
        serializer2 = RouteListSerializer(self.route2)
        serializer3 = RouteListSerializer(self.route3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer3.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_routes_by_source_city(self):
        res = self.client.get(
            ROUTE_URL, {"source_city": "kyiv"}
        )

        serializer1 = RouteListSerializer(self.route1)
        serializer2 = RouteListSerializer(self.route2)
        serializer3 = RouteListSerializer(self.route3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_routes_by_destination_city(self):
        res = self.client.get(
            ROUTE_URL, {"destination_city": "paris"}
        )

        serializer1 = RouteListSerializer(self.route1)
        serializer2 = RouteListSerializer(self.route2)
        serializer3 = RouteListSerializer(self.route3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_create_route_forbidden(self):
        source = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        dest = sample_airport(name="CDG", closest_big_city="Paris")
        payload = {
            "source": source.id,
            "destination": dest.id,
            "distance": 90,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        source = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        dest = sample_airport(name="CDG", closest_big_city="Paris")
        payload = {
            "source": source.id,
            "destination": dest.id,
            "distance": 90,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(payload["source"], route.source_id)
        self.assertEqual(payload["destination"], route.destination_id)
        self.assertEqual(payload["distance"], route.distance)
