# Internet Radio Recorder

**Schedule it. Record it. Keep it.**

A self-hosted Internet radio recorder for Docker, NAS and home servers. Configure multiple radio streams, plan recordings on a weekly calendar and keep recordings on your own storage.

[![Current release](https://img.shields.io/github/v/release/sp7uto/internet-radio-recorder?label=release)](https://github.com/sp7uto/internet-radio-recorder/releases/latest) [![CI](https://github.com/sp7uto/internet-radio-recorder/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sp7uto/internet-radio-recorder/actions/workflows/ci.yml) [![MIT](https://img.shields.io/github/license/sp7uto/internet-radio-recorder)](https://github.com/sp7uto/internet-radio-recorder/blob/main/LICENSE)

![Today view of Internet Radio Recorder](https://raw.githubusercontent.com/sp7uto/internet-radio-recorder/main/docs/screenshots/IRR01.png)

*Illustrative historical interface screenshot (version label updated to v2.2.1); not a live production image.*

## Start here

| I want to... | Wiki guide |
| --- | --- |
| Install IRR in Docker | [Getting Started](https://github.com/sp7uto/internet-radio-recorder/wiki/Getting-Started) |
| Add radio streams or inspect recording diagnostics | [Stations and Recording](https://github.com/sp7uto/internet-radio-recorder/wiki/Stations-and-Recording) |
| Plan weekly programmes and recording margins | [Scheduling](https://github.com/sp7uto/internet-radio-recorder/wiki/Scheduling) |
| Manage files, retention, backups and imports | [Storage and Backups](https://github.com/sp7uto/internet-radio-recorder/wiki/Storage-and-Backups) |
| Run IRR on Synology, QNAP or another NAS | [Docker and NAS](https://github.com/sp7uto/internet-radio-recorder/wiki/Docker-and-NAS) |
| Use ICS calendars, notifications and web UI | [Integrations](https://github.com/sp7uto/internet-radio-recorder/wiki/Integrations) |
| Learn about safe automatic updates and recovery | [Updates and Recovery](https://github.com/sp7uto/internet-radio-recorder/wiki/Updates-and-Recovery) |
| Diagnose recording issues | [Troubleshooting](https://github.com/sp7uto/internet-radio-recorder/wiki/Troubleshooting) |
| Protect the web panel | [Security](https://github.com/sp7uto/internet-radio-recorder/wiki/Security) |

## At a glance

- **Recording:** MP3/AAC format selection based on FFprobe; stream copying without re-encoding; manual REC/STOP.
- **Schedules:** multiple programmes per station, weekly patterns, margins, adjacent programmes and overnight recordings.
- **Web interface:** Today, Calendar, Stations, Stream Status, History, Recording Library and Statistics.
- **Local storage:** keep files and settings on NAS disks; retention and storage limits by station.
- **Deployment:** Docker Compose, Synology/Portainer example and public GHCR images.
- **Calendar and alerts:** subscribe to ICS; optional NTFY/webhook notifications.

> [!WARNING]
> **The IRR administration panel has no built-in login.** Keep it on a trusted LAN, behind a VPN such as Tailscale, or behind an authenticated HTTPS reverse proxy. **Never publish port 8080 directly to the Internet.** [More](https://github.com/sp7uto/internet-radio-recorder/wiki/Security).

## Source and support

- [README and screenshots](https://github.com/sp7uto/internet-radio-recorder)
- [Latest stable release](https://github.com/sp7uto/internet-radio-recorder/releases/latest)
- [Docker images in GHCR](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder)
- [Reference documentation](https://github.com/sp7uto/internet-radio-recorder/tree/main/docs)
- [Issues and feature requests](https://github.com/sp7uto/internet-radio-recorder/issues)

**Documentation policy:** These Wiki pages explain the product; the files in [`docs/`](https://github.com/sp7uto/internet-radio-recorder/tree/main/docs) remain the source of truth for detailed configuration, version-specific deployment procedures and troubleshooting. The reference VPS updater is **optional and environment-specific**, not part of a regular Compose installation.
