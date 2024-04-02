from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from config.services.swagger import schema_view

admin.site.site_title = "Admin"
admin.site.site_header = "3D Model Configuration"

api_urlpatterns = [
    path("users/", include("apps.users.urls", namespace="users")),
    path("models/", include("apps.models.urls", namespace="models")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_urlpatterns)),
    path(
        "playground/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("silk/", include("silk.urls", namespace="silk")),
]


# Media Assets
if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
