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
    # These are needed to compile and install psycopg2 (it is source code version, for 
    # psycopg2-binary we do not need to install these)
    # (Psycopg is the most popular PostgreSQL database adapter for the Python)
    # jpeg-dev is a dependency for Pillow (Python imaging library)
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
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
        django-user && \
        # these directories will be used for static files and images
        mkdir -p /vol/web/media && \
        mkdir -p /vol/web/static && \
        chown -R django-user:django-user /vol && \
        # django-user and users in django-user group can make any changes in /vol (755)
        chmod -R 755 /vol
        
ENV PATH="/py/bin:$PATH"

USER django-user