# Stations and Recording

## Adding stations

Use **Stations** in the web interface to configure each Internet radio station and its stream URL. Use **Test stream** to check availability and inspect codec/bitrate metadata before planning recordings.

Stations can be reordered with drag-and-drop or the arrow controls; save changes to keep their order.

## Automatic format detection

IRR probes a stream with **FFprobe immediately before recording** and selects an appropriate MP3 or AAC output container when supported. It copies the audio stream with FFmpeg without transcoding where the source allows it; old `codec` or `detected_ext` entries alone do not determine the file extension.

The recorder reports missing/empty output files as errors rather than mistaking an older file for a successful recording.

## Recording controls and views

| View/control | Purpose |
| --- | --- |
| **REC / STOP** | Manual recording control |
| **Today** | Upcoming recordings and current activity |
| **History** | Finished tasks, failures and diagnostic details |
| **Stream Status** | Station status and stream metadata |
| **Recording Library** | Browse stored files |
| **Statistics** | Summary of recordings and storage |

## Persistent state

Station configuration normally lives at `/config/stations.json`. Treat it as valuable data: make backups before bulk changes or imports and ensure the container user can write to `/config`.

See the [Configuration reference](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/CONFIGURATION.md), [API reference](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/API.md) and [Troubleshooting](https://github.com/sp7uto/internet-radio-recorder/wiki/Troubleshooting).
