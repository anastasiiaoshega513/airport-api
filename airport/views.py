from django.db.models import F, Count, Prefetch
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket
from airport.serializers import AirportSerializer, RouteSerializer, AirplaneTypeSerializer, AirplaneSerializer, \
    CrewSerializer, FlightSerializer, OrderSerializer, TicketSerializer, RouteListSerializer, AirplaneListSerializer, \
    FlightListSerializer, FlightDetailSerializer, AirplaneDetailSerializer, TicketSeatsSerializer, OrderListSerializer, \
    TicketListSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")

    def get_queryset(self):
        source_name = self.request.query_params.get("source_name")
        destination_name = self.request.query_params.get("destination_name")
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")

        queryset = self.queryset

        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)

        if destination_name:
            queryset = queryset.filter(destination__name__icontains=destination_name)

        if source_city:
            queryset = queryset.filter(source__closest_big_city__icontains=source_city)

        if destination_city:
            queryset = queryset.filter(destination__closest_big_city__icontains=destination_city)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 30


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
            "route__source",
            "route__destination",
            "airplane",
        ).prefetch_related("crews").annotate(
            available_seats=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    pagination_class = DefaultPagination

    def get_queryset(self):
        source_name = self.request.query_params.get("source_name")
        destination_name = self.request.query_params.get("destination_name")
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")

        queryset = self.queryset

        if source_name:
            queryset = queryset.filter(route__source__name__icontains=source_name)

        if destination_name:
            queryset = queryset.filter(route__destination__name__icontains=destination_name)

        if source_city:
            queryset = queryset.filter(route__source__closest_big_city__icontains=source_city)

        if destination_city:
            queryset = queryset.filter(route__destination__closest_big_city__icontains=destination_city)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        elif self.action == "available_seats":
            return TicketSeatsSerializer
        return FlightSerializer

    @action(
        detail=True,
        methods=["get"],
        url_path="available-seats",
    )
    def available_seats(self, request, pk=None):
        flight = self.get_object()
        airplane = flight.airplane

        taken = set(
            Ticket.objects.filter(flight=flight).values_list("row", "seat")
        )
        available = []
        for row in range(1, airplane.rows + 1):
            for seat in range(1, airplane.seats_in_row + 1):
                if (row, seat) not in taken:
                    available.append({"row": row, "seat": seat})

        return Response(available)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        "flight",
        "flight__route",
        "flight__route__source",
        "flight__route__destination",
        "flight__airplane",
        "order"
    ).prefetch_related(
        "flight__crews"
    )

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        return TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        tickets_qs = (Ticket.objects.select_related(
                "flight",
                "flight__route",
                "flight__route__source",
                "flight__route__destination",
            )
        )
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(Prefetch("tickets", queryset=tickets_qs))
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
