from django.db.models import Q
from django.utils import timezone
import numpy as np
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.mixins import AuthenticatedAccessMixin
from apps.models.utils import ai_note_description, convert_2d_to_3d
from .constants import ModelStatusType
from .models import Model, EditModel, Point, ImageTo3dModel
from .serializers import (
    EditModelDeleteInputSerializer,
    EditModelDetailSerializer,
    ModelListSerializer,
    EditModelListSerializer,
    ModelUploadSerializer,
    ModelUploadedSerializer,
    ModelDeleteInputSerializer,
    EditModelInputSerializer,
    NoteDeleteSerializer,
    PointCloudSerializer,
    PointInputSerializer,
    PointOutputSerializer,
    PointDeleteSerializer,
    PointNoteSerializer,
    NoteAiSerializer,
    ImageTo3dModelSerializer,
    SegmentSerializer
)
from model_segmentation.logic import set_point_cloud, clear_state, save_pointcloud, segment_pointcloud


class ModelListApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for listing public, uploaded, and edited models for the authenticated user.
    """

    def get(self, request):
        """
        Retrieve the list of public models, uploaded models by the user, and models edited by the user.
        """
        public_models = Model.objects.filter(status=ModelStatusType.PUBLIC)
        uploaded_models = Model.objects.filter(
            Q(created_by_id=request.user.id) &
            (Q(status=ModelStatusType.UPLOADED) | Q(
                status=ModelStatusType.CREATED_FROM_2D))
        )
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


class ModelUploadApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for handling model uploads and listing uploaded models for the authenticated user.
    """

    def get(self, request):
        """
        Retrieve the list of models uploaded by the authenticated user.
        """
        uploaded_models = Model.objects.filter(
            Q(created_by_id=request.user.id) &
            (Q(status=ModelStatusType.UPLOADED) | Q(
                status=ModelStatusType.CREATED_FROM_2D))
        )
        serializer = ModelUploadedSerializer(uploaded_models, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Upload a new model.
        """
        serializer = ModelUploadSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            file = serializer.validated_data.get("file")
            title = serializer.validated_data.get("title")

            Model.objects.create(
                created_by_id=request.user.id, title=title, file=file, status=ModelStatusType.UPLOADED
            )

            return Response(
                {"detail": "مدل شما با موفقیت آپلود شد."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModelDeleteApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for deleting models.
    """

    def delete(self, request):
        """
        Delete a specified model.
        """
        serializer = ModelDeleteInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            model_id = serializer.validated_data.get("model_id")

            model = Model.objects.filter(id=model_id).first()
            if model:
                model.delete()
                return Response(
                    {"detail": "مدل مورد نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Model not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditModelApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for handling the creation and listing of edited models.
    """

    def get(self, request):
        """
        Retrieve the list of models edited by the authenticated user.
        """
        edited_models = EditModel.objects.filter(
            user_id=request.user.id).order_by("-last_edit")
        edited_models_serializer = EditModelListSerializer(
            edited_models, many=True)
        return Response(edited_models_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create or update an edit model.
        """
        input_serializer = EditModelInputSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            model_id = input_serializer.validated_data['model_id']
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')

            edit_model = None
            if edit_model_id:
                edit_model = EditModel.objects.filter(id=edit_model_id).first()

            if not edit_model:
                model = Model.objects.filter(id=model_id).first()
                if not model:
                    return Response({"detail": "Model not found."}, status=status.HTTP_404_NOT_FOUND)

                edit_models_count = EditModel.objects.filter(
                    model_id=model_id).count()
                display_name = model.title

                if edit_models_count >= 0:
                    display_name = f'{display_name} ({edit_models_count + 1})'

                edit_model = EditModel.objects.create(
                    user_id=request.user.id,
                    model_id=model_id,
                    display_name=display_name,
                    last_edit=timezone.now()
                )

            output_serializer = EditModelDetailSerializer(edit_model)

            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditModelDeleteApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for deleting edited models.
    """

    def delete(self, request):
        """
        Delete a specified edited model.
        """
        serializer = EditModelDeleteInputSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            edit_model_id = serializer.validated_data.get("edit_model_id")

            edit_model = EditModel.objects.filter(id=edit_model_id).first()
            if edit_model:
                edit_model.delete()
                return Response(
                    {"detail": "مدل مورد نظر با موفقیت حذف شد"}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Edit model not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PointListApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for listing points for a specific edited model.
    """

    def get(self, request, edit_model_id):
        """
        Retrieve the list of points for a specific edited model.
        """
        points = Point.objects.filter(edit_model_id=edit_model_id)
        output_serializer = PointOutputSerializer(points, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class PointAddApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for adding points to an edited model.
    """

    def post(self, request):
        """
        Add a new point to an edited model.
        """
        input_serializer = PointInputSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                "edit_model_id")
            position = input_serializer.validated_data.get("position")
            color = input_serializer.validated_data.get("color")
            radius = input_serializer.validated_data.get("radius")

            EditModel.objects.filter(id=edit_model_id).update(
                last_edit=timezone.now())

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


class PointDeleteApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for deleting points from an edited model.
    """

    def delete(self, request):
        """
        Delete a specified point from an edited model.
        """
        input_serializer = PointDeleteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                "edit_model_id")
            point_id = input_serializer.validated_data.get("point_id")

            EditModel.objects.filter(id=edit_model_id).update(
                last_edit=timezone.now())
            point = Point.objects.filter(id=point_id).first()
            if point:
                point.delete()
                return Response(
                    {"detail": "نقطه مورد نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Point not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteAddApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for adding a note to a point in an edited model.
    """

    def post(self, request):
        """
        Add a note to a specific point in an edited model.
        """
        input_serializer = PointNoteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')
            point_id = input_serializer.validated_data.get("point_id")
            note = input_serializer.validated_data.get("note")
            title = input_serializer.validated_data.get("title")

            # Update last edit time
            EditModel.objects.filter(id=edit_model_id).update(
                last_edit=timezone.now())

            # Retrieve the point and add the note
            point = Point.objects.filter(id=point_id).first()
            if point:
                point.note = note
                point.title = title
                point.save()
                return Response(
                    {"detail": "یادداشت با موفقیت ذخیره شد."}, status=status.HTTP_201_CREATED
                )
            return Response(
                {"detail": "Point not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteDeleteApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for deleting a note from a point in an edited model.
    """

    def delete(self, request):
        """
        Delete a note from a specific point in an edited model.
        """
        input_serializer = NoteDeleteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')
            point_id = input_serializer.validated_data.get("point_id")

            # Update last edit time
            EditModel.objects.filter(id=edit_model_id).update(
                last_edit=timezone.now())

            # Retrieve the point and delete the note
            point = Point.objects.filter(id=point_id).first()
            if point:
                point.note = None
                point.save()
                return Response(
                    {"detail": "یادداشت مورد نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Point not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteTitleDeleteApi(AuthenticatedAccessMixin, APIView):
    """
    API endpoint for deleting a note from a point in an edited model.
    """

    def delete(self, request):
        """
        Delete a note from a specific point in an edited model.
        """
        input_serializer = NoteDeleteSerializer(data=request.data)
        if input_serializer.is_valid(raise_exception=True):
            edit_model_id = input_serializer.validated_data.get(
                'edit_model_id')
            point_id = input_serializer.validated_data.get("point_id")

            # Update last edit time
            EditModel.objects.filter(id=edit_model_id).update(
                last_edit=timezone.now())

            # Retrieve the point and delete the note
            point = Point.objects.filter(id=point_id).first()
            if point:
                point.title = None
                point.save()
                return Response(
                    {"detail": "عنوان یادداشت مورد نظر با موفقیت حذف شد."}, status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Point not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteAiApi(AuthenticatedAccessMixin, APIView):
    def post(self, request):
        serializer = NoteAiSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            title = serializer.validated_data.get('title')
            try:
                note = ai_note_description(title)
                return Response({'detail': "توضیحات مورد نظر براساس عنوان نوت  با موفقیت به وجود آمد.", 'generated_note': note}, status=status.HTTP_200_OK)
            except Exception:
                return Response({'error': "مشکلی در برقراری ارتباط پیش آمده است. لطفا دوباره تلاش کنید."}, status=status.HTTP_400_BAD_REQUEST)


class ImageTo3dModelApi(AuthenticatedAccessMixin, APIView):
    def post(self, request):
        serializer = ImageTo3dModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_file = serializer.validated_data.get('file')
            model_title = serializer.validated_data.get('title')

            image_model = ImageTo3dModel.objects.create(image=image_file)

            model_3d = convert_2d_to_3d(image_model.image.path)

            if model_3d:
                Model.objects.create(
                    created_by_id=request.user.id,
                    title=model_title,
                    file=model_3d,
                    status=ModelStatusType.CREATED_FROM_2D
                )

            return Response({'detail': "مدل سه بعدی با موفقیت ساخته شد."}, status=status.HTTP_200_OK)


class PointCloudView(APIView):
    def post(self, request):
        serializer = PointCloudSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            model_name = serializer.validated_data.get('model_name')

            # Call the AI logic function to set the point cloud
            xyz, rgb = set_point_cloud(model_name)

            return Response({"xyz": xyz, "rgb": rgb}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SegmentView(APIView):
    def post(self, request):
        serializer = SegmentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            prompt_point = serializer.validated_data.get("prompt_point")
            prompt_label = serializer.validated_data.get("prompt_label")

            prompt_point_list = [float(i) for i in prompt_point.split(',')]

            # Call the AI logic function to perform segmentation
            segmentation_result = segment_pointcloud(prompt_point_list, prompt_label)

            return Response({"seg": segmentation_result}, status=status.HTTP_200_OK)


class ClearView(APIView):
    def post(self, request):
        # Call the AI logic function to clear the state
        clear_state()
        return Response({"status": "cleared"}, status=status.HTTP_200_OK)


class SaveView(APIView):
    def post(self, request):
        # Call the AI logic function to save the point cloud
        save_pointcloud()
        return Response({"status": "saved"}, status=status.HTTP_200_OK)
