from django.utils import timezone
from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.mixins import AuthenticatedAccessMixin
from apps.models.models import EditModel, Model
from .serializers import (
    EnterRoomSerializer, InputRoomCreateSerializer, OutputRoomModelSerializer,
    RoomDeleteInputSerializer, RoomDetailSerializer, RoomEndSerializer,
    RoomJoinInputSerializer, RoomListSerializer, RoomMemberLeftSerializer,
    RoomMemberListSerializer, RoomModelDeleteSerializer, RoomSelectModelSerializer,
    InputRoomModelSerializer
)
from .models import Room, RoomMember, RoomModel
from .videoSDK import generate_token, create_room

class RoomApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for handling Room operations.
    """

    def get(self, request):
        """
        Retrieve the list of rooms created and joined by the current user.
        """
        created_rooms = Room.objects.filter(owner_id=request.user.id).annotate(
            edit_models_count=Count("room_models")
        ).order_by("-created_at")

        joined_rooms = RoomMember.objects.filter(user_id=request.user.id).exclude(
            room__owner_id=request.user.id
        ).order_by("-last_join")

        created_rooms_serializer = RoomListSerializer(created_rooms, many=True)
        joined_rooms_serializer = RoomMemberListSerializer(joined_rooms, many=True)

        result = {
            "created_rooms": created_rooms_serializer.data,
            "joined_rooms": joined_rooms_serializer.data,
        }

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new room.
        """
        serializer = InputRoomCreateSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            Room.objects.create(
                title=serializer.validated_data['title'],
                owner_id=request.user.id
            )
            return Response({"detail": "جلسه با موفقیت ساخته شد."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Delete a room.
        """
        serializer = RoomDeleteInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.filter(id=serializer.validated_data["room_id"]).first()
            if room:
                room.delete()
                return Response({"detail": "جلسه مورد نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK)
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomEnterApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for entering a room.
    """

    def post(self, request):
        """
        Enter a room and generate an videoSDK authentication token.
        """
        serializer = EnterRoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.filter(id=serializer.validated_data['room_id']).first()
            if not room:
                return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

            room.is_active = True
            room.save(update_fields=['is_active'])

            is_owner = room.owner_id == request.user.id
            auth_token = generate_token(is_owner)

            if not room.meeting_id:
                response = create_room(auth_token)
                room.meeting_id = response['roomId']
                room.save(update_fields=['meeting_id'])

            result = {
                "auth_token": auth_token,
                "room_title": room.title,
                "meeting_id": room.meeting_id
            }

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for retrieving room details.
    """

    def get(self, request, room_id):
        """
        Get the details of a specific room.
        """
        room = Room.objects.filter(id=room_id).first()
        if room:
            room_serializer = RoomDetailSerializer(room)
            return Response(room_serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "The room id is not found."}, status=status.HTTP_404_NOT_FOUND)


class RoomEndApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for ending a room session.
    """

    def post(self, request):
        """
        End a room session and mark all members as left.
        """
        serializer = RoomEndSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.filter(meeting_id=serializer.validated_data["meeting_id"]).first()
            if room:
                RoomMember.objects.filter(room__meeting_id=serializer.validated_data["meeting_id"]).update(
                    is_leave=True, last_join=timezone.now()
                )
                room.is_active = False
                room.save(update_fields=['is_active'])
                return Response({"detail": "Room ended successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomMemberLeftApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for marking a member as left from a room.
    """

    def post(self, request):
        """
        Mark a user as having left a room.
        """
        serializer = RoomMemberLeftSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            member = RoomMember.objects.filter(
                room__meeting_id=serializer.validated_data["meeting_id"],
                user_id=serializer.validated_data["user_id"]
            ).first()
            if member:
                member.is_leave = True
                member.last_join = timezone.now()
                member.save(update_fields=['is_leave', 'last_join'])
                return Response({"detail": "User left the room successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Room member not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomJoinApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for joining a room.
    """

    def post(self, request):
        """
        Join a room.
        """
        serializer = RoomJoinInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            room = Room.objects.filter(meeting_id=serializer.validated_data["room_id"]).first()
            if not room:
                return Response({'detail': "جلسه مورد نظر پیدا نشد."}, status=status.HTTP_400_BAD_REQUEST)
            if not room.is_active:
                return Response({"detail": "جلسه به اتمام رسیده است."}, status=status.HTTP_400_BAD_REQUEST)

            member, created = RoomMember.objects.get_or_create(user_id=request.user.id, room_id=room.id)
            member.is_leave = False
            member.save(update_fields=['is_leave'])

            is_owner = room.owner_id == request.user.id
            auth_token = generate_token(is_owner)

            result = {
                "auth_token": auth_token,
                "meeting_id": room.meeting_id,
                "room_title": room.title,
                "room_id": room.id,
            }

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomModelListApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for listing room models.
    """

    def get(self, request, meeting_id):
        """
        Get the list of models associated with a room.
        """
        room_models = RoomModel.objects.filter(room__meeting_id=meeting_id)
        serializer = OutputRoomModelSerializer(room_models, many=True)

        selected_model = RoomModel.objects.filter(room__meeting_id=meeting_id, is_select=True).order_by("-created_at").first()

        selected_data = None
        if selected_model:
            model_serializer = OutputRoomModelSerializer(selected_model)
            selected_data = model_serializer.data

        result = {
            "models": serializer.data,
            "selected_model": selected_data,
        }

        return Response(result, status=status.HTTP_200_OK)


class RoomSelectModelApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for selecting a model in a room.
    """

    def post(self, request):
        """
        Select a specific model for a room.
        """
        serializer = RoomSelectModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data["meeting_id"]
            edit_model_id = serializer.validated_data["edit_model_id"]

            RoomModel.objects.filter(room__meeting_id=meeting_id).update(is_select=False)
            RoomModel.objects.filter(room__meeting_id=meeting_id, edit_model_id=edit_model_id).update(is_select=True)

            return Response({"detail": "The Model selected successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomModelDeleteApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for deleting a model from a room.
    """

    def post(self, request):
        """
        Delete a specific model from a room.
        """
        serializer = RoomModelDeleteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data["meeting_id"]
            edit_model_id = serializer.validated_data["edit_model_id"]

            RoomModel.objects.filter(room__meeting_id=meeting_id, edit_model_id=edit_model_id).delete()

            return Response({"detail": "مدل با موفقیت از جلسه حذف شد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomModelAddApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for adding a model to a room.
    """

    def post(self, request):
        """
        Add a new model to a room.
        """
        input_serializer = InputRoomModelSerializer(data=request.data)

        if input_serializer.is_valid(raise_exception=True):
            meeting_id = input_serializer.validated_data["meeting_id"]
            model_id = input_serializer.validated_data["model_id"]
            edit_model_id = input_serializer.validated_data.get("edit_model_id")

            room = Room.objects.filter(meeting_id=meeting_id).first()
            if not room:
                return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

            edit_model = None
            if edit_model_id:
                edit_model = EditModel.objects.filter(id=edit_model_id).first()

            if not edit_model:
                model = Model.objects.filter(id=model_id).first()
                if not model:
                    return Response({"detail": "Model not found."}, status=status.HTTP_404_NOT_FOUND)

                edit_models_count = EditModel.objects.filter(model_id=model_id).count()
                display_name = model.title
                if edit_models_count >= 0:
                    display_name = f"{display_name} ({edit_models_count + 1})"

                edit_model = EditModel.objects.create(
                    user_id=request.user.id,
                    model_id=model_id,
                    display_name=display_name,
                    last_edit=timezone.now()
                )

            RoomModel.objects.filter(room_id=room.id).update(is_select=False)

            room_model, created = RoomModel.objects.get_or_create(
                room_id=room.id, edit_model_id=edit_model.id,
                defaults={"is_select": True}
            )

            if not created:
                room_model.is_select = True
                room_model.save(update_fields=['is_select'])

            return Response({"detail": "New Edit model Opened."}, status=status.HTTP_201_CREATED)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
