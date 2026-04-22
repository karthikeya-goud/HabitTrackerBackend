from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, TaskLogCreateView, DownloadMonthlyHabitExcel, HabitView

router = DefaultRouter()
router.register(r"task", TaskViewSet, basename="task")

urlpatterns = [
    path("tasklog/", TaskLogCreateView.as_view()),
    path("download/", DownloadMonthlyHabitExcel.as_view()),
    path("habits/monthly/", HabitView.as_view()),
] + router.urls
