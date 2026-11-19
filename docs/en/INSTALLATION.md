# Installation and upgrades

[🇵🇱 Polski](../INSTALLATION.md) · **🇬🇧 English**

This guide covers Docker Compose v2 and an installation on a trusted network.

## Standard installation

```bash
git clone https://github.com/sp7uto/internet-radio-recorder.git
cd internet-radio-recorder
cp .env.example .env
cp config/stations.example.json config/stations.json
```

Edit `.env`: set a long random `CALENDAR_TOKEN`, review station URLs, directories and the other settings. Then start:

```bash
docker compose up -d --build
```

The web panel normally uses port 8080. **Never expose that port directly to the public Internet**, because IRR has no built-in authentication.

## Persistent data and permissions

- `/config`: station settings, history and application state; preserve `stations.json`.
- `/recordings`: recorded audio and its directory tree.

The container uses UID `1000`; ensure write access to both mounts. Avoid unrestricted `chmod 777`.

## Updating a local build

1. Back up Compose files, `.env` and `config/`.
2. Review active and upcoming recordings; do not restart the container during a programme.
3. Select the intended version/tag; never overwrite `stations.json` with a sample.
4. In a safe window run `docker compose up -d --build`.
5. Verify `/api/data`, recording history and fresh output files.

## Synology and Portainer

`docker-compose-portainer.yml` is a **template**, not an actual production configuration. Example paths include `/volume1/docker/internet-radio-recorder/config` and `/volume1/docker/radio`. Replace them as needed, and verify local image tags before use. Do not accidentally deploy two recorders using the same schedules.

## Optional GHCR automatic updates

The reference `irr-vps` installation uses public `ghcr.io/sp7uto/internet-radio-recorder:stable`, a systemd timer, checks for FFmpeg activity and upcoming programmes, and rollback support. The guarded update of v2.2.1 was verified on 26 October 2026, as was the v2.2.2 atomic-lock deployment at 03:01:21 CET that day.

**The timer is not included in standard Docker Compose.** The `deploy/install-vps.sh` procedure is specific to the reference VPS; never run it unchanged on another server or NAS.

## Key environment variables

| Variable | Meaning |
| --- | --- |
| `TZ` | Time zone (e.g. `Europe/Warsaw`) |
| `CONFIG_FILE` | Station file, normally `/config/stations.json` |
| `RECORDINGS_DIR` | Recording directory, normally `/recordings` |
| `WEB_PORT` | HTTP port (8080) |
| `RETRY_DELAY` | Stream reconnection delay |
| `RETENTION_CHECK_MINUTES` | Retention check interval |
| `HEALTHCHECK_SECONDS` | Stream check interval |
| `CALENDAR_TOKEN` | Private ICS token |
| `NTFY_URL`, `WEBHOOK_URL` | Optional notification destinations |
| `NOTIFY_ON_COMPLETE` | Notify after completed recordings |

[Automatic updates](AUTOMATIC_UPDATES.md) · [Atomic maintenance lock](ATOMIC_MAINTENANCE.md) · [Security](../../SECURITY.en.md)
