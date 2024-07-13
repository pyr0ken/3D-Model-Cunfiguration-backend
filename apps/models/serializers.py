from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import Model, EditModel, Point


class ModelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = (
            "id",
            "title",
            "file",
            "created_at",
        )


class EditModelListSerializer(serializers.ModelSerializer):
    title = serializers.UUIDField(source='model.title')
    file = serializers.FileField(source='model.file')
    model_id = serializers.UUIDField(source="model.id")
    points_count = serializers.SerializerMethodField()
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = EditModel
        fields = (
            "id",
            "title",
            "file",
            "model_id",
            "display_name",
            "last_edit",
            "created_at",
            "points_count",
            "notes_count",
        )

    def get_points_count(self, obj):
        return Point.objects.filter(edit_model_id=obj.id).count()

    def get_notes_count(self, obj):
        return Point.objects.filter(edit_model_id=obj.id).exclude(note=None).count()


class ModelUploadSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    file = serializers.FileField(
        required=True,
        validators=[
            FileExtensionValidator(
                [
                    "glb",
                    "gltf",
                ]
            )
        ],
    )


class ModelUploadedSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    format = serializers.SerializerMethodField()

    class Meta:
        model = Model
        fields = (
            "id",
            "title",
            "file",
            "size",
            "format",
            "created_at",
        )

    def get_size(self, obj):
        return obj.file.size

    def get_format(self, obj):
        return obj.file.name.split(".")[-1]


class ModelDeleteInputSerializer(serializers.Serializer):
    model_id = serializers.UUIDField(required=True)


class EditModelInputSerializer(serializers.Serializer):
    model_id = serializers.UUIDField(required=True)
    edit_model_id = serializers.UUIDField(required=False)


class EditModelDeleteInputSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)


class EditModelDetailSerializer(serializers.ModelSerializer):
    title = serializers.UUIDField(source='model.title')
    file = serializers.FileField(source='model.file')
    model_id = serializers.UUIDField(source="model.id")

    class Meta:
        model = EditModel
        fields = (
            "id",
            "title",
            "file",
            "display_name",
            "last_edit",
            "model_id",
            "created_at"
        )


class PointInputSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)
    position = serializers.CharField(required=True)
    color = serializers.CharField(required=True)
    radius = serializers.CharField(required=True)
    note = serializers.CharField(required=False)


class PointNoteSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)
    point_id = serializers.UUIDField(required=True)
    note = serializers.CharField(required=True)


class PointOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = (
            "id",
            "position",
            "color",
            "radius",
            "note",
        )


class PointDeleteSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)
    point_id = serializers.UUIDField(required=True)


class NoteDeleteSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)
    point_id = serializers.UUIDField(required=True)
