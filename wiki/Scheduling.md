# Scheduling

IRR supports multiple weekly programme entries per station, recording margins, and programmes that cross midnight.

## Example entry

```json
{
  "start": "20:00",
  "end": "21:00",
  "title": "Programme Name",
  "pre": 2,
  "post": 3
}
```

- `start` and `end` — planned programme times.
- `title` — programme label.
- `pre` — minutes of recording before the programme.
- `post` — minutes after it.

Add entries using the IRR station editor and inspect the resulting week in **Calendar**.

## Adjacent and overnight programmes

The schedule engine handles shows passing midnight. In **one file per programme** mode, the nominal start of the next show takes priority over overlapping margins, so neighbouring recordings can be separated.

## Practical checks

- Make sure the correct day and time are selected.
- Review the upcoming recording in **Today**.
- Check **History** for the result, including diagnostic information if FFmpeg fails.
- Allow for the source stream becoming temporarily unavailable.

For authoritative edge-case behaviour, see [docs/SCHEDULING.md](https://github.com/sp7uto/internet-radio-recorder/blob/main/docs/SCHEDULING.md).
