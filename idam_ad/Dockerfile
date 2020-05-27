FROM python:3.6-alpine

RUN apk update && \
    apk upgrade && \
    apk add build-base

RUN mkdir /idam_ad
WORKDIR /idam_ad

ADD ./requirements.txt /idam_ad/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ADD . /idam_ad

CMD ["nameko", "run", "idam_ad.service", "--config", "idam_ad/config.yaml"]