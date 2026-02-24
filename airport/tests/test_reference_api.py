from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airport, AirplaneType, Airplane, Crew
from airport.serializers import (AirportSerializer,
                                 AirplaneDetailSerializer,
                                 AirplaneTypeSerializer,
                                 CrewSerializer)

AIRPORT_URL = reverse("airport:airport-list")
AIRPLANE_TYPE_URL = reverse("airport:airplane-type-list")
AIRPLANE_URL = reverse("airport:airplane-list")
CREW_URL = reverse("airport:crew-list")


def sample_airport(**params):
    defaults = {
        "name": "Boryspil International Airport",
        "closest_big_city": "Kyiv",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {"name": "Boeing 737"}
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    defaults = {
        "name": "UR-PSA",
        "rows": 20,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "Alex",
        "last_name": "Smith",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def airport_detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])

def airplane_type_detail_url(airplane_type_id):
    return reverse("airport:airplane-type-detail", args=[airplane_type_id])

def airplane_detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])

def crew_detail_url(crew_id):
    return reverse("airport:crew-detail", args=[crew_id])

class AirportApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@test.com", password="pass1234")
        self.admin = get_user_model().objects.create_superuser(email="admin@test.com", password="pass1234")

    def test_list_airports(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_airport_forbidden(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        payload = {
            "name": "Test airport",
            "closest_big_city": "Test city",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_airport_detail(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        airport = sample_airport()

        url = airport_detail_url(airport.id)
        res = self.client.get(url)

        serializer = AirportSerializer(airport)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_create_airport_allowed(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        payload = {
            "name": "Test airport",
            "closest_big_city": "Test city",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AirplaneApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@test.com", password="pass1234")
        self.admin = get_user_model().objects.create_superuser(email="admin@test.com", password="pass1234")

    def test_list_airplanes(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_airplane_forbidden(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        payload = {
            "name": "Test airplane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_airplane_detail(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        airplane = sample_airplane()

        url = airplane_detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_create_airplane_allowed(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        payload = {
            "name": "Test airplane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@test.com", password="pass1234")
        self.admin = get_user_model().objects.create_superuser(email="admin@test.com", password="pass1234")

    def test_list_airplane_types(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_airplane_type_forbidden(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        payload = {
            "name": "Test airplane type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_airplane_type_detail(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        airplane_type = sample_airplane_type()

        url = airplane_type_detail_url(airplane_type.id)
        res = self.client.get(url)

        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_create_airplane_type_allowed(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        payload = {
            "name": "Test airplane type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class CrewApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="user@test.com", password="pass1234")
        self.admin = get_user_model().objects.create_superuser(email="admin@test.com", password="pass1234")

    def test_list_crews(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_crew_forbidden(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        payload = {
            "first_name": "Test name",
            "last_name": "Test surname",
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_crew_detail(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        crew = sample_crew()

        url = crew_detail_url(crew.id)
        res = self.client.get(url)

        serializer = CrewSerializer(crew)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_create_crew_allowed(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        payload = {
            "first_name": "Test name",
            "last_name": "Test surname",
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
