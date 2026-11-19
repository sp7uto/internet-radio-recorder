# Configuration

[🇵🇱 Polski](../CONFIGURATION.md) · **🇬🇧 English**

The main station configuration is `/config/stations.json`:

```json
{
  "stations": [{
    "name": "Example Radio",
    "url": "https://example.invalid/live.mp3",
    "codec": "mp3",
    "detected_ext": "mp3",
    "segment_minutes": 60,
    "retention_days": 90,
    "max_storage_gb": 20,
    "one_file_per_program": true,
    "enabled": true,
    "schedule": {
      "mon": [], "tue": [], "wed": [], "thu": [],
      "fri": [], "sat": [], "sun": []
    }
  }]
}
```

Prefer managing the configuration through the web interface.

## Station fields

- `name`: unique name.
- `url`: direct audio stream URL.
- `codec`, `detected_ext`: cached format metadata; may be detected during stream tests.
- `segment_minutes`: segment duration when one-file-per-programme is disabled.
- `retention_days`: age-based removal; `0` disables age retention.
- `max_storage_gb`: per-station limit; `0` means no limit.
- `one_file_per_program`: one output file per programme.
- `enabled`: whether the station is active.
- `schedule`: weekly programme entries.

## Saving

Writes are atomic; before replacing `stations.json` the old version is copied to `stations.json.bak`. The saved file is read back for validation.

## Station order

The order in the `stations` array determines card order. Use the drag handle or arrow controls and save your changes.

## Codec detection (since 2.2.1)

Immediately before recording, FFprobe inspects the source and IRR selects the correct MP3/AAC extension where supported, rather than trusting stale `codec` and `detected_ext` fields. FFmpeg copies compatible source audio without re-encoding. Consult History for process errors or missing outputs.
