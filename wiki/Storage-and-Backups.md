# Storage and Backups

## Storage layout

The container expects two persistent mounts:

| Container path | Contains |
| --- | --- |
| `/config` | Station configuration, application state, history and backups |
| `/recordings` | Recorded audio |

The default local Compose example mounts `./config` and `./recordings`. Do **not** replace these volumes with sample files during upgrades. The container runs as UID 1000; check write permissions on both.

## Storage controls

IRR supports per-station retention and storage limits. Use the **Recording Library** and **Statistics** to inspect the saved material.

## Backup, import, restore

| UI operation | Result |
| --- | --- |
| **Backup** | Download the current `stations.json` |
| **Import / Merge** | Merge new non-conflicting station and schedule entries with existing configuration |
| **Restore Backup** | Replace the complete configuration |

Before import, IRR creates a timestamped copy such as `stations.before-import-YYYYMMDD-HHMMSS.json`.

For a NAS migration or upgrade, also back up any local `.env` and Compose configuration. Keep your recording library separately backed up where appropriate.

More details: [Backup and import/merge](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/BACKUP_AND_MERGE.md) and [Installation](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/INSTALLATION.md).
