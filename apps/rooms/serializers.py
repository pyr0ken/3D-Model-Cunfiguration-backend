from rest_framework import serializers
from apps.rooms.models import Room, RoomMember, RoomModel
from apps.users.serializers import UserSerializer


class EnterRoomSerializer(serializers.Serializer):
    room_id = serializers.UUIDField(required=True)


class InputRoomCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)


class RoomDeleteInputSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)


class RoomJoinInputSerializer(serializers.Serializer):
    room_id = serializers.CharField(required=True)


class RoomMemberLeftSerializer(serializers.Serializer):
    meeting_id = serializers.CharField(required=True)
    user_id = serializers.UUIDField(required=True)


class RoomEndSerializer(serializers.Serializer):
    meeting_id = serializers.CharField(required=True)


class RoomListSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField()
    edit_models_count = serializers.IntegerField()

    class Meta:
        model = Room
        fields = (
            "id",
            "title",
            "meeting_id",
            "is_active",
            "members_count",
            "edit_models_count",
            "created_at",
        )


class RoomDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Room
        fields = (
            "id",
            "title",
            "meeting_id",
            "owner",
            "is_active",
            "created_at",
        )


class RoomMemberListSerializer(serializers.ModelSerializer):
    room = RoomDetailSerializer()

    class Meta:
        model = RoomMember
        fields = (
            "id",
            "room",
            "last_join",
        )


class InputRoomModelSerializer(serializers.Serializer):
    meeting_id = serializers.CharField(required=True)
    model_id = serializers.UUIDField(required=True)
    edit_model_id = serializers.UUIDField(required=False)


class OutputRoomModelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='edit_model.id')
    model_id = serializers.UUIDField(source='edit_model.model.id')
    title = serializers.CharField(source='edit_model.model.title')
    display_name = serializers.CharField(source='edit_model.display_name')
    file = serializers.FileField(source='edit_model.model.file')
    created_at = serializers.DateTimeField(
        source='edit_model.model.created_at')

    class Meta:
        model = RoomModel
        fields = (
            "id",
            "title",
            "file",
            "model_id",
            "display_name",
            "created_at",
        )


class RoomSelectModelSerializer(serializers.Serializer):
    meeting_id = serializers.CharField(required=True)
    edit_model_id = serializers.UUIDField(required=True)

class RoomModelDeleteSerializer(RoomSelectModelSerializer):
    ...
