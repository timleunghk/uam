import logging
import cx_Oracle
import datetime
from nameko.dependency_providers import DependencyProvider
from weakref import WeakKeyDictionary

logger = logging.getLogger(__name__)


class BackendStorageImpl:

    # AUDIT_LOG = 'audit_logs'
    # DEDICATED_FIELD_LOG_WRITE_TIME = 'idam_write_time'

    def __init__(self, worker_ctx, db_config):
        self.worker_ctx = worker_ctx
        self.db_config = db_config
        self.db_client = cx_Oracle.connect(
            self.db_config['username'], self.db_config['password'],
            '%s/%s' % (self.db_config['host'], self.db_config['instance']))

    def get_roma_info(self, roma_id):
        cursor = self.db_client.cursor()
        cursor = cursor.execute(
            "select sf_getstaffname_hkid(:roma_id) from dual",
            roma_id=roma_id
        )
        for (result,) in cursor:
            if result is None:
                return None, None
            return tuple(result.split('|'))


class BackendStorage(DependencyProvider):

    def get_dependency(self, worker_ctx):
        return BackendStorageImpl(worker_ctx, self.container.config['ORACLE_CONFIG'])


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
            status = "errored"

        now = datetime.datetime.now()
        worker_started = self.timestamps.pop(worker_ctx)
        difference = now - worker_started
        elapsed = (difference.total_seconds() * 1000) + \
            (now - worker_started).microseconds/1000
        logger.info("Worker:%s - %s - elapsed: %sms",
                    worker_ctx.call_id, status, elapsed)
