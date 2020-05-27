import logging
from nameko.dependency_providers import DependencyProvider
from weakref import WeakKeyDictionary
from ldap3 import Connection, Server, ALL, ALL_ATTRIBUTES, SUBTREE, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
import datetime
from collections import Mapping

logger = logging.getLogger(__name__)


W_EPOCH_STR = '16010101'


class BackendStorageImpl:

    def __init__(self, worker_ctx, ad_config):
        self.worker_ctx = worker_ctx
        self.ad_config = ad_config
        self.base_dn = ad_config['base_dn']
        self.hostname = ad_config['hostname']
        self.username = ad_config['username']
        self.pwd = ad_config['pwd']

    def _ldap_connect(self):
        server = Server(host=self.hostname, use_ssl=True, get_info=ALL)
        conn = Connection(server, user=self.username,
                          password=self.pwd, auto_bind=True)
        return conn

    def create_user(self, username, attrs, pwd, isEnable, groups, ou):
        try:
            conn = self._ldap_connect()
            attrs['objectclass'] = [
                'organizationalPerson', 'top', 'person', 'user']

            if attrs.get('accountExpires'):
                date_str = attrs['accountExpires']
                if '.' in date_str:
                    date_format = '%Y-%m-%d %H:%M:%S.%f'
                else:
                    date_format = '%Y-%m-%d %H:%M:%S'
                attrs['accountExpires'] = datetime.datetime.strptime(
                    date_str.replace('T', ' '), date_format)

            user_dn = 'cn={},ou={},{}'.format(username, ou, self.base_dn)
            result = conn.add(user_dn, attributes=attrs)

            if not result:
                raise Exception(conn.last_error)

            result = conn.extend.microsoft.unlock_account(user=user_dn)

            if not result:
                raise Exception(conn.last_error)

            result = conn.extend.microsoft.modify_password(
                user=user_dn, new_password=pwd)

            if not result:
                raise Exception(conn.last_error)

            if isEnable:
                control = 512
            else:
                control = 514

            enable_account = {"userAccountControl": (
                MODIFY_REPLACE, [control])}
            result = conn.modify(user_dn, changes=enable_account)

            if not result:
                raise Exception(conn.last_error)

            chg_pwd_nt = {"pwdLastSet": (MODIFY_REPLACE, [0])}
            result = conn.modify(user_dn, changes=chg_pwd_nt)

            if not result:
                raise Exception(conn.last_error)

            for group in groups:
                result = conn.extend.microsoft.add_members_to_groups(
                    user_dn, group)
                if not result:
                    raise Exception(conn.last_error)

            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def search_user(self, username, exact=True):
        try:
            conn = self._ldap_connect()
            entries = conn.extend.standard.paged_search(
                search_base=self.base_dn,
                search_filter='(&(objectclass=person)(objectclass=user)( !(objectclass=computer) )(sAMAccountName={}))'.format(
                    username),
                search_scope=SUBTREE,
                attributes='*',
                get_operational_attributes=True,
                paged_size=999,
                generator=True)

            users = []

            for entry in entries:
                if 'attributes' in entry:
                    attributes = entry['attributes']
                    user_dict = {}

                    att_names = ['accountExpires', 'cn', 'distinguishedName', 'description', 'displayName', 'givenName', 'memberOf', 'name', 'mail', 'pwdLastSet', 'sAMAccountName', 'userAccountControl', 'userPrincipalName', 'sn', 'sAMAccountName'
                                 ]

                    for att_name in att_names:
                        if att_name in attributes:
                            if (isinstance(attributes[att_name], list)) and att_name == 'memberOf':
                                user_dict[att_name] = attributes[att_name]
                            elif (isinstance(attributes[att_name], list)) and att_name != 'memberOf':
                                user_dict[att_name] = attributes[att_name][0]
                            else:
                                user_dict[att_name] = attributes[att_name]

                    users.append(user_dict)
            return users
        except Exception as e:
            return 'Error : ' + str(e)
        finally:
            conn.unbind()

    def update_attribute(self, username, changeType, attName, attValue):
        try:
            conn = self._ldap_connect()
            user_dn = 'cn={},{}'.format(username, self.base_dn)

            if changeType == 'a':
                type = MODIFY_ADD
            elif changeType == 'd' or (changeType == 'r' and attValue == ''):
                type = MODIFY_DELETE
                attValue = []
            elif changeType == 'r':
                type = MODIFY_REPLACE

            result = conn.modify(user_dn,  {attName: [(type, attValue)]})
            if not result:
                raise Exception(conn.last_error)
            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def delete_user(self, username):
        try:
            conn = self._ldap_connect()
            user_dn = 'cn={},{}'.format(username, self.base_dn)
            result = conn.delete(user_dn)
            if not result:
                raise Exception(conn.last_error)
            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def disable_user(self, username):
        return self.update_attribute(username, 'r', 'userAccountControl', '514')

    def enable_user(self, username):
        return self.update_attribute(username, 'r', 'userAccountControl', '512')

    def reset_password(self, username, pwd, chg_pwd_nt):
        try:
            conn = self._ldap_connect()
            user_dn = 'cn={},{}'.format(username, self.base_dn)

            result = conn.extend.microsoft.unlock_account(user=user_dn)

            if not result:
                raise Exception(conn.last_error)

            result = conn.extend.microsoft.modify_password(
                user=user_dn, new_password=pwd)

            if not result:
                raise Exception(conn.last_error)

            if chg_pwd_nt.lower() == 'true':
                chg_pwd_nt = {"pwdLastSet": (MODIFY_REPLACE, [0])}
                result = conn.modify(user_dn, changes=chg_pwd_nt)

                if not result:
                    raise Exception(conn.last_error)

            conn.unbind()
            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def user_add_groups(self, username, groups):
        try:
            conn = self._ldap_connect()
            user_dn = 'cn={},{}'.format(username, self.base_dn)

            for group in groups:
                result = conn.extend.microsoft.add_members_to_groups(
                    user_dn, group)
                if not result:
                    raise Exception(conn.last_error)

            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def user_remove_groups(self, username, groups):
        try:
            conn = self._ldap_connect()
            user_dn = 'cn={},{}'.format(username, self.base_dn)

            for group in groups:
                result = conn.extend.microsoft.remove_members_from_groups(
                    user_dn, group)
                if not result:
                    raise Exception(conn.last_error)

            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def create_groups(self, groups):
        try:
            conn = self._ldap_connect()

            for group in groups:
                attrs = {}
                attrs['objectclass'] = ['group', 'top']
                attrs['groupType'] = -2147483646
                attrs['sAMAccountName'] = group
                attrs['description'] = group

                group_dn = 'cn={},{}'.format(group, self.base_dn)
                result = conn.add(group_dn, attributes=attrs)
                if not result:
                    raise Exception(conn.last_error)

            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def delete_groups(self, groups):
        try:
            conn = self._ldap_connect()
            for group in groups:
                result = conn.delete(group)
                if not result:
                    raise Exception(conn.last_error)

            return {'success': True, 'remarks': None}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def search_groups(self, group_name):
        try:
            conn = self._ldap_connect()
            entries = conn.extend.standard.paged_search(
                search_base=self.base_dn,
                search_filter='(&(objectclass=group)(sAMAccountName={}))'.format(
                    group_name),
                search_scope=SUBTREE,
                attributes='*',
                get_operational_attributes=True,
                paged_size=999,
                generator=True)

            users = []

            for entry in entries:
                if 'attributes' in entry:
                    attributes = entry['attributes']
                    user_dict = {}

                    att_names = ['cn', 'groupType',
                                 'member', 'name', 'sAMAccountName']

                    for att_name in att_names:
                        if att_name in attributes:
                            user_dict[att_name] = attributes[att_name]

                    users.append(user_dict)
            return users
        except Exception as e:
            return 'Error : ' + str(e)
        finally:
            conn.unbind()


class BackendStorage(DependencyProvider):

    def get_dependency(self, worker_ctx):
        return BackendStorageImpl(worker_ctx, self.container.config['AD_CONFIG'])


class LoggingDependency(DependencyProvider):

    def __init__(self):
        self.timestamps = WeakKeyDictionary()

    def worker_setup(self, worker_ctx):

        self.timestamps[worker_ctx] = datetime.datetime.now()

        # service_name = worker_ctx.service_name
        # method_name = worker_ctx.entrypoint.method_name

        logger.info("Worker:%s - starting", worker_ctx.call_id)

    def worker_result(self, worker_ctx, result=None, exc_info=None):

        # service_name = worker_ctx.service_name
        # method_name = worker_ctx.entrypoint.method_name

        if exc_info is None:
            status = "completed"
        else:
            status = "error"

        now = datetime.datetime.now()
        worker_started = self.timestamps.pop(worker_ctx)
        difference = now - worker_started
        elapsed = (difference.total_seconds() * 1000) + \
            (now - worker_started).microseconds/1000
        logger.info("Worker:%s - %s - elapsed: %sms",
                    worker_ctx.call_id, status, elapsed)
