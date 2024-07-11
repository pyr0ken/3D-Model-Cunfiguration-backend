from django.urls import path
from . import views

app_name = "rooms"


urlpatterns = [
    # room api
    path("", views.RoomApi.as_view(), name="room-list"),
    path("end/", views.RoomEndApi.as_view(), name="room-end"),
    path("left/", views.RoomMemberLeftApi.as_view(), name="room-member-left"),
    path("join/", views.RoomJoinApi.as_view(), name="room-member"),
    path("<str:room_id>/detail/", views.RoomDetailApi.as_view(), name="room-member"),
    path('video-sdk/create/', views.VideoSDKCreateRoomApi.as_view(),
         name='video-sdk-create-room'),

    # room model api
    path("models/select/", views.RoomSelectModelApi.as_view(),
         name="room-select-model"),
    path("models/delete/", views.RoomModelDeleteApi.as_view(),
         name="room-delete-model"),
    path("models/<str:meeting_id>/",
         views.RoomModelListApi.as_view(), name="room-models-list"),
    path("models/", views.RoomModelAddApi.as_view(), name="room-models"),
]
