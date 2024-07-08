from django.urls import path
from . import views

app_name = "models"

urlpatterns = [
    # models api
    path("", views.ModelListApi.as_view(), name="model-list"),
    path("upload/", views.ModelUploadApi.as_view(), name="model-upload"),
    path("delete/", views.ModelDeleteApi.as_view(), name="model-delete"),
    path("<uuid:id>/", views.ModelDetailApi.as_view(), name="model-detail"),

    # edit model api
    path("edit/", views.EditModelApi.as_view(), name="model-edit"),
    path("edit/<uuid:edit_model_id>/", views.EditModelDetailApi.as_view(), name="model-edit-detail"),
    path("edit/delete/", views.EditModelDeleteApi.as_view(), name="model-edit-delete"),


    # model point api
    path("points/<uuid:edit_model_id>/", views.PointListApi.as_view(), name="model-point"),
    path("points/add/", views.PointAddApi.as_view(), name="model-point-add"),
    path("points/delete/", views.PointDeleteApi.as_view(), name="model-point-delete"),

    # models note api
    path("notes/add/", views.NoteAddApi.as_view(), name="model-note-add"),
    path("notes/delete/", views.NoteDeleteApi.as_view(), name="model-note-delete"),
]
