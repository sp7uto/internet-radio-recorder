# Updates and Recovery

## Standard Docker Compose installation

1. Back up `.env`, Compose settings and `/config`.
2. Check **Today/Calendar/History** to avoid interrupting a recording.
3. Update the release or code in a safe window.
4. Recreate or rebuild the service using the deployment method you originally chose.
5. Verify the web interface, station configuration, upcoming schedule and new recordings.

**Do not overwrite** `stations.json` with the example configuration.

The detailed procedure depends on whether the installation builds the image locally or uses a versioned GHCR image. See [Installation](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md).

## Optional guarded Docker updater

The repository includes a specialized systemd updater for a reference Linux VPS. It checks the schedule and FFmpeg activity, only recreates IRR in a safe window, and retains a local rollback image. Since v2.2.2, the recorder and host updater coordinate through `flock` on a common config bind-mount file.

> [!IMPORTANT]
> The reference updater is **not** enabled by installing the application with standard Docker Compose. It is intentionally tied to a particular VPS layout. Do not run `deploy/install-vps.sh` unchanged on a different NAS or server.

The atomic gate prevents a race between a new FFmpeg start and an updater lock, but does **not** guarantee lossless capture for a programme beginning during a container restart.

For diagnostics, holds, rollback and the documented production example, consult:
- [Automatic Updates](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/AUTOMATIC_UPDATES.md)
- [Atomic Maintenance](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/ATOMIC_MAINTENANCE.md)
- [Release notes](https://github.com/sp7uto/internet-radio-recorder/releases/latest)
