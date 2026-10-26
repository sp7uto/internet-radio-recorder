# Docker and NAS

IRR is designed for a Docker host, including compatible Synology and QNAP NAS devices or a Linux home server.

## Deployment options

| Environment | Recommended starting point |
| --- | --- |
| Linux / VPS with Docker | [Quick Start](https://github.com/sp7uto/internet-radio-recorder/wiki/Getting-Started) and [standard Compose](https://github.com/sp7uto/internet-radio-recorder/blob/main/docker-compose.yml) |
| Synology / Portainer | [Portainer Compose example](https://github.com/sp7uto/internet-radio-recorder/blob/main/docker-compose-portainer.yml) |
| QNAP / Container Station | Adapt the [standard Compose](https://github.com/sp7uto/internet-radio-recorder/blob/main/docker-compose.yml) to existing NAS volumes and ports |

**Important:** the Synology/Portainer file is a **template**. Review its paths, image and permissions rather than copying it verbatim into a production environment. Example NAS directories in the repository are not universal defaults.

## Networking and permissions

- Keep the web service on a **trusted network**; there is no built-in authentication.
- Confirm the host's folders map to `/config` and `/recordings`.
- Ensure UID 1000 inside the container can write to those directories.
- Avoid running a second recorder against the same schedules unintentionally.
- Back up existing configuration before rebuilding or migrating containers.

## Public Docker images

Published GHCR packages: [Internet Radio Recorder container](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder).

The repository also provides local image builds from source. **The automatic guarded-updater configuration documented for the reference VPS is optional and not installed by default on Synology/QNAP.**

Detailed instructions: [Installation](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md), [Configuration](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/CONFIGURATION.md), [Security](https://github.com/sp7uto/internet-radio-recorder/blob/main/SECURITY.md).
