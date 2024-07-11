from rest_framework import serializers
from apps.rooms.models import Room
from apps.models.models import EditModel


class RoomMemberDashboardSerializer(serializers.ModelSerializer):
    members = serializers.IntegerField()

    class Meta:
        model = Room
        fields = ('title', 'meeting_id', 'members')


class DashboardEditModelSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField()

    class Meta:
        model = EditModel
        fields = ('display_name', 'points')
