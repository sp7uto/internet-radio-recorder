# Internet Radio Recorder v2.2.3 — volume label correction

[🇵🇱 Polski](RELEASE_NOTES_v2.2.3.md) · **🇬🇧 English**

## Changed

- The disk usage label no longer implies that only Synology storage is supported: **"Zajętość wolumenu Synology" → "Zajętość wolumenu"** ("Synology volume usage" → "Volume usage").
- The label was updated in both UI implementations (`templates/index.html` and `web.py`) in [PR #17](https://github.com/sp7uto/internet-radio-recorder/pull/17).

## Compatibility

This is a cosmetic maintenance release. There are no changes to streams, MP3/AAC recording, FFmpeg, schedules, API, the `stations.json` format, ports or `/config` and `/recordings` mounts.

The `flock-v1` atomic maintenance lock introduced in v2.2.2 remains unchanged.

## Upgrading

Public Docker images are published to GHCR with `v2.2.3` and `stable` tags. On the reference VPS, the guarded updater can deploy a new image after detecting a release and checking the safe update window. **Publishing an image does not prove that a VPS has deployed it.**

- [Safe update policy](docs/en/AUTOMATIC_UPDATES.md)
- [Release v2.2.2](RELEASE_NOTES_v2.2.2.md)
