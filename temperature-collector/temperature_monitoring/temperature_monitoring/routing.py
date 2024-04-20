# temperature_monitoring/routing.py
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from temperature_monitoring.temperature_collector.consumers import TemperatureDataConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/temperature-data/", TemperatureDataConsumer.as_asgi()),
    ]),
})