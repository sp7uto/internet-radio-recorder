# Backup, merge import and restore

[🇵🇱 Polski](../BACKUP_AND_MERGE.md) · **🇬🇧 English**

## Backup

The **Backup** button downloads a JSON document of this shape:

```json
{"stations": []}
```

The downloaded file contains the actual station list in place of the empty example array.

## Import / Merge

This is the safer default mode:

1. Existing stations are preserved.
2. An entirely new station is appended to the list.
3. If a station name already exists (case-insensitive), its current settings remain unchanged.
4. New non-conflicting programme entries for an existing station can be added.
5. Exact duplicates with the same `start + end + title` are skipped.
6. An entry overlapping the nominal time of an existing programme on the same day is skipped.

After importing, the interface reports the counts of added stations, added tasks, skipped duplicates and conflicts.

## Restore Backup

**This replaces the entire configuration** with the imported file. Use with care.

## Automatic backup before import

Before either import operation, IRR saves the current settings to:

```text
/config/stations.before-import-YYYYMMDD-HHMMSS.json
```

Ordinary configuration saves also create `stations.json.bak`.
