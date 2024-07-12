from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .constants import ModelStatusType
from .models import Model, EditModel, Point
from .serializers import (
    EditModelDeleteInputSerializer,
    EditModelDetailSerializer,
    ModelListSerializer,
    EditModelListSerializer,
    ModelDetailSerializer,
    ModelUploadSerializer,
    ModelUploadedSerializer,
    ModelDeleteInputSerializer,
    EditModelInputSerializer,
    NoteDeleteSerializer,
    PointInputSerializer,
    PointOutputSerializer,
    PointDeleteSerializer,
    PointNoteSerializer
)


class ModelListApi(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        public_models = Model.objects.filter(status=ModelStatusType.PUBLIC)
        uploaded_models = Model.objects.filter(
            Q(created_by_id=request.user.id) & Q(status=ModelStatusType.UPLOADED))
        edited_models = EditModel.objects.filter(
            user_id=request.user.id).order_by("-last_edit")

        public_models_serializer = ModelListSerializer(
            public_models, many=True)
        uploaded_models_serializer = ModelListSerializer(
            uploaded_models, many=True)
        edited_models_serializer = EditModelListSerializer(
            edited_models, many=True)

        result = {
            "public_models": public_models_serializer.data,
            "uploaded_models": uploaded_models_serializer.data,
            "edited_models": edited_models_serializer.data,
        }

        return Response(result, status=status.HTTP_200_OK)


class ModelDetailApi(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        model = Model.objects.filter(id=id).first()
        serializer = ModelDetailSerializer(model)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ModelUploadApi(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        uploaded_models = Model.objects.filter(
            Q(created_by_id=request.user.id) & Q(status=ModelStatusType.UPLOADED))
        serializer = ModelUploadedSerializer(uploaded_models, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ModelUploadSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            file = serializer.validated_data.get("file")
            title = serializer.validated_data.get("title")

            # create new model
            Model.objects.create(
                created_by_id=request.user.id, title=title, file=file, status=ModelStatusType.UPLOADED
            )

            return Response(
                {"detail": "مدل شما با موفقیت آپلود شد."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModelDeleteApi(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        serializer = ModelDeleteInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            model_id = serializer.validated_data.get("model_id")

            model = Model.objects.filter(id=model_id).first()
            model.delete()

            return Response(
                {"detail": "مدل مورد نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK
            )


class EditModelApi(APIView):
    def get(self, request):
        edited_models = EditModel.objects.filter(user_id=request.user.id).order_by("-last_edit")
        edited_models_serializer = EditModelListSerializer(
            edited_models, many=True)
        return Response(edited_models_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        input_serializer = EditModelInputSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            model_id = input_serializer.validated_data['model_id']
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')

            # check edit model is exist
            edit_model = None
            if edit_model_id:
                edit_model = EditModel.objects.filter(id=edit_model_id).first()

            # check edit model is not exist create ones
            if not edit_model:
                # get model and room
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

            output_serializer = EditModelDetailSerializer(edit_model)

            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditModelDetailApi(APIView):
    def get(self, request, edit_model_id):
        edit_model = EditModel.objects.filter(id=edit_model_id).first()
        serializer = EditModelDetailSerializer(edit_model)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditModelDeleteApi(APIView):
    permission_classes = (IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        serializer = EditModelDeleteInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            edit_model_id = serializer.validated_data.get("edit_model_id")

            edit_model = EditModel.objects.filter(id=edit_model_id).first()
            edit_model.delete()

            return Response(
                {"detail": "مدل مورد نظر با موفقیت حذف شد"}, status=status.HTTP_200_OK
            )


class PointListApi(APIView):
    def get(self, request, edit_model_id):
        points = Point.objects.filter(edit_model_id=edit_model_id)
        output_serializer = PointOutputSerializer(points, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class PointAddApi(APIView):
    def post(self, request):
        input_serializer = PointInputSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                "edit_model_id")
            position = input_serializer.validated_data.get("position")
            color = input_serializer.validated_data.get("color")
            radius = input_serializer.validated_data.get("radius")

            # Update last edit time
            EditModel.objects.filter(
                id=edit_model_id).update(last_edit=timezone.now())

            # Create New Point
            Point.objects.create(
                edit_model_id=edit_model_id,
                position=position,
                color=color,
                radius=radius,
            )

            return Response(
                {"detail": "Point added successfully."}, status=status.HTTP_201_CREATED
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PointDeleteApi(APIView):
    def delete(self, request, *args, **kwargs):
        input_serializer = PointDeleteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')
            point_id = input_serializer.validated_data.get("point_id")

            # Update last edit time
            EditModel.objects.filter(
                id=edit_model_id).update(last_edit=timezone.now())

            point = Point.objects.filter(
                id=point_id,
            )
            point.delete()
            return Response(
                {"detail": "نقطه مورد نظر با موفقیت حذف شد."},
                status=status.HTTP_201_CREATED,
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteAddApi(APIView):
    def post(self, request, *args, **kwargs):
        input_serializer = PointNoteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')
            point_id = input_serializer.validated_data.get("point_id")
            note = input_serializer.validated_data.get("note")

            # Update last edit time
            EditModel.objects.filter(
                id=edit_model_id).update(last_edit=timezone.now())

            point = Point.objects.filter(id=point_id).first()
            point.note = note
            point.save()

            return Response(
                {"detail": "یادداشت با موفقیت ذخیره شد."}, status=status.HTTP_201_CREATED
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteDeleteApi(APIView):
    def delete(self, request, *args, **kwargs):
        input_serializer = NoteDeleteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')
            point_id = input_serializer.validated_data.get("point_id")

            # Update last edit time
            EditModel.objects.filter(
                id=edit_model_id).update(last_edit=timezone.now())

            point = Point.objects.filter(
                id=point_id,
            ).first()
            point.note = None
            point.save()

            return Response(
                {"detail": "یادداشت مورد نظر با موفقیت حذف شد."}, status=status.HTTP_201_CREATED
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
