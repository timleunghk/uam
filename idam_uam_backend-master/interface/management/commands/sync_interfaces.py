from django.core.management.base import BaseCommand
from interface.models import ExternalSync
from interface.actions import sync_interface
# from uam_requests.models import BaseRequest
from common import utils
# from django.utils import timezone
# import json


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        '''
        Synchronize all outstanding interface (e.g. JJO portal, DP, Notes, Send mail, AD)
        '''
        with utils.get_common_nameko_client() as sync_client:
            outstanding_sync = ExternalSync.objects.exclude(
                sync_status=ExternalSync.SYNC_STATUS_COMPLETED).order_by('creation_date')
            for sync_rec in outstanding_sync:
                sync_interface(sync_client, sync_rec)
