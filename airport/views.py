from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket
from airport.serializers import AirportSerializer, RouteSerializer, AirplaneTypeSerializer, AirplaneSerializer, \
    CrewSerializer, FlightSerializer, OrderSerializer, TicketSerializer, RouteListSerializer, AirplaneListSerializer, \
    FlightListSerializer, FlightDetailSerializer, AirplaneDetailSerializer


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
        ).prefetch_related("crews")
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
        return FlightSerializer




class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
