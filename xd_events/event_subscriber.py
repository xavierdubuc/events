import logging
from abc import ABC, abstractmethod
from xd_events.models import Event, EventType


class EventSubscriber(ABC):
    logger = logging.getLogger('django')

    @abstractmethod
    def handle(self, event: Event) -> bool:
        pass

    @abstractmethod
    def supports(self, event_type: EventType) -> bool:
        pass

    def __str__(self):
        return 'EventSubscriber "' + str(__class__.__name__) + '"'

    def log_info(self, msg):
        self.logger.info(self.get_log_head() + msg)

    def log_error(self, msg):
        self.logger.error(self.get_log_head() + msg)

    def get_log_head(self):
        return '[' + self.__class__.__name__ + '] '
