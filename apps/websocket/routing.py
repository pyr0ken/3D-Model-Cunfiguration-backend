from django.urls import path

from . import consumers

# Video room route
websocket_urlpatterns = [
    path("ws/room/<str:room_id>/", consumers.RoomConsumer.as_asgi()),
    path("ws/speech-to-text/", consumers.SpeechToTextConsumer.as_asgi()),
]
