# Automatic updates — GitHub → GHCR → VPS

[🇵🇱 Polski](../AUTOMATIC_UPDATES.md) · **🇬🇧 English**

## Scope and verified deployment

A guarded Docker updater has been deployed to the project's reference host `irr-vps`. The deployment is **not** part of ordinary Docker Compose installations and is not automatically enabled on QNAP or Synology.

Verified on 26 October 2026: the updater deployed v2.2.1 at 01:30 CET; the automatic v2.2.2 update with the atomic maintenance lock completed at 03:01:21 CET. These are historical verification records, **not assertions about the image currently running**.

| Component | Reference deployment |
| --- | --- |
| Application directory | `/srv/irr/app` |
| Container | `Internet-Radio-Recorder` |
| Image | `ghcr.io/sp7uto/internet-radio-recorder:stable` |
| Scheduled updater | `irr-docker-update.timer` |
| Frequency | Two runs per hour with up to 60 seconds of randomized delay |
| Image registry | [GitHub Container Registry](https://github.com/sp7uto/internet-radio-recorder/pkgs/container/internet-radio-recorder) |

## Update sequence

1. The host timer starts a guarded update attempt.
2. The updater obtains/checks the published GHCR image.
3. It verifies relevant schedules and active FFmpeg processes and postpones an unsafe update.
4. The compatible updater coordinates with recording workers through the shared `flock` maintenance file.
5. In a safe window, it recreates the container and verifies the outcome.
6. It retains the previous image for rollback if the update fails.

The maintenance lock prevents the race between permission to launch a recorder and permission to replace the container. It does **not** guarantee capture of a programme starting during a restart.

## Deployment precautions

- The installer `deploy/install-vps.sh` is specific to the reference host and must not be executed unchanged elsewhere.
- Keep the persistent `/config` mount and its maintenance-lock inode consistent between container and host.
- Back up application configuration and verify container volume paths before introducing the updater.
- Do not replace an installed updater with a different script solely because a new version exists.
- A new GitHub Release or GHCR image does not itself install or activate a timer.

For the original detailed deployment notes, commands and historical logs, consult the [Polish operations reference](../AUTOMATIC_UPDATES.md). Related: [Atomic maintenance lock](ATOMIC_MAINTENANCE.md).
