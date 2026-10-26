<p align="center">
  <img src="static/favicon.svg" width="80" height="80" alt="Internet Radio Recorder logo">
</p>

<h1 align="center">Internet Radio Recorder</h1>

<p align="center">
  <strong>Schedule it. Record it. Keep it.</strong><br>
  Self-hosted Internet radio recording for your NAS or home server.
</p>

<p align="center">
  <a href="https://github.com/sp7uto/internet-radio-recorder/actions/workflows/ci.yml"><img src="https://github.com/sp7uto/internet-radio-recorder/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI status"></a>
  <a href="https://github.com/sp7uto/internet-radio-recorder/releases/latest"><img src="https://img.shields.io/github/v/release/sp7uto/internet-radio-recorder?label=release" alt="Latest release"></a>
  <a href="https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder"><img src="https://img.shields.io/badge/container-GHCR-2496ED?logo=docker&logoColor=white" alt="Docker image on GHCR"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/sp7uto/internet-radio-recorder" alt="MIT license"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#features">Features</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#security">Security</a>
</p>

<p align="center">
  <a href="docs/screenshots/IRR01.png"><img src="docs/screenshots/IRR01.png" alt="Internet Radio Recorder — Today view and scheduled recordings" width="900"></a>
</p>

<p align="center"><sub>Today view — illustrative historical capture (version label updated to v2.2.1), not a live screenshot of the current release.</sub></p>

## Why Internet Radio Recorder?

Choose programmes, set a weekly schedule, and let IRR record them to your own storage. Manage everything in a browser — without maintaining individual cron jobs or deploying a full broadcast automation stack. Designed for Docker-based home servers and NAS installations.

