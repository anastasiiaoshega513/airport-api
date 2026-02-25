from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Flight
from airport.serializers import FlightListSerializer
from airport.tests.test_reference_api import (
    sample_crew,
    sample_airplane,
    sample_airplane_type,
)
from airport.tests.test_route_api import sample_route, sample_airport

FLIGHT_URL = reverse("airport:flight-list")


def sample_flight(**params):
    defaults = {
        "route": sample_route(),
        "airplane": sample_airplane(airplane_type=sample_airplane_type()),
        "departure_time": "2026-03-01T10:30:00Z",
        "arrival_time": "2026-03-01T13:15:00Z",
    }
    defaults.update(params)

    flight = Flight.objects.create(**defaults)
    flight.crews.set([sample_crew()])
    return flight


def flight_detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class FlightGeneralApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="pass1234"
        )
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="pass1234"
        )

    def test_list_flights(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_flight_forbidden(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        route = sample_route()
        airplane_type = sample_airplane_type()
        airplane = sample_airplane(airplane_type=airplane_type)
        crew1 = sample_crew(first_name="John", last_name="Doe")
        crew2 = sample_crew(first_name="Anna", last_name="Smith")

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2026-03-01T10:30:00Z",
            "arrival_time": "2026-03-01T13:15:00Z",
            "crews": [crew1.id, crew2.id],
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_flight_detail(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        flight = sample_flight()

        url = flight_detail_url(flight.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("available_seats", res.data)
        self.assertEqual(
            res.data["available_seats"],
            flight.airplane.rows * flight.airplane.seats_in_row,
        )

    def test_admin_create_flight_allowed(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        route = sample_route()
        airplane_type = sample_airplane_type()
        airplane = sample_airplane(airplane_type=airplane_type)
        crew1 = sample_crew(first_name="John", last_name="Doe")
        crew2 = sample_crew(first_name="Anna", last_name="Smith")

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2026-03-01T10:30:00Z",
            "arrival_time": "2026-03-01T13:15:00Z",
            "crews": [crew1.id, crew2.id],
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(flight.route_id, route.id)
        self.assertEqual(flight.airplane_id, airplane.id)
        self.assertEqual(
            set(flight.crews.values_list("id", flat=True)), {crew1.id, crew2.id}
        )


class FlightFilterApiTestCase(TestCase):
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

        self.route1 = sample_route(
            source=self.kyiv_airport, destination=self.barcelona_airport
        )
        self.route2 = sample_route(
            source=self.kyiv_airport, destination=self.paris_airport
        )
        self.route3 = sample_route(
            source=self.paris_airport, destination=self.barcelona_airport
        )

        self.flight1 = sample_flight(route=self.route1)
        self.flight2 = sample_flight(route=self.route2)
        self.flight3 = sample_flight(route=self.route3)

    def test_filter_flights_by_source_name(self):
        res = self.client.get(FLIGHT_URL, {"source_name": "boryspil"})

        serializer1 = FlightListSerializer(self.flight1)
        serializer2 = FlightListSerializer(self.flight2)
        serializer3 = FlightListSerializer(self.flight3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_flights_by_destination_name(self):
        res = self.client.get(FLIGHT_URL, {"destination_name": "prat"})

        serializer1 = FlightListSerializer(self.flight1)
        serializer2 = FlightListSerializer(self.flight2)
        serializer3 = FlightListSerializer(self.flight3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer3.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_filter_flights_by_source_city(self):
        res = self.client.get(FLIGHT_URL, {"source_city": "kyiv"})

        serializer1 = FlightListSerializer(self.flight1)
        serializer2 = FlightListSerializer(self.flight2)
        serializer3 = FlightListSerializer(self.flight3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_flights_by_destination_city(self):
        res = self.client.get(FLIGHT_URL, {"destination_city": "paris"})

        serializer1 = FlightListSerializer(self.flight1)
        serializer2 = FlightListSerializer(self.flight2)
        serializer3 = FlightListSerializer(self.flight3)

        self.assertNotIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])
