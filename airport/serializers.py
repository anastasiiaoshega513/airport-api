from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs):
        Route.validate_route(
            attrs["source"],
            attrs["destination"],
            serializers.ValidationError
        )
        return attrs


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name", read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination")
    )
    crews = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crew.objects.all(),
    )
    airplane = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.all(),
    )

    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crews"
        )


class FlightListSerializer(serializers.ModelSerializer):
    crews = serializers.StringRelatedField(many=True, read_only=True)
    route = serializers.StringRelatedField(read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crews"
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    crews = serializers.StringRelatedField(many=True, read_only=True)
    route = serializers.StringRelatedField(read_only=True)
    airplane = AirplaneDetailSerializer(read_only=True)
    distance = serializers.FloatField(source="route.distance",read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "route", "distance", "airplane", "departure_time", "arrival_time", "crews", "available_seats"
        )


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(many=False, read_only=True)

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketListSerializer(TicketSerializer):
    flight = serializers.CharField(source="flight.route", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "flight", "row", "seat")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class TicketCreateSerializer(serializers.ModelSerializer):
    flight = serializers.CharField(source="flight.route", read_only=True)
    class Meta:
        model = Ticket
        fields = ("flight", "row", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketCreateSerializer(many=True, read_only=True)