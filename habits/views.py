from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


from .serializers import TaskSerializer, ReorderTaskSerializer
from .models import Task, TaskLog

from django.db import transaction
from django.db.models.aggregates import Max
from .utils import *


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user, is_deleted=False, is_active=True
        ).order_by("priority")

    def list(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        user = request.user

        result = []

        for task in tasks:
            start, end = get_period_range(task.frequency)

            log = TaskLog.objects.filter(
                user=user,
                task=task,
                created_at__range=(start, end),
            ).last()

            # total_value = logs.aggregate(total=Max("value"))["total"] or 0

            total_value = 0 if log is None else log.value

            completion = calculate_completion(total_value, task.target_value, task.type)

            result.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "type": task.type,
                    "target_value": task.target_value,
                    "max_score_per_day": task.max_score_per_day,
                    "is_soft_deleted": task.is_soft_deleted,
                    "frequency": task.frequency,
                    # 🔥 NEW FIELDS
                    "current_value": total_value,
                    "completion": completion,
                }
            )

        return Response(result)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_soft_deleted = True
        instance.save()
        return Response({"message": "Soft deleted"}, status=204)

    @action(detail=True, methods=["post"])
    def hard_delete(self, request, pk=None):
        task = Task.objects.get(pk=pk, user=request.user)
        task.is_deleted = True
        task.save()
        return Response({"message": "Deleted"})

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        task = Task.objects.get(pk=pk, user=request.user)
        task.is_soft_deleted = False
        task.save()
        return Response({"message": "Restored"})

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        serializer = ReorderTaskSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        objs = []
        for item in serializer.validated_data:
            task = Task.objects.get(id=item["id"], user=request.user)
            task.priority = item["priority"]
            objs.append(task)

        with transaction.atomic():
            Task.objects.bulk_update(objs, ["priority"])

        return Response({"message": "Reordered"})


class TaskLogCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        task_id = request.data.get("id")
        value = float(request.data.get("value", 0))

        try:
            task = Task.objects.get(id=task_id, user=user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        completion = calculate_completion(value, task.target_value, task.type)
        score = calculate_score(completion, task.max_score_per_day)

        start, end = get_period_range(task.frequency)
        log = TaskLog.objects.filter(
            user=user,
            task=task,
            created_at__range=(start, end),
        ).last()

        isToday = False if log is None else is_today(log.created_at)

        if log is None or not isToday:
            log = TaskLog.objects.create(
                user=user,
                task=task,
                value=value,
                target_value=task.target_value,
                type=task.type,
                unit=task.unit,
                completion_percentage=completion,
                score_earned=score,
            )
        else:
            log.value = value
            log.completion_percentage = completion
            log.score_earned = score
            log.target_value = task.target_value
            log.type = task.type
            log.unit = task.unit

            log.save()

        return Response(
            {
                "id": log.id,
                "completion": completion,
                "score": score,
            },
            status=201,
        )


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone

from .models import TaskLog
from .utils import generate_excel


class DownloadMonthlyHabitExcel(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # start of month
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # fetch logs for current month
        logs = (
            TaskLog.objects.filter(user=user, created_at__range=(start, now))
            .select_related("task")
            .order_by("task_id", "created_at")
        )

        # generate workbook
        wb = generate_excel(logs)

        # response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        filename = f"habit_report_{now.strftime('%B_%Y')}.xlsx"
        response["Content-Disposition"] = f'inline; filename="{filename}"'

        wb.save(response)
        return response


from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from collections import defaultdict

from .models import TaskLog


class HabitView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # ❗ only till yesterday
        end_date = today - timedelta(days=1)

        # ❗ start of current month
        start_date = end_date.replace(day=1)

        # all dates in month till yesterday
        dates = []
        d = start_date
        while d <= end_date:
            dates.append(d)
            d += timedelta(days=1)

        logs = TaskLog.objects.filter(
            user=user, created_at__date__range=(start_date, end_date)
        ).select_related("task")

        # 🔥 group by type
        grouped = {
            "daily": {},
            "weekly": {},
            "monthly": {},
        }

        for log in logs:
            t = log.task
            freq = t.frequency  # assume this exists

            if t.id not in grouped[freq]:
                grouped[freq][t.id] = {
                    "id": t.id,
                    "title": t.title,
                    "type": t.type,
                    "target": t.target_value,
                    "unit": t.unit,
                    "logs": {},
                }

            grouped[freq][t.id]["logs"][str(log.created_at.date())] = {
                "value": log.value
            }

        return Response(
            {
                "dates": [d.strftime("%d %b") for d in dates],
                "date_keys": [str(d) for d in dates],
                "data": {
                    "daily": list(grouped["daily"].values()),
                    "weekly": list(grouped["weekly"].values()),
                    "monthly": list(grouped["monthly"].values()),
                },
            }
        )
