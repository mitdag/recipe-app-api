FROM python:3.9-alpine3.13
LABEL maintainer="Mithat Daglar"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false

RUN python -m venv /py && \ 
    /py/bin/pip install --upgrade pip && \
    # These are need to compile and install psycopg2 (it is source code version, for psycopg2-binary 
    # we do not need to install these)
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = true ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    # We used build-base postgresql-dev musl-dev just to compile psycopg2. We will not use them any more.
    # Thus we can delete the temporary folder
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
ENV PATH="/py/bin:$PATH"

USER django-user