from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.models.models import EditModel, Model
from .serializers import (
    InputRoomCreateSerializer,
    OutputRoomModelSerializer,
    RoomDeleteInputSerializer,
    RoomDetailSerializer,
    RoomEndSerializer,
    RoomJoinInputSerializer,
    RoomListSerializer,
    RoomMemberLeftSerializer,
    RoomMemberListSerializer,
    RoomModelDeleteSerializer,
    RoomSelectModelSerializer,
    VideoSDKCreateRoomSerializer,
    InputRoomModelSerializer,
)
from .models import Room, RoomMember, RoomModel
from .viideoSDK import generate_token, create_room


class VideoSDKCreateRoomApi(APIView):
    def post(self, request):
        serializer = VideoSDKCreateRoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            id = serializer.validated_data['id']

            room = Room.objects.filter(id=id).first()
            room.is_active = True
            room.save(update_fields=['is_active'])

            # Create Token
            is_owner = False
            if room.owner_id == request.user.id:
                is_owner = True

            auth_token = generate_token(is_owner)

            # Check room meeting id
            if not room.meeting_id:

                # Create Room
                response = create_room(auth_token)

                room.meeting_id = response['roomId']
                room.save(update_fields=['meeting_id'])

            result = {
                "auth_token": auth_token,
                "room_title": room.title,
                "meeting_id": room.meeting_id
            }

            return Response(result, status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        created_rooms = Room.objects.filter(owner_id=request.user.id)
        joined_rooms = RoomMember.objects.filter(user_id=request.user.id).exclude(
            room__owner_id=request.user.id
        )

        created_rooms_serializer = RoomListSerializer(created_rooms, many=True)
        joined_rooms_serializer = RoomMemberListSerializer(
            joined_rooms, many=True)

        result = {
            "created_rooms": created_rooms_serializer.data,
            "joined_rooms": joined_rooms_serializer.data,
        }

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = InputRoomCreateSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            title = serializer.validated_data['title']

            new_room = Room.objects.create(
                title=title,
                owner_id=request.user.id
            )

            return Response(
                {"detail": "The room created successfully."}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        serializer = RoomDeleteInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            id = serializer.validated_data.get("id")

            room = Room.objects.filter(id=id).first()
            room.delete()

            return Response(
                {"detail": "The room deleted successfully."}, status=status.HTTP_200_OK
            )


class RoomDetailApi(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_id):
        room = Room.objects.filter(id=room_id).first()

        if room:
            room_serializer = RoomDetailSerializer(room)
            return Response(room_serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "The room id is not found."}, status=status.HTTP_404_NOT_FOUND
        )


class RoomEndApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RoomEndSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data.get("meeting_id")
            room = Room.objects.filter(meeting_id=meeting_id).first()

            RoomMember.objects.filter(
                room__meeting_id=meeting_id
            ).update(
                is_leave=True,
                last_join=timezone.now()
            )

            room.is_active = False
            room.save(update_fields=['is_active'])

            return Response({"detail": "Room ended successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomMemberLeftApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RoomMemberLeftSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data.get("meeting_id")
            user_id = serializer.validated_data.get("user_id")

            member = RoomMember.objects.filter(
                room__meeting_id=meeting_id,
                user_id=user_id
            ).first()

            member.is_leave = True
            member.last_join = timezone.now()
            member.save(update_fields=['is_leave', 'last_join'])

            return Response({"detail": "User left the room successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomJoinApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RoomJoinInputSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data.get("room_id")
            room = Room.objects.filter(meeting_id=meeting_id).first()

            member, created = RoomMember.objects.get_or_create(
                user_id=request.user.id, room_id=room.id)

            member.is_leave = False
            member.save(update_fields=['is_leave'])

            if not room:
                return Response({'detail': "Room is not not found"}, status=status.HTTP_404_NOT_FOUND)

            if not room.is_active:
                return Response({"detail": "Room is ended"}, status=status.HTTP_400_BAD_REQUEST)

            is_owner = False
            if room.owner_id == request.user.id:
                is_owner = True

            auth_token = generate_token(is_owner)

            result = {
                "auth_token": auth_token,
                "meeting_id": room.meeting_id,
                "room_title": room.title,
                "room_id": room.id,
            }

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomModelListApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, meeting_id):
        room_models = RoomModel.objects.filter(room__meeting_id=meeting_id)
        serializer = OutputRoomModelSerializer(room_models, many=True)

        selected_model = RoomModel.objects.filter(
            room__meeting_id=meeting_id, is_select=True).order_by("-created_at").first()

        selected_data = None

        if selected_model:
            model_serializer = OutputRoomModelSerializer(selected_model)
            selected_data = model_serializer.data

        result = {
            "models": serializer.data,
            "selected_model": selected_data,
        }

        return Response(result, status=status.HTTP_200_OK)


class RoomSelectModelApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RoomSelectModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data['meeting_id']
            edit_model_id = serializer.validated_data['edit_model_id']

            # False is select of all previous models
            RoomModel.objects.filter(
                room__meeting_id=meeting_id,
            ).update(is_select=False)

            # True is select of new selected model
            RoomModel.objects.filter(
                room__meeting_id=meeting_id,
                edit_model_id=edit_model_id,
            ).update(is_select=True)

            return Response({"detail": "The Model selected successfully"}, status=status.HTTP_200_OK)


class RoomModelDeleteApi(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = RoomModelDeleteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            meeting_id = serializer.validated_data['meeting_id']
            edit_model_id = serializer.validated_data['edit_model_id']

            # False is select of all previous models
            RoomModel.objects.filter(
                room__meeting_id=meeting_id,
                edit_model_id=edit_model_id,
            ).delete()

            return Response({"detail": "The Model deleted successfully"}, status=status.HTTP_200_OK)


class RoomModelAddApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        input_serializer = InputRoomModelSerializer(data=request.data)

        if input_serializer.is_valid(raise_exception=True):
            meeting_id = input_serializer.validated_data['meeting_id']
            model_id = input_serializer.validated_data['model_id']
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')

            # get room
            room = Room.objects.filter(meeting_id=meeting_id).first()

            # check edit model is exist
            edit_model = None
            if edit_model_id:
                edit_model = EditModel.objects.filter(id=edit_model_id).first()

            # check edit model is not exist create ones
            if not edit_model:
                # get model
                model = Model.objects.filter(id=model_id).first()

                # check display name
                edit_models_count = EditModel.objects.filter(
                    model_id=model_id).count()
                display_name = model.title

                # if model is exits change display name
                if edit_models_count >= 0:
                    display_name = f'{display_name} ({edit_models_count + 1})'

                # create new edit modelw
                edit_model = EditModel.objects.create(
                    user_id=request.user.id,
                    model_id=model_id,
                    display_name=display_name,
                    last_edit=timezone.now()
                )

            # False all room model selected
            RoomModel.objects.filter(
                room_id=room.id,
            ).update(is_select=False)

            # Check room model is exist and select it
            room_model = RoomModel.objects.filter(
                room_id=room.id, edit_model_id=edit_model.id,)
            if room_model:
                room_model.update(is_select=True)
                return Response({"detail": "New Edit model Opened."}, status=status.HTTP_201_CREATED)

            # create new room model
            RoomModel.objects.create(
                room_id=room.id,
                edit_model_id=edit_model.id,
                is_select=True,
            )

            return Response({"detail": "New Edit model Opened."}, status=status.HTTP_201_CREATED)
