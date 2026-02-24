import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Order, Ticket
from airport.serializers import OrderSerializer, TicketSerializer
from airport.tests.test_flight_api import sample_flight

ORDER_URL = reverse("airport:order-list")
TICKET_URL = reverse("airport:ticket-list")


def create_user(password="testpass"):
    email = f"{uuid.uuid4()}@test.com"
    return get_user_model().objects.create_user(email, password)

def auth(client, user):
    client.force_authenticate(user=user)

def sample_order(**params):
    defaults = {
        "user": create_user(),
    }
    defaults.update(params)

    return Order.objects.create(**defaults)


def order_detail_url(order_id):
    return reverse("airport:order-detail", args=[order_id])

def ticket_detail_url(ticket_id):
    return reverse("airport:ticket-detail", args=[ticket_id])


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = create_user()
        self.user2 = create_user()
        self.client.force_authenticate(self.user1)

    def test_user_create_order(self):
        self.client.force_authenticate(user=self.user1)
        flight = sample_flight()

        payload = {
            "tickets": [
                {"flight": flight.id, "row": 1, "seat": 1},
                {"flight": flight.id, "row": 1, "seat": 2},
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        print(res.status_code, res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_order_without_tickets(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "tickets": []
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_sees_only_own_orders(self):
        self.client.force_authenticate(user=self.user1)

        order1 = sample_order(user=self.user1)
        order2 = sample_order(user=self.user2)
        flight = sample_flight()

        Ticket.objects.create(order=order1, flight=flight, row=1, seat=1)
        Ticket.objects.create(order=order2, flight=flight, row=1, seat=2)

        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        orders_ids = {order["id"] for order in res.data["results"]}
        print(res.status_code, res.data)
        self.assertIn(order1.id, orders_ids)
        self.assertNotIn(order2.id, orders_ids)


    def test_retrieve_order_detail(self):
        order = sample_order(user=self.user1)
        Ticket.objects.create(order=order, flight=sample_flight(), row=1, seat=1)

        url = order_detail_url(order.id)
        res = self.client.get(url)

        serializer = OrderSerializer(order)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_sees_only_own_tickets(self):
        self.client.force_authenticate(user=self.user1)

        order1 = sample_order(user=self.user1)
        order2 = sample_order(user=self.user2)
        ticket1 = Ticket.objects.create(order=order1, flight=sample_flight(), row=1, seat=1)
        ticket2 = Ticket.objects.create(order=order2, flight=sample_flight(), row=1, seat=2)

        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tickets_ids = {ticket["id"] for ticket in res.data}
        self.assertIn(ticket1.id, tickets_ids)
        self.assertNotIn(ticket2.id, tickets_ids)


    def test_retrieve_ticket_detail(self):
        order = sample_order(user=self.user1)
        ticket = Ticket.objects.create(order=order, flight=sample_flight(), row=1, seat=1)

        url = ticket_detail_url(ticket.id)
        res = self.client.get(url)

        serializer = TicketSerializer(ticket)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
