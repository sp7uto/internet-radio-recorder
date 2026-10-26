# Troubleshooting

Start with **History** and **Stream Status** in the web UI. Do not delete configuration or recreate containers until you know which component failed.

| Symptom | First check |
| --- | --- |
| Stations cannot be saved | Is `/config` writable for container UID 1000? |
| Radio stream is offline | Is the actual stream URL reachable and supported? Run **Test stream**. |
| Expected recording is missing | Check station enablement, schedule, **History** and `/recordings` write permissions. |
| MP3 recordings appear as empty AAC files | Confirm you run v2.2.1 or later; inspect FFprobe and FFmpeg details in **History**. |
| Recording stops/starts at an unexpected time | Review margins, programmes crossing midnight and adjacent entries. |
| ICS subscription cannot be fetched externally | Remote calendar services cannot reach a local-only URL. |
| Container shows an old UI after an update | Check the running image and whether your browser displays cached content. |
| Guarded updater delays deployment | Check if recording is active or scheduled soon; deferral can be correct. |

For the complete known-issue list and appropriate read-only commands, see [docs/TROUBLESHOOTING.md](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/TROUBLESHOOTING.md).

When reporting a bug in [GitHub Issues](https://github.com/sp7uto/internet-radio-recorder/issues), include the release number, a brief reproduction sequence, relevant error messages **without tokens or private URLs**, and your deployment method.
