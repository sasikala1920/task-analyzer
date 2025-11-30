from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.IntegerField(default=1)
    importance = models.IntegerField(default=5)  # 1-10
    dependencies = models.JSONField(default=list, blank=True)  # list of task ids

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"
