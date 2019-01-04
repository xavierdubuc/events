import importlib, inspect
from typing import List
from django.utils import timezone
from django.conf import settings
from xd_events.event_subscriber import EventSubscriber
from xd_events.models import Event, EventType
from xd_events.exceptions import EventProcessFailedException


class EventProcessor:
    subscribers = []
    subscribers_support_cache = {}

    def __init__(self):
        for path in settings.XD_EVENTS_SUBSCRIBERS_PATHS:
            importlib.import_module(path)
        for subclass in self.get_all_subclasses(EventSubscriber):
            if not inspect.isabstract(subclass):
                self.subscribers.append(subclass())

    def get_all_subclasses(self, cls):
        subclasses = []
        for subclass in cls.__subclasses__():
            subclasses.append(subclass)
            subclasses.extend(self.get_all_subclasses(subclass))
        return subclasses


    @staticmethod
    def get_unprocessed_events_queryset():
        return Event.objects.filter(processed_at__isnull=True)

    @staticmethod
    def get_unprocessed_events():
        return EventProcessor.get_unprocessed_events_queryset().all()

    def process(self, event: Event):
        event_type = event.type
        if event_type not in self.subscribers_support_cache:
            self._create_cache(event_type)
        subscribers = self.subscribers_support_cache[event_type.name]
        self._call_subscribers(event, subscribers)
        event.processed_at = timezone.now()
        event.save()
        return True

    def _create_cache(self, event_type: EventType):
        self.subscribers_support_cache[event_type.name] = []
        for subscriber in self.subscribers:
            if subscriber.supports(event_type):
                self.subscribers_support_cache[event_type.name].append(subscriber)

    def _call_subscribers(self, event: Event, subscribers: list):
        for subscriber in subscribers:
            succeed = subscriber.handle(event=event)
            if not succeed:
                raise EventProcessFailedException

    @staticmethod
    def get_subscribers(event: Event) -> List[EventSubscriber]:
        if event.type is not None and event.type.name is not None:
            if event.type.name in EventProcessor.subscribers:
                return EventProcessor.subscribers[event.type.name]
        return []
