FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt



# RUN sed -i -e s/dl-cdn/dl-4/ /etc/apk/repositories && \
#     apk add --update --no-cache postgresql-client
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk add --update --no-cache postgresql-client

RUN apk add --update --no-cache jpeg-dev

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip3 install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D appuser
RUN chown -R appuser:appuser /vol/
RUN chmod -R 755 /vol/web
USER appuser