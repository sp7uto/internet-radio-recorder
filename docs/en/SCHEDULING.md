# Scheduling and programme boundaries

[🇵🇱 Polski](../SCHEDULING.md) · **🇬🇧 English**

## Scheduled programme entry

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Programme name",
  "pre": 2,
  "post": 3
}
```

- `start`, `end`: nominal programme time.
- `title`: name used in the interface and output filename.
- `pre`: recording minutes before start.
- `post`: recording minutes after end.

## Adjacent programmes

For example:

```text
20:00–21:00  Programme A
21:00–23:00  Programme B
```

When the extended pre/post windows overlap, **nominal programme boundaries take priority** (since 2.1.10). Programme B becomes active at precisely 21:00.

With `one_file_per_program: true`, the recorder stops file A using the `program_change` reason and immediately begins file B, without the ordinary reconnection delay.

## Overnight programmes

When `end <= start`, the programme ends on the following day, e.g. `22:30–01:00`. Pre/post margins work across midnight as well.

## Segmented mode

When `one_file_per_program` is false, FFmpeg divides output into `segment_minutes` segments aligned to wall-clock time.

## Manual mode

`REC` switches the station to manual recording independently of its schedule; it continues until `STOP` is clicked or the station is removed/disabled.
