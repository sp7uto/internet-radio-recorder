# Internet Radio Recorder v2.2.1 — MP3 recording fix

## Changes

- The recorder probes the stream immediately before recording and selects the
  matching MP3 or AAC output container without transcoding.
- Imported stations and stations saved without using **Test stream** no longer
  depend on a stale default AAC value.
- Empty or missing output files are recorded as errors instead of being hidden
  by an older file from the same station.
- Execution history now includes the `ffmpeg` command, return code and selected
  output format.
- Optional completion notifications can be enabled with
  `NOTIFY_ON_COMPLETE=true` for NTFY or webhook integrations.

The `stations.json` format, ports and volume paths remain unchanged.
