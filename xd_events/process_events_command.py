import logging
from abc import ABC
from django.core.management.base import BaseCommand
from xd_events.event_processor import EventProcessor
from xd_events.exceptions import EventProcessFailedException

class Command(ABC, BaseCommand):
    processor = EventProcessor()

    def add_arguments(self, parser):
        parser.add_argument('type_id', type=int, nargs='?', default=0)

    def handle(self, *args, **options):
        fails = []
        success_count = 0
        events = EventProcessor.get_unprocessed_events_queryset()
        total_amount = events.count()
        self.stdout.write('Going to process ' + str(total_amount) + ' unprocessed events.')
        type_id = options.get('type_id')
        if type_id != 0:
            events = events.filter(type_id=type_id)
        for event in events.all():
            self.stdout.write('Processing ' + str(event), ending='')
            self.stdout.flush()
            try:
                self.processor.process(event)
                success_count += 1
                self.stdout.write(self.style.SUCCESS(' ... SUCCESS !'))
            except EventProcessFailedException as e:
                logging.getLogger('django').exception(e)
                self.stderr.write(' ... FAIL !')
                fails.append(event)
            except Exception as e:
                logging.getLogger('django').exception(e)
                self.stderr.write(' ... ERROR !')
                fails.append(event)

        self.stdout.write("")
        self.stdout.write('-----')
        self.stdout.write("")

        self.stdout.write(str(total_amount) + ' events have been reviewed.')

        if success_count > 0:
            self.stdout.write(self.style.SUCCESS(str(success_count) + ' events have been successfully processed.'))

        amount_of_fails = len(fails)
        if amount_of_fails > 0:
            self.stderr.write(str(amount_of_fails) + ' events raised an exception during their processing.')
            self.stderr.write('Here are these events : ')
            for fail in fails:
                self.stderr.write('\t' + str(fail))
