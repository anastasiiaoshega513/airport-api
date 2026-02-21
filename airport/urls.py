from django.urls import path, include

from airport.views import AirportViewSet, RouteViewSet, AirplaneTypeViewSet, AirplaneViewSet, CrewViewSet, OrderViewSet, \
    FlightViewSet, TicketViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
