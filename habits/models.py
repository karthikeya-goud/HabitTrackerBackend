from django.db import models

TYPE_CHOICES = [
    ("checkbox", "Checkbox"),
    ("slider", "Slider"),
    ("target", "Target"),
]

UNITS_TYPES = [
    ("meters", "Meters"),
    ("kilometers", "Kilometers"),
    ("liters", "Liters"),
    ("milliliters", "Milliliters"),
    ("grams", "Grams"),
    ("kilograms", "Kilograms"),
    ("count", "Counts"),
    (None, "None"),
]


class Task(models.Model):

    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="tasks"
    )

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True, null=True)

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    target_value = models.FloatField(null=True, blank=True)
    unit = models.CharField(choices=UNITS_TYPES, max_length=50, null=True, blank=True)

    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)

    max_score_per_day = models.FloatField(default=10)

    priority = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_soft_deleted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        last = Task.objects.filter(user=self.user).order_by("-priority").first()
        self.priority = (last.priority + 1) if last else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}-{self.user}"


class TaskLog(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    target_value = models.FloatField(null=True, blank=True)
    value = models.FloatField(default=0)
    completion_percentage = models.FloatField(default=0)
    score_earned = models.FloatField(default=0)
    unit = models.CharField(choices=UNITS_TYPES, max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task.title}"
