# Atomic maintenance lock — design and deployment

[🇵🇱 Polski](../ATOMIC_MAINTENANCE.md) · **🇬🇧 English**

**Historical status (26 October 2026):** v2.2.2 was deployed to the reference `irr-vps` through the automatic updater at 03:01:21 CET. Logs confirmed an exclusive updater lock and the recorder reported `flock-v1`.

## Shared lock file

Both the recorder and the updater open **the same persistent file**:

- In the container: `/config/.irr-maintenance.lock`.
- On the reference host: `/srv/irr/app/config/.irr-maintenance.lock`.

They point to the same inode through the `/config` bind mount. Do not delete or recreate the lock file during normal operation.

## Recording workers

Each recording worker acquires a non-blocking **shared lock** (`LOCK_SH | LOCK_NB`) *before* FFprobe starts, and retains it through FFprobe, FFmpeg and process completion. Multiple concurrent recordings can hold shared locks.

## Host updater

After image retrieval and preliminary checks, the updater requests an exclusive non-blocking lock (`LOCK_EX | LOCK_NB`). If a worker owns the shared lock, the update is deferred. When the exclusive lock is held, a new worker cannot begin FFprobe or FFmpeg; it waits and retries. After successful deployment or rollback, the lock is released.

## Guarantees and limitations

This mechanism prevents a race between **starting a recording process** and **replacing the container**. It cannot guarantee uninterrupted audio if a broadcast starts during the brief period of maintenance or restart, and it is not a substitute for backups and post-update validation.

## Prerequisites for another installation

A compatible version of both the recorder and host updater; a shared persistent lock inode; correct permissions and bind mounts; scheduling and FFmpeg safety checks; rollback and recovery paths.

**This is not a standard Docker Compose feature that installs itself.** The reference host's installation scripts require adaptation before use on a different server.

For low-level diagnostics, test procedures and rollout evidence, see the [original detailed Polish reference](../ATOMIC_MAINTENANCE.md).
