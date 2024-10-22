from django.urls import path, include
from . import views

app_name = "models"

model_segmentation_api = [
    path('point-cloud/', views.PointCloudView.as_view(), name='point-cloud'),
    path('clear/', views.ClearView.as_view(), name='clear'),
    path('save/', views.SaveView.as_view(), name='save'),
    path('segment/', views.SegmentView.as_view(), name='segment'),
]

urlpatterns = [
    # models api
    path("", views.ModelListApi.as_view(), name="model-list"),
    path("upload/", views.ModelUploadApi.as_view(), name="model-upload"),
    path("delete/", views.ModelDeleteApi.as_view(), name="model-delete"),

    # edit model api
    path("edit/", views.EditModelApi.as_view(), name="model-edit"),
    path("edit/delete/", views.EditModelDeleteApi.as_view(),
         name="model-edit-delete"),


    # model point api
    path("points/<uuid:edit_model_id>/",
         views.PointListApi.as_view(), name="model-point"),
    path("points/add/", views.PointAddApi.as_view(), name="model-point-add"),
    path("points/delete/", views.PointDeleteApi.as_view(),
         name="model-point-delete"),

    # models note api
    path("notes/add/", views.NoteAddApi.as_view(), name="model-note-add"),
    path("notes/delete/", views.NoteDeleteApi.as_view(), name="model-note-delete"),
    path("notes/title/delete/", views.NoteTitleDeleteApi.as_view(), name="model-note-title-delete"),

    # ai api
    path("ai/segmentation/", include(model_segmentation_api)),
    path("ai/note/", views.NoteAiApi.as_view(), name="model-note-ai"),
    path("ai/image-to-3d/", views.ImageTo3dModelApi.as_view(), name="model-note-ai"),
]
