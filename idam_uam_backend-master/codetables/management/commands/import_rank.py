from django.core.management.base import BaseCommand, CommandError
from codetables.models import MasterRank
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
                codes = set()
                csv_reader = csv.reader(infile, delimiter=',')
                instances = []
                for row in csv_reader:
                    code = row[0]
                    desc = row[1]
                    if code not in codes:
                        try:
                            instance = MasterRank.objects.get(value=code)
                            instance.description = desc
                            instance.save()
                        except MasterRank.DoesNotExist:
                            instances.append(MasterRank(value=code, description=desc))
                        codes.add(code)
                if instances:
                    MasterRank.objects.bulk_create(instances)

