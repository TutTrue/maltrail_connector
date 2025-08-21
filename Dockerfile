FROM python:3.11-alpine
ENV CONNECTOR_TYPE=EXTERNAL_IMPORT

# Copy the connector
COPY . maltrail-connector
WORKDIR /maltrail-connector
# Install Python modules
# hadolint ignore=DL3003
RUN apk update && apk upgrade && \
    apk --no-cache add git build-base libmagic libffi-dev libxml2-dev libxslt-dev

RUN pip install poetry && \
    poetry config virtualenvs.create false

RUN poetry install && \
    apk del git build-base


