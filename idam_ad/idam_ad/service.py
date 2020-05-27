from nameko.rpc import rpc
from idam_ad import dependencies
from datetime import datetime

class ADService:

    name = 'idam_ad_service'

    storage = dependencies.BackendStorage()
    log_dependency = dependencies.LoggingDependency()

    @rpc
    def create_user(self, username, attrs, pwd, isEnable, groups):
        return self.storage.create_user(username, attrs, pwd, isEnable, groups)

    @rpc
    def search_user(self, username):
        return self.storage.search_user(username)

    @rpc
    def update_attribute(self, username, changeType, attName, attValue):
        return self.storage.update_attribute(username, changeType, attName, attValue)

    @rpc
    def user_add_groups(self, username, groups):
        return self.storage.user_add_groups(username, groups)

    @rpc
    def user_remove_groups(self, username, groups):
        return self.storage.user_remove_groups(username, groups)

    @rpc
    def create_groups(self, groups):
        return self.storage.create_groups(groups)

    @rpc
    def delete_groups(self, groups):
        return self.storage.delete_groups(groups)

    @rpc
    def search_groups(self, group):
        return self.storage.search_groups(group)

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
    def reset_password(self, username, password, chg_pwd_nt):
        return self.storage.reset_password(username, password, chg_pwd_nt)

    @rpc
    def get_date(self, tmp_date):
        # tmp_datetime = datetime.strptime(tmp_date)
        print(tmp_date)
        # print(datetime.strptime(tmp_date, '%Y-%m-%dT%H:%M:%S.%z'))
        print(isinstance(tmp_date, str))
        return tmp_date