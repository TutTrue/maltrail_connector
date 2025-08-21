# OpenCTI External Ingestion Connector Template

<!--
General description of the connector
* What it does
* How it works
* Special requirements
* Use case description
* ...
-->

Table of Contents

- [OpenCTI External Ingestion Connector Template](#opencti-external-ingestion-connector-template)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Requirements](#requirements)
  - [Configuration variables](#configuration-variables)
    - [OpenCTI environment variables](#opencti-environment-variables)
    - [Base connector environment variables](#base-connector-environment-variables)
    - [Connector extra parameters environment variables](#connector-extra-parameters-environment-variables)
  - [Deployment](#deployment)
    - [Docker Deployment](#docker-deployment)
      - [Using Pre-built Image from GitHub Container Registry](#using-pre-built-image-from-github-container-registry)
      - [Building Your Own Image](#building-your-own-image)
      - [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)
    - [Manual Deployment](#manual-deployment)
  - [Usage](#usage)
  - [Behavior](#behavior)
  - [Debugging](#debugging)
  - [Additional information](#additional-information)

## Introduction

## Installation

### Requirements

- OpenCTI Platform >= 6...

## Configuration variables

There are a number of configuration options, which are set either in `docker-compose.yml` (for Docker) or
in `config.yml` (for manual deployment).

### OpenCTI environment variables

Below are the parameters you'll need to set for OpenCTI:

| Parameter     | config.yml | Docker environment variable | Mandatory | Description                                          |
|---------------|------------|-----------------------------|-----------|------------------------------------------------------|
| OpenCTI URL   | url        | `OPENCTI_URL`               | Yes       | The URL of the OpenCTI platform.                     |
| OpenCTI Token | token      | `OPENCTI_TOKEN`             | Yes       | The default admin token set in the OpenCTI platform. |

### Base connector environment variables

Below are the parameters you'll need to set for running the connector properly:

| Parameter       | config.yml | Docker environment variable | Default         | Mandatory | Description                                                                              |
|-----------------|------------|-----------------------------|-----------------|-----------|------------------------------------------------------------------------------------------|
| Connector ID    | id         | `CONNECTOR_ID`              | /               | Yes       | A unique `UUIDv4` identifier for this connector instance.                                |
| Connector Type  | type       | `CONNECTOR_TYPE`            | EXTERNAL_IMPORT | Yes       | Should always be set to `EXTERNAL_IMPORT` for this connector.                            |
| Connector Name  | name       | `CONNECTOR_NAME`            |                 | Yes       | Name of the connector.                                                                   |
| Connector Scope | scope      | `CONNECTOR_SCOPE`           |                 | Yes       | The scope or type of data the connector is importing, either a MIME type or Stix Object. |
| Log Level       | log_level  | `CONNECTOR_LOG_LEVEL`       | info            | Yes       | Determines the verbosity of the logs. Options are `debug`, `info`, `warn`, or `error`.   |

### Connector extra parameters environment variables

Below are the parameters you'll need to set for the connector:

| Parameter    | config.yml   | Docker environment variable | Default | Mandatory | Description |
|--------------|--------------|-----------------------------|---------|-----------|-------------|
| API base URL | api_base_url |                             |         | Yes       |             |
| API key      | api_key      |                             |         | Yes       |             |

## Deployment

### Docker Deployment

#### Using Pre-built Image from GitHub Container Registry

The easiest way to deploy this connector is using the pre-built image from GitHub Container Registry:

```shell
# Pull the latest image
docker pull ghcr.io/yourusername/maltrail-connector:latest

# Run with docker-compose
GITHUB_REPOSITORY_OWNER=yourusername docker-compose up -d
```

#### Building Your Own Image

If you need to build the image yourself:

```shell
# Build the image locally
docker build . -t ghcr.io/yourusername/maltrail-connector:latest

# Push to your GitHub Container Registry (optional)
docker push ghcr.io/yourusername/maltrail-connector:latest
```

#### GitHub Actions CI/CD Setup

This repository includes automated Docker image building and publishing to GitHub Container Registry via GitHub Actions.

**Required GitHub Secrets:**

The workflow automatically uses the built-in `GITHUB_TOKEN` secret, so no additional secrets are required! The workflow will:

- Automatically authenticate using your repository's GitHub token
- Push images to `ghcr.io/yourusername/maltrail-connector`
- Use your GitHub username and repository name automatically

**Note:** Make sure your repository has the "Packages" feature enabled in Settings → General → Features.

**Automated Builds:**

The GitHub Actions workflow will automatically:
- Build multi-platform images (AMD64 and ARM64)
- Push images to GitHub Container Registry on every push to `main` branch
- Create versioned tags when you create Git tags (e.g., `v1.0.0`)
- Use Docker layer caching for faster builds

**Manual Trigger:**

You can also manually trigger the build process:
1. Go to your repository → Actions → "Build and Push to GitHub Container Registry"
2. Click "Run workflow" → "Run workflow"

Make sure to replace the environment variables in `docker-compose.yml` with the appropriate configurations for your
environment. Then, start the docker container with the provided docker-compose.yml

```shell
# Set your GitHub username and start the container
GITHUB_REPOSITORY_OWNER=yourusername docker-compose up -d
```

### Manual Deployment

Create a file `config.yml` based on the provided `config.yml.sample`.

Replace the configuration variables (especially the "**ChangeMe**" variables) with the appropriate configurations for
you environment.

Install the required python dependencies (preferably in a virtual environment):

```shell
pip3 install -r requirements.txt
```

Then, start the connector from recorded-future/src:

```shell
python3 main.py
```

## Usage

After Installation, the connector should require minimal interaction to use, and should update automatically at a regular interval specified in your `docker-compose.yml` or `config.yml` in `duration_period`.

However, if you would like to force an immediate download of a new batch of entities, navigate to:

`Data management` -> `Ingestion` -> `Connectors` in the OpenCTI platform.

Find the connector, and click on the refresh button to reset the connector's state and force a new
download of data by re-running the connector.

## Behavior

<!--
Describe how the connector functions:
* What data is ingested, updated, or modified
* Important considerations for users when utilizing this connector
* Additional relevant details
-->


## Debugging

The connector can be debugged by setting the appropiate log level.
Note that logging messages can be added using `self.helper.connector_logger,{LOG_LEVEL}("Sample message")`, i.
e., `self.helper.connector_logger.error("An error message")`.

<!-- Any additional information to help future users debug and report detailed issues concerning this connector -->

## Additional information

<!--
Any additional information about this connector
* What information is ingested/updated/changed
* What should the user take into account when using this connector
* ...
-->
