FROM python:3.6-alpine

RUN apk update && \
    apk upgrade && \
    apk add build-base

RUN mkdir /idam_auditlog
WORKDIR /idam_auditlog

ADD ./requirements.txt /idam_auditlog/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD . /idam_auditlog

CMD ["nameko", "run", "idam_audit_log.service", "--config", "idam_audit_log/config.yaml"]