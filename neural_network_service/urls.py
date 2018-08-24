from django.contrib import admin
from django.urls import path
from .views import TaskStart, TaskManage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('network/', TaskStart.as_view()),
    path('network/<int:pk>/', TaskManage.as_view()),
]
