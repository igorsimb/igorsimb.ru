from django.urls import path
from .views import IndexView, Ez2TaskView, StoreProjectView, MPMonitorView

app_name = "core"
urlpatterns = [
    path("", IndexView.as_view(), name="main"),
    path("mp-monitor-project/", MPMonitorView.as_view(), name="mp_monitor"),
    path("ez2task-project/", Ez2TaskView.as_view(), name="ez2task"),
    path("store-project/", StoreProjectView.as_view(), name="store_project"),
]
