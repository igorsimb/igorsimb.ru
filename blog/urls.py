from django.urls import path

from .views import (
    BlogDashboardView,
    BlogDetailView,
    BlogImageUploadView,
    BlogEditorPreviewView,
    BlogEditorSaveView,
    BlogEditorView,
    BlogIndexView,
)

app_name = "blog"

urlpatterns = [
    path("", BlogIndexView.as_view(), name="index"),
    path("dashboard/", BlogDashboardView.as_view(), name="dashboard"),
    path("write/", BlogEditorView.as_view(), name="editor_create"),
    path("write/preview/", BlogEditorPreviewView.as_view(), name="editor_preview"),
    path("write/save/", BlogEditorSaveView.as_view(), name="editor_save"),
    path(
        "write/upload-image/", BlogImageUploadView.as_view(), name="editor_upload_image"
    ),
    path("write/<int:pk>/", BlogEditorView.as_view(), name="editor"),
    path("<slug:slug>/", BlogDetailView.as_view(), name="detail"),
]
