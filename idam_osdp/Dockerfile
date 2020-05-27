FROM python:3.6-alpine

RUN apk update && \
    apk upgrade && \
    apk add build-base

RUN mkdir /idam_osdp
WORKDIR /idam_osdp

ADD ./requirements.txt /idam_osdp/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ADD . /idam_osdp

CMD ["nameko", "run", "idam_osdp.service", "--config", "idam_osdp/config.yaml"]