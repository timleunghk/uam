from nameko.rpc import rpc
from idam_audit_log import dependencies

class AuditLogService:

    name = 'idam_audit_log_service'

    storage = dependencies.BackendStorage()

    @rpc
    def write_log(self, data):
        result = self.storage.write_log(data)
        result['success'] = True
        return result

    @rpc
    def get_request_log(self, request_id):
        return self.storage.get_request_log(request_id)