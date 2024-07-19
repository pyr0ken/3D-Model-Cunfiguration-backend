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
    """
    API endpoint for retrieving dashboard statistics for the logged-in user.
    """

    def get(self, request):
        """
        Get counts of edited models, uploaded models, and points created by the user.
        """
        user_id = request.user.id

        # Count the number of edited models by the user
        edited_models_count = EditModel.objects.filter(user_id=user_id).count()

        # Count the number of models uploaded by the user
        uploaded_models_count = Model.objects.filter(
            created_by_id=user_id, status=ModelStatusType.UPLOADED).count()

        # Count the number of points created by the user
        points_count = Point.objects.filter(edit_model__user_id=user_id).count()

        result = {
            "edited_models_count": edited_models_count,
            "uploaded_models_count": uploaded_models_count,
            "points_count": points_count,
        }

        return Response(result, status=status.HTTP_200_OK)


class DashboardRoomMemberApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for retrieving the rooms owned by the logged-in user.
    """

    def get(self, request):
        """
        Get the list of rooms created by the user.
        """
        rooms = Room.objects.filter(owner_id=request.user.id)

        # Serialize the room data
        serializer = RoomMemberDashboardSerializer(rooms, many=True)

        return Response(serializer.data)


class DashboardEditModelApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for retrieving edited models and their associated points count for the logged-in user.
    """

    def get(self, request):
        """
        Get the list of edited models and the count of points for each model.
        """
        # Annotate the edited models with the count of points
        edit_models = EditModel.objects.filter(
            user_id=request.user.id).annotate(points=Count('edit_model_points'))

        # Serialize the edited model data
        serializer = DashboardEditModelSerializer(edit_models, many=True)

        return Response(serializer.data)
