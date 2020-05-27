from arango import ArangoClient
from nameko.dependency_providers import DependencyProvider
from datetime import datetime

class BackendStorageImpl:

    AUDIT_LOG = 'audit_logs'
    DEDICATED_FIELD_LOG_WRITE_TIME = 'idam_write_time'

    def __init__(self, worker_ctx, db_config):
        self.worker_ctx = worker_ctx
        self.db_config = db_config
        self.db_client = ArangoClient(protocol=self.db_config['protocol'], host=self.db_config['host'])
        self.db = self.db_client.db(self.db_config['db'], username=self.db_config['username'], password=self.db_config['password'])
        self._prepare_db_structure(self.db)

    def _prepare_db_structure(self, db):
        if db.has_collection(self.AUDIT_LOG):
            audit_logs = db.collection(self.AUDIT_LOG)
        else:
            audit_logs = db.create_collection(self.AUDIT_LOG)
        
    # def write_log(self, data, extra_info):
    #     audit_logs = self.db.collection(self.AUDIT_LOG)
    #     now = datetime.now()
    #     data[self.DEDICATED_FIELD_LOG_WRITE_TIME] = now.isoformat()
    #     if extra_info is not None:
    #         data = {**data, **extra_info}
    #     audit_logs.insert(data)

    def write_log(self, data):
        audit_logs = self.db.collection(self.AUDIT_LOG)
        now = datetime.now()
        data[self.DEDICATED_FIELD_LOG_WRITE_TIME] = now.isoformat()
        # if extra_info is not None:
        #     data = {**data, **extra_info}
        return audit_logs.insert(data)

    def _format_out_log_entry(self, doc):
        EXCLUDE_FIELD = ['_id', '_key', '_rev']
        outdoc = { key: value for key, value in doc.items() if key not in EXCLUDE_FIELD }
        return outdoc
    def get_request_log(self, request_id):
        # print(request_id)
        result =  [self._format_out_log_entry(doc) for doc in self.db.aql.execute('FOR doc IN %s FILTER doc.request_id == @request_id SORT doc.src_log_time, doc.last_modification_date RETURN doc' % self.AUDIT_LOG, bind_vars={'request_id': request_id})]
        # print(tmprec)
        return result

class BackendStorage(DependencyProvider):

    def get_dependency(self, worker_ctx):
        return BackendStorageImpl(worker_ctx, self.container.config['ARANGO_CONFIG'])