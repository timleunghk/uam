import logging
# import traceback
import datetime
from nameko.dependency_providers import DependencyProvider
from ldap3 import Connection, Server, ALL, ALL_ATTRIBUTES, SUBTREE, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from weakref import WeakKeyDictionary

logger = logging.getLogger(__name__)


class BackendStorageImpl:

    # AUDIT_LOG = 'audit_logs'
    # DEDICATED_FIELD_LOG_WRITE_TIME = 'idam_write_time'

    def __init__(self, worker_ctx, ldap_config):
        self.worker_ctx = worker_ctx
        self.ldap_config = ldap_config
        self.base_dn = ldap_config['base_dn']
        self.hostname = ldap_config['hostname']
        self.portno = ldap_config['portno']
        self.username = ldap_config['username']
        self.pwd = ldap_config['pwd']

    def _ldap_connect(self):
        server = Server(host=self.hostname, port=self.portno,
                        use_ssl=True, get_info=ALL)
        conn = Connection(server, user=self.username,
                          password=self.pwd, auto_bind=True)
        return conn

    def _get_dn(self, username):
        return 'cn={},{}'.format(username, self.base_dn)

    def create_user(self, username, attrs):
        try:
            conn = self._ldap_connect()
            attrs['objectclass'] = ['JJOPerson', 'organizationalPerson',
                                    'top', 'person', 'inetOrgPerson']
            user_dn = self._get_dn(username)
            tmp_attrs = {key: value for (
                key, value) in attrs.items() if attrs[key]}
            result = conn.add(user_dn, attributes=tmp_attrs)
            # result = conn.add(user_dn, attributes=attrs)
            if not result:
                raise Exception(conn.last_error)
            return {'success': True, 'remarks': None}
        except Exception as e:
            # return {'success': False, 'remarks': traceback.format_exc(e)}
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def search_user(self, username, exact):

        def _format_search_filter(username, exact):
            name_array = [username] if exact else ['*%s*' %
                                                   uname for uname in username.split()]
            filter_strings = ['(cn=%s)' % uname for uname in name_array]
            result_string = '(&(objectClass=Person)%s)' % (
                '(&%s)' % ''.join(filter_strings) if name_array else '',)
            logger.debug(result_string)
            return result_string

        try:
            conn = self._ldap_connect()
            entries = conn.extend.standard.paged_search(
                search_base=self.base_dn,
                search_filter=_format_search_filter(username, exact),
                # search_filter='(&(objectClass=Person)(cn={}))'.format(
                #     username),
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

                    att_names = ['cn', 'description', 'employeeType', 'employeeNumber', 'fullName',
                                 'givenName', 'initials', 'Language', 'JUDUserJJO', 'loginDisabled', 'mail', 'sn']

                    for att_name in att_names:
                        if att_name in attributes:
                            if isinstance(attributes[att_name], list):
                                user_dict[att_name] = str(
                                    attributes[att_name][0])
                            elif isinstance(attributes[att_name], bool):
                                if attributes[att_name]:
                                    user_dict[att_name] = 'TRUE'
                                else:
                                    user_dict[att_name] = 'FALSE'
                            else:
                                user_dict[att_name] = str(attributes[att_name])

                    users.append(user_dict)
            return users
        except Exception as e:
            return 'Error : ' + str(e)
        finally:
            conn.unbind()

    def update_attribute(self, username, changeType, attName, attValue):
        try:
            conn = self._ldap_connect()
            if not self.search_user(username, True):
                return {'success': False, 'remarks': 'JJO User %s not found' % username}
            user_dn = self._get_dn(username)
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
            # return {'success': False, 'remarks': traceback.format_exc(e)}
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def delete_user(self, username):
        try:
            conn = self._ldap_connect()
            user_dn = self._get_dn(username)
            result = conn.delete(user_dn)
            if not result:
                raise Exception(conn.last_error)
            return {'success': True, 'remarks': None}
        except Exception as e:
            # return {'success': False, 'remarks': traceback.format_exc(e)}
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        finally:
            conn.unbind()

    def disable_user(self, username):
        return self.update_attribute(username, 'r', 'loginDisabled', 'TRUE')

    def enable_user(self, username):
        return self.update_attribute(username, 'r', 'loginDisabled', 'FALSE')

    def update_user(self, username, atts_new):

        def _gen_insensitive_dict(indict):
            return {key.lower(): value for key, value in indict.items()}

        try:
            attrs_old = self.search_user(username, True)

            if not attrs_old:
                return {'success': False, 'remarks': 'User not found'}
            else:
                attrs_old1 = _gen_insensitive_dict(attrs_old[0])
                attrs_new1 = _gen_insensitive_dict(atts_new)

                if 'loginDisabled' in attrs_old1:
                    attrs_old1.pop('loginDisabled')

                attrs_dels = set(attrs_old1.keys()) - set(attrs_new1.keys())
                attrs_adds = set(attrs_new1.keys()) - set(attrs_old1.keys())
                attrs_upds = set(attrs_new1.keys()).intersection(
                    set(attrs_old1.keys()))

                chgs = {}

                for attrs_upd in attrs_upds:
                    new_value = attrs_new1[attrs_upd]
                    old_value = attrs_old1[attrs_upd]
                    if new_value != old_value:
                        chgs[attrs_upd] = [
                            (MODIFY_REPLACE, [attrs_new1[attrs_upd]])]

                for attrs_del in attrs_dels:
                    chgs[attrs_del] = [(MODIFY_DELETE, [])]

                for attrs_add in attrs_adds:
                    chgs[attrs_add] = [(MODIFY_ADD, [attrs_new1[attrs_add]])]

                user_dn = self._get_dn(username)
                chgs.pop('cn', None)

                if len(chgs) > 0:
                    conn = self._ldap_connect()
                    result = conn.modify(user_dn, chgs)
                    if not result:
                        raise Exception(conn.last_error)
                    return {'success': True, 'remarks': None}
                else:
                    logger.info('--- no changes----')
                    return {'success': True, 'remarks': 'No change is required'}
        except Exception as e:
            logger.error(str(e), exc_info=e)
            return {'success': False, 'remarks': str(e)}
        # finally:
        #     if conn:
        #         conn.unbind()

class BackendStorage(DependencyProvider):

    def get_dependency(self, worker_ctx):
        return BackendStorageImpl(worker_ctx, self.container.config['JJO_CONFIG'])


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
