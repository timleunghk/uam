from django.core.management.base import BaseCommand, CommandError
from codetables.models import Section
from common import utils
import csv
import os

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file', nargs=1, type=str)
        # parser.add_argument('--truncate', dest='truncate', action="store_true")
        # parser.set_defaults(truncate=False)
    def handle(self, *args, **options):
        '''
        import all csv file into section table
        '''
        for filename in options['file']:
            if not os.path.isfile(filename):
                raise CommandError('Argument %s is not a file' % filename)
            with open(filename, 'r') as infile:
                csv_reader = csv.reader(infile, delimiter=',')
                instances = []
                for row in csv_reader:
                    code = '%s-%s-%s' % (row[0], row[2], row[4])
                    desc = '%s - %s - %s' % (row[1], row[3], row[5])
                    try:
                        instance = Section.objects.get(code=code)
                        instance.description = desc
                        instance.save()
                    except Section.DoesNotExist:
                        instances.append(Section(code=code, description=desc))
                if len(instances) > 0:
                    Section.objects.bulk_create(instances)

