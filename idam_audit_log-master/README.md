## A microservice for saving and retrieving Audit log information of UAM

This service depends on nameko. To remotely invoke the service, one must install nameko (i.e. pip install nameko) at the local environment.
To start the service:
1.  go to current folder (same folder as this readme doc)
2.  Run:
    >   nameko run idam_audit_log.service --config idam_audit_log/config.yaml
