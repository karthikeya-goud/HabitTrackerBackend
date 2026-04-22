from rest_framework import serializers
from .models import Task, TaskLog


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["updated_at", "created_at", "is_deleted", "is_active"]
        read_only_fields = ["user"]

    def update(self, instance, validated_data):
        validated_data.pop("frequency", None)
        return super().update(instance, validated_data)


class ReorderTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    priority = serializers.IntegerField()


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = "__all__"
        read_only_fields = ["user", "completion_percentage", "score_earned"]
