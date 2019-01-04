from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from xd_events.models import EventType, EventParameter
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class EventManager(models.Manager):
    @transaction.atomic
    def fire(self, type, entity=None, user=None, created_at=None, params=None):
        if not type:
            raise ValueError('An event must have a type !')

        event_type, new_event_type_has_been_created = EventType.objects.get_or_create(name=type)
        if created_at is None:
            created_at = timezone.now()
        event = self.model(
            type=event_type,
            entity=entity,
            user=user if user else None,
            created_at=created_at
        )
        event.save()

        if isinstance(params, dict):
            params = self._to_event_params(params, event)
        if params is not None:
            for param in params:
                param.event = event
                param.save()

        return event

    def _to_event_params(self, params, event=None):
        event_params = []
        for key, value in params.items():
            event_param = EventParameter(key=key, value=value, event=event)
            event_params.append(event_param)
        return event_params


class Event(models.Model):
    objects = EventManager()
    created_at = models.DateTimeField()
    processed_at = models.DateTimeField(null=True)
    # Event type (USER_CREATE, ... )
    type = models.ForeignKey('xd_events.EventType', on_delete=models.SET_NULL, blank=True, null=True)
    # Concerned model
    entity_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        related_name='event_content_type'
    )
    entity_object_id = models.PositiveIntegerField(null=True)
    entity = GenericForeignKey('entity_content_type', 'entity_object_id')
    # Applying user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='events')

    def __str__(self):
        return 'Event #' + str(self.pk) + ' (' + self.type.name + ')'

    def save(self, *args, **kwargs):
        if not self.id and not self.created_at:
            self.created_at = timezone.now()
        return super(Event, self).save(*args, **kwargs)
