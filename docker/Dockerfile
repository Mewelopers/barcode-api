FROM python:3.10.11-bullseye

# Install chromium and postgresql libraries
RUN apt update && apt install -y \
    chromium \
    libpq-dev \
    make

WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt

RUN chmod +x ./docker/docker-entrypoint.sh

RUN useradd -ms /bin/bash fastapi
RUN chown -R fastapi:fastapi /app

USER fastapi
ENTRYPOINT ./docker/docker-entrypoint.sh