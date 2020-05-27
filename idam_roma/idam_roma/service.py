from nameko.rpc import rpc
from idam_roma import dependencies


class RomaInfoService:

    name = 'idam_roma_service'

    storage = dependencies.BackendStorage()
    log_dependency = dependencies.LoggingDependency()

    @rpc
    def get_roma_info(self, roma_id):
        return self.storage.get_roma_info(roma_id)
