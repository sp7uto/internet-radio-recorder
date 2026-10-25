# Optional preservation of recovered recording fragments

The recorder already retries stream connections through FFmpeg and restarts
FFmpeg when a process exits unexpectedly. This change **does not** change its
reconnection, scheduling, codec selection, or stream settings.

## Why

In `one_file_per_program` mode the output filename uses minute precision.
A restart in that same minute could select the same filename and overwrite
already captured audio.

## Opt-in setting

Set `PRESERVE_RECOVERY_PARTS=true` in the recorder container environment.
The default is `false`: existing deployments behave exactly as before.

When enabled, the original file keeps its old name. If the FFmpeg process exits
unexpectedly while the same scheduled programme is still active, its first
retry writes a separate file ending in `_part02`, the next in `_part03`,
and so on. The counter resets for the next programme, but occupied filenames
are skipped (including after a container restart). FFmpeg also uses `-n` in
this optional mode, so it refuses an overwrite in case of a filename race.
The original fragment is never deliberately rewritten by a retry.

This setting applies only to scheduled `one_file_per_program` recordings.
Segmented output and manual recordings are unchanged. Fragments are not
automatically merged, and audio missed during an outage cannot be recovered.
Existing execution history still records the final file of each FFmpeg
process; a later enhancement can group fragments in the UI.

## Verification

From the repository root:

```bash
python3 -m unittest discover -s tests -p 'test_recovery_parts.py' -v
python3 -m py_compile recorder.py
```

Do not deploy automatically. Review the change and test with a disposable
stream and a separate recordings directory before considering VPS rollout.

## Additional regression coverage

Tests now cover a retry crossing midnight, preservation of existing filenames
across restarts, and a competition between two independent FFmpeg processes
for a shared output path. The `-n` option is a last-resort overwrite guard,
**not an atomic cross-container lock**. Avoid running multiple IRR instances
that write to the same directory until a separate multi-writer locking design
has been implemented and independently tested.
