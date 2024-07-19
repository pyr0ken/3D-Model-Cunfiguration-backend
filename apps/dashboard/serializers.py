from rest_framework import serializers
from apps.rooms.models import Room, RoomMember
from apps.models.models import EditModel


class RoomMemberDashboardSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ('title', 'meeting_id', 'members')
        
    def get_members(self, obj):
        return RoomMember.objects.filter(room_id=obj.id).count()


class DashboardEditModelSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField()

    class Meta:
        model = EditModel
        fields = ('display_name', 'points')
