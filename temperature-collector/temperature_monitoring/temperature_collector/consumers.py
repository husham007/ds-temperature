# temperature_collector/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

# Configure logging
logger = logging.getLogger(__name__)


class TemperatureDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def temperature_data(self, event):
        temperature_data = event['temperature_data']
        await self.send(text_data=json.dumps(temperature_data))
