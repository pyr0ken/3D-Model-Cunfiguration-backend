from tkinter import E
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import Model, EditModel, Point


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = (
            "id",
            "title",
            "file",
            "created_at",
        )


class ModelListSerializer(ModelSerializer):
    ...


class ModelDetailSerializer(ModelSerializer):
    ...


class EditModelListSerializer(serializers.ModelSerializer):
    title = serializers.UUIDField(source='model.title')
    file = serializers.FileField(source='model.file')
    size = serializers.SerializerMethodField()
    format = serializers.SerializerMethodField()
    model_id = serializers.UUIDField(source="model.id")

    class Meta:
        model = EditModel
        fields = (
            "id",
            "title",
            "file",
            "model_id",
            "display_name",
            "size",
            "format",
            "created_at"
        )

    def get_size(self, obj):
        return obj.model.file.size

    def get_format(self, obj):
        return obj.model.file.name.split(".")[-1]


class ModelUploadSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    file = serializers.FileField(
        required=True,
        validators=[
            FileExtensionValidator(
                [
                    "glb",
                    "gltf",
                    "obj",
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
    id = serializers.UUIDField(required=True)


class EditModelInputSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)


class EditModelDeleteInputSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)


class EditModelOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = (
            "id",
            "title",
            "file",
        )


class EditModelDetailSerializer(serializers.ModelSerializer):
    title = serializers.UUIDField(source='model.title')
    file = serializers.FileField(source='model.file')
    model_id = serializers.UUIDField(source="model.id")
    # size = serializers.SerializerMethodField()
    # format = serializers.SerializerMethodField()

    class Meta:
        model = EditModel
        fields = (
            "id",
            "title",
            "file",
            "display_name",
            "model_id",
            "created_at"
        )


class PointInputSerializer(serializers.Serializer):
    edit_model_id = serializers.UUIDField(required=True)
    position = serializers.CharField(required=True)
    color = serializers.CharField(required=True)
    radius = serializers.CharField(required=True)
    note = serializers.CharField(required=False)
    image = serializers.CharField(required=False)


class PointNoteSerializer(serializers.Serializer):
    point_id = serializers.UUIDField(required=True)
    note = serializers.CharField(required=True)


class PointImageSerializer(serializers.Serializer):
    point_id = serializers.UUIDField(required=True)
    image = serializers.ImageField(required=True)


class PointOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = (
            "id",
            "position",
            "color",
            "radius",
            "note",
            "image",
        )


class PointDeleteSerializer(serializers.Serializer):
    point_id = serializers.UUIDField(required=True)


class NoteDeleteSerializer(serializers.Serializer):
    point_id = serializers.UUIDField(required=True)
