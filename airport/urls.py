from django.urls import path, include

from airport.views import AirportViewSet, RouteViewSet, AirplaneTypeViewSet, AirplaneViewSet, CrewViewSet, OrderViewSet, \
    FlightViewSet, TicketViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("airplane_types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("crews", CrewViewSet, basename="crew")
router.register("routes", RouteViewSet, basename="route")
router.register("flights", FlightViewSet, basename="flight")
router.register("orders", OrderViewSet, basename="order")
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
