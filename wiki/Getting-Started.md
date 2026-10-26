# Getting Started

**Goal:** a self-hosted IRR installation on a trusted network with persistent configuration and recordings.

## Requirements

- Docker and Docker Compose v2.
- Writable directories for configuration and audio files.
- A working Internet radio stream URL.

## Local Docker Compose installation

On your Docker host:

```bash
git clone https://github.com/sp7uto/internet-radio-recorder.git
cd internet-radio-recorder
cp .env.example .env
cp config/stations.example.json config/stations.json
```

Edit `.env`: **replace `CALENDAR_TOKEN` with a long, random value** before starting, and review the other settings. Then run:

```bash
docker compose up -d --build
```

On your trusted network, open `http://server-address:8080`.

**Persistent directories:** `./config` holds stations and application state; `./recordings` holds recorded audio. The image runs as **UID 1000**; both mounted directories must be writable by that user.

## What to do next

1. Open **Stations** to add a name and radio stream URL.
2. Use the stream test to check the connection and audio metadata.
3. Add a schedule entry and review it in **Calendar** or **Today**.
4. Check **History**, **Stream Status** and the **Recording Library** after the first recording.

**Security:** the panel does not require a password. Never expose port 8080 directly to the public Internet.

See [Stations and Recording](https://github.com/sp7uto/internet-radio-recorder/wiki/Stations-and-Recording), [Scheduling](https://github.com/sp7uto/internet-radio-recorder/wiki/Scheduling) and [Security](https://github.com/sp7uto/internet-radio-recorder/wiki/Security).

Authoritative installation and upgrade guidance: [docs/INSTALLATION.md](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md).
