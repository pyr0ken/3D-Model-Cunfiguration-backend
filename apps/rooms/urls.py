from django.urls import path, include
from . import views

app_name = "rooms"


video_sdk_urlpatterns = [
    # path('token/', views.VideoSDKTokenApi.as_view(), name='video-sdk-token'),
    path('create/', views.VideoSDKCreateRoomApi.as_view(),
         name='video-sdk-create-room'),
]

urlpatterns = [
    path('video-sdk/', include(video_sdk_urlpatterns)),
    path("", views.RoomApi.as_view(), name="room-list"),
    path("models/<str:meeting_id>/", views.RoomModelListApi.as_view(), name="room-models-list"),
    path("models/", views.RoomModelAddApi.as_view(), name="room-models"),
    path("end/", views.RoomEndApi.as_view(), name="room-end"),
    path("left/", views.RoomMemberLeftApi.as_view(), name="room-member-left"),
    # path("check/", views.RoomCheckApi.as_view(), name='room-check'),
    path("join/", views.RoomJoinApi.as_view(), name="room-member"),
    path("<str:room_id>/detail/", views.RoomDetailApi.as_view(), name="room-member"),
    path("<str:room_id>/members/",
         views.RoomMemberApi.as_view(), name="room-member"),
]
