from django.db import models


class EventParameter(models.Model):
    # data
    key = models.CharField(max_length=250)
    value = models.TextField()
    # related event
    event = models.ForeignKey('xd_events.Event', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.key
