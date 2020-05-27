from django.core.management.base import BaseCommand
from uam_requests.models import AuditLog
from rest_framework.parsers import JSONParser
from common import utils
from django.utils import timezone
import json

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        '''
        Synchronize all audit log to remote audit log services and then remove successfully synced local logs 
        '''
        with utils.get_nameko_client_for_audit_log() as client:
            result_map = {}
            for log in AuditLog.objects.filter(sync_time__isnull=True):
                tmpdata = json.loads(log.audit_log_data)
                tmpdata['src_log_time'] = log.log_time
                result_map[log.id] = client.idam_audit_log_service.write_log(tmpdata)
                if result_map[log.id].get('success', False):
                    log.sync_time = timezone.now()
                    log.save()
            # delete_ids = [id for id, result in result_map.items() if result.get('success', False)]
            # AuditLog.objects.filter(pk__in=delete_ids).delete()

