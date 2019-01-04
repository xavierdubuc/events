from abc import ABC
from rest_framework import viewsets
from django.contrib.auth import get_user_model
User = get_user_model()
from xd_events.models import Event


class EventFiringViewSet(viewsets.ModelViewSet, ABC):
    entity_name = 'Generic entity'

    def perform_create(self, serializer):
        super(EventFiringViewSet, self).perform_create(serializer)
        self._fire_create_event(self.request, serializer.instance)

    def retrieve(self, request, *args, **kwargs):
        self._fire_get_event(request)
        return super(EventFiringViewSet, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._fire_update_event(request)
        return super(EventFiringViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._fire_update_event(request)
        return super(EventFiringViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._fire_delete_event(request)
        return super(EventFiringViewSet, self).destroy(request, *args, **kwargs)

    # PROTECTED

    def _fire_create_event(self, request, instance):
        return self._fire_event('CREATE', request, instance)

    def _fire_get_event(self, request):
        instance = self.get_object()
        return self._fire_event('GET', request, instance)

    def _fire_update_event(self, request):
        instance = self.get_object()
        return self._fire_event('UPDATE', request, instance)

    def _fire_delete_event(self, request):
        instance = self.get_object()
        return self._fire_event('DELETE', request, instance)

    def _fire_event(self, event_type, request, instance):
        type = self.__format_type(event_type)
        user = request.user if isinstance(request.user, User) else None
        Event.objects.fire(type=type,
                           entity=instance,
                           user=user)

    # PRIVATE
    def __format_type(self, event_type):
        return event_type + '_' + self.entity_name.upper()
