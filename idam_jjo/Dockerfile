FROM python:3.6-alpine

RUN apk update && \
    apk upgrade && \
    apk add build-base

RUN mkdir /idam_jjo
WORKDIR /idam_jjo

ADD ./requirements.txt /idam_jjo/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ADD . /idam_jjo

CMD ["nameko", "run", "idam_jjo.service", "--config", "idam_jjo/config.yaml"]