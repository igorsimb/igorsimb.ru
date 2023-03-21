from django.urls import path
from .views import IndexView, Ez2TaskView

app_name = "core"
urlpatterns = [
    path('', IndexView.as_view(), name='main'),
    path('ez2task/', Ez2TaskView.as_view(), name='ez2task'),
]