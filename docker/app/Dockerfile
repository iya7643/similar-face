FROM python:3.10.13

RUN apt-get update \
    && apt-get install -y vim \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY ./app/requirements.txt /tmp/requirements.txt

RUN pip install -U pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /var/www/app