**Current stable version: [v2.2.3](https://github.com/sp7uto/internet-radio-recorder/releases/tag/v2.2.3).** This maintenance release corrects the [volume usage label](RELEASE_NOTES_v2.2.3.md); the v2.2.2 atomic maintenance gate remains unchanged.

## Features

| Area | What you get |
| --- | --- |
| **Recording** | Multiple Internet radio stations; MP3/AAC selection via FFprobe; stream copy without transcoding (`ffmpeg -c:a copy`); one file per programme; manual **REC / STOP** |
| **Scheduling** | Weekly timetables, programme titles, `pre` / `post` margins, adjacent programmes and midnight-crossing schedules |
| **Web dashboard** | **Today**, **Calendar**, **History**, **Stream Status**, **Recording Library**, **Statistics**; station ordering by drag-and-drop or arrows |
| **Monitoring** | Stream availability tests, codec and bitrate diagnostics, detection of missing or empty output files |
| **Storage & configuration** | Per-station retention and storage limits; configuration backup, safe import/merge and full restore |
| **Integrations** | ICS calendar subscription; optional NTFY and webhook alerts, including recording-completion notifications |
| **Deployment** | Docker Compose, Synology/Portainer example and public GHCR images; optional guarded Docker auto-updates on the reference VPS |

<!-- SCREENSHOTS_START -->

## Screenshots

These six images are **historical example captures**, with their displayed title
updated to **v2.2.1**. They illustrate the interface and sample data, not a fresh
capture from the current production release. Click to see the full image.

| | |
| :---: | :---: |
| **Today — scheduled recordings** | **Calendar** |
| [<img src="docs/screenshots/IRR01.png" alt="Today — scheduled recordings" width="420">](docs/screenshots/IRR01.png) | [<img src="docs/screenshots/IRR03.png" alt="Calendar view" width="420">](docs/screenshots/IRR03.png) |
| **Stations** | **Stream status** |
| [<img src="docs/screenshots/IRR02.png" alt="Station management" width="420">](docs/screenshots/IRR02.png) | [<img src="docs/screenshots/IRR04.png" alt="Stream status and diagnostics" width="420">](docs/screenshots/IRR04.png) |
| **Recording library** | **Statistics** |
| [<img src="docs/screenshots/IRR05.png" alt="Recording library" width="420">](docs/screenshots/IRR05.png) | [<img src="docs/screenshots/IRR06.png" alt="Recording statistics" width="420">](docs/screenshots/IRR06.png) |

<!-- SCREENSHOTS_END -->

## Quick Start

**Requirements:** Docker and Docker Compose v2.

1. Clone the repository:

   ```bash
   git clone https://github.com/sp7uto/internet-radio-recorder.git
   cd internet-radio-recorder
   ```

2. Create local configuration files:

   ```bash
   cp .env.example .env
   cp config/stations.example.json config/stations.json
   ```

3. Edit `.env` and **change `CALENDAR_TOKEN`** before starting.
4. Build and start the container:

   ```bash
   docker compose up -d --build
   ```

5. Open `http://server-address:8080` on your trusted network.

| Path | Purpose |
| --- | --- |
| `./recordings` | Audio files |
| `./config` | Stations and application configuration |

> [!WARNING]
> **The administration panel has no built-in authentication.** Do not expose
> port `8080` directly to the public Internet. See [Security](#security)
> before enabling remote access.

For installation options, upgrades and permissions, see
[Installation and upgrades](docs/INSTALLATION.md).

## Synology / Portainer

An example stack is provided in [`docker-compose-portainer.yml`](docker-compose-portainer.yml).
Example Synology paths (adapt to your own NAS):

```text
/volume1/docker/internet-radio-recorder/config
/volume1/docker/radio
```

This is **an example, not a production configuration**. See the
[installation guide](docs/INSTALLATION.md) before deploying.

## Scheduling

Each station may have multiple entries for each day of the week:

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Programme Name",
  "pre": 2,
  "post": 3
}
```

`pre` and `post` are recording margins in minutes. Programmes crossing
midnight are supported. With **one file per programme**, the nominal start
of the next programme takes priority over overlapping recording margins.

See [Scheduling](docs/SCHEDULING.md).

## Backup and Import

| Action in the web UI | Effect |
| --- | --- |
| **Backup** | Download the current `stations.json` |
| **Import / Merge** | Keep existing stations and schedules; add non-conflicting entries |
| **Restore Backup** | Replace the complete configuration |

Before importing, IRR creates a timestamped backup:
`stations.before-import-YYYYMMDD-HHMMSS.json`.

See [Backup and import/merge](docs/BACKUP_AND_MERGE.md).

## ICS Calendar

Subscribe to the recording schedule using:

```text
http://server-address:8080/calendar.ics?token=YOUR_TOKEN
```

The access token is configured via `CALENDAR_TOKEN`.

## Notifications

Optional **NTFY** and **webhook** notifications can report recording events
and application status. Set `NOTIFY_ON_COMPLETE=true` to be notified
after each successful recording. Missing or empty output files generate
an error notification when a notification destination is configured.

## Security

**The administration panel does not provide built-in authentication.**
Anyone able to reach it may be able to change station settings, start or
stop recordings, or delete files from the library.

**Never expose port `8080` directly to the public Internet.** For remote
access, use **Tailscale**, another VPN, or a reverse proxy with HTTPS and
authentication. Read [SECURITY.md](SECURITY.md) before deploying.

## Documentation

| Getting started | Reference & operations |
| --- | --- |
| [Installation and upgrades](docs/INSTALLATION.md) | [API and endpoints](docs/API.md) |
| [Configuration](docs/CONFIGURATION.md) | [Troubleshooting](docs/TROUBLESHOOTING.md) |
| [Scheduling](docs/SCHEDULING.md) | [Automatic Docker updates (GHCR / VPS)](docs/AUTOMATIC_UPDATES.md) |
| [Backup and import/merge](docs/BACKUP_AND_MERGE.md) | [Atomic maintenance gate (v2.2.2)](docs/ATOMIC_MAINTENANCE.md) |
| [Security](SECURITY.md) | [GitHub publishing](docs/GITHUB_PUBLISHING.md) |
| [Changelog](CHANGELOG.md) | [Release notes v2.2.3](RELEASE_NOTES_v2.2.3.md) |

## Technical Details

The Docker image is based on `debian:bookworm-slim` and includes
**Python 3, FFmpeg and FFprobe**. The container runs as **UID 1000**;
mounted `/config` and `/recordings` directories must be writable by that user.

## Latest Release & Docker Delivery

**Stable: [v2.2.3](https://github.com/sp7uto/internet-radio-recorder/releases/tag/v2.2.3).**
This maintenance release changes only the volume usage label to
`Zajętość wolumenu`. The atomic maintenance gate from v2.2.2 and MP3/AAC
recording diagnostics from v2.2.1 remain unchanged.

Versioned and stable images are published to
[GHCR](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder),
including `ghcr.io/sp7uto/internet-radio-recorder:stable`.

<details>
<summary>Verified production deployment (reference irr-vps)</summary>

The optional updater on `irr-vps` completed its first guarded automatic Docker
update (v2.2.1) on **2026-10-26 at 01:30 CET**. On
**2026-10-26 at 03:01:21 CET**, its timer automatically deployed v2.2.2:
the service journal confirmed an exclusive maintenance lock, successful
container recreation and `flock-v1` in the running recorder. The prior
image was retained for rollback.

This automation is **specific to the reference VPS**; a normal
Docker Compose installation does not automatically install the timer.
See [Automatic updates](docs/AUTOMATIC_UPDATES.md) for its prerequisites,
safety limitations and rollback.

</details>

## Contributing & Feedback

Bug reports, feature requests and pull requests are welcome.
Please read [CONTRIBUTING.md](CONTRIBUTING.md) and open a
[GitHub Issue](https://github.com/sp7uto/internet-radio-recorder/issues).

## License

Internet Radio Recorder is released under the
[MIT License](LICENSE).
