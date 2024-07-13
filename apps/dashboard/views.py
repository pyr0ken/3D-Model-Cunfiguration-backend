from django.db.models import Count
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from apps.core.mixins import AuthenticatedAccessMixin
from apps.rooms.models import Room
from apps.models.models import EditModel, Model, Point
from apps.models.constants import ModelStatusType
from .serializers import DashboardEditModelSerializer, RoomMemberDashboardSerializer


class DashboardApi(AuthenticatedAccessMixin, APIView):
    def get(self, request):
        user_id = request.user.id

        edited_models_count = EditModel.objects.filter(
            user_id=user_id).count()
        uploaded_models_count = Model.objects.filter(
            created_by_id=user_id, status=ModelStatusType.UPLOADED).count()
        points_count = Point.objects.filter(
            edit_model__user_id=user_id).count()

        result = {
            "edited_models_count": edited_models_count,
            "uploaded_models_count": uploaded_models_count,
            "points_count": points_count,

        }

        return Response(result, status=status.HTTP_200_OK)


class DashboardRoomMemberApi(AuthenticatedAccessMixin, APIView):
    def get(self, request):
        rooms = Room.objects.filter(owner_id=request.user.id).annotate(
            members=Count('user_rooms'))
        serializer = RoomMemberDashboardSerializer(rooms, many=True)
        return Response(serializer.data)


class DashboardEditModelApi(AuthenticatedAccessMixin, APIView):
    def get(self, request):
        edit_models = EditModel.objects.filter(
            user_id=request.user.id).annotate(points=Count('edit_model_points'))
        serializer = DashboardEditModelSerializer(edit_models, many=True)
        return Response(serializer.data)
