from django.urls import path
from . import views


app_name = "dashboard"

urlpatterns = [
    path('', views.DashboardApi.as_view(), name="room-members"),
    path('room-members/', views.DashboardRoomMemberApi.as_view(), name="room-members"),
    path('edit-models/', views.DashboardEditModelApi.as_view(), name="room-members"),
]
