import csv
import os

from django.core.management.base import BaseCommand, CommandError
from uam_users.models import UamUser


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file', nargs=1, type=str)
        # parser.add_argument('--truncate', dest='truncate', action="store_true")
        # parser.set_defaults(truncate=False)

    def _convert_rec(self, rec):
        tmprec = {k.lower().strip(): v for k, v in rec.items()}
        for key, value in tmprec.items():
            if value is not None:
                value = value.strip() if value.strip() != 'NULL' else None
            tmprec[key] = value
        return tmprec

    def handle(self, *args, **options):
        '''
        import all csv file into section table
        '''
        for filename in options['file']:
            if not os.path.isfile(filename):
                raise CommandError('Argument %s is not a file' % filename)
            with open(filename, 'r', encoding='utf-8-sig') as infile:
                csv_reader = csv.DictReader(infile)
                for rec in csv_reader:
                    tmprec = self._convert_rec(rec)
                    try:
                        user = UamUser.objects.get(uam_id=tmprec['uid'])
                        user.surname = tmprec['surname']
                        user.surname_chinese = tmprec['surname_chinese']
                        user.given_name = tmprec['givenname']
                        user.given_name_chinese = tmprec['givenname_chinese']
                        user.post_title = tmprec['postaddressing_title']
                        user.account_type = UamUser.ACCOUNT_TYPE_JJO if tmprec[
                            'is_jjo_flag'] else UamUser.ACCOUNT_TYPE_NON_JJO
                        user.oa_need_windows_login = True
                        user.ad_windows_login_name = tmprec['loginname']
                        user.save()
                    except UamUser.DoesNotExist:
                        user = UamUser(
                            surname=tmprec['surname'],
                            surname_chinese=tmprec['surname_chinese'],
                            given_name=tmprec['givenname'],
                            given_name_chinese=tmprec['givenname_chinese'],
                            post_title=tmprec['postaddressing_title'],
                            account_type=UamUser.ACCOUNT_TYPE_JJO if tmprec[
                                'is_jjo_flag'] else UamUser.ACCOUNT_TYPE_NON_JJO,
                            oa_need_windows_login=True,
                            ad_windows_login_name=tmprec['loginname'],
                            uam_id=int(tmprec['uid']),
                        )
                        user.save()
