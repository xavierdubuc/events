from django.db import models


class EventType(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    description = models.TextField()

    def __str__(self):
        return self.name
