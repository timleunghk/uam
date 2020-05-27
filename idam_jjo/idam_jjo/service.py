import logging
from nameko.rpc import rpc
from idam_jjo import dependencies

class JJOService:

    name = 'idam_jjo_service'

    storage = dependencies.BackendStorage()
    log_dependency = dependencies.LoggingDependency()

    @rpc
    def create_user(self, username, attrs):
        return self.storage.create_user(username, attrs)

    @rpc
    def search_user(self, username, exact=True):
        return self.storage.search_user(username, exact)

    @rpc
    def delete_user(self, username):
        return self.storage.delete_user(username)

    @rpc
    def disable_user(self, username):
        return self.storage.disable_user(username)

    @rpc
    def enable_user(self, username):
        return self.storage.enable_user(username)

    @rpc
    def update_attribute(self, username, changeType, attName, attValue):
        return self.storage.update_attribute(username, changeType, attName, attValue)

    @rpc
    def update_user(self, username, atts):
        return self.storage.update_user(username, atts)

    @rpc
    def update_or_create_user(self, username, attrs):
        if self.storage.search_user(username, True):
            return self.storage.update_user(username, attrs)
        return self.storage.create_user(username, attrs)
