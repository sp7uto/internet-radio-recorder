# IRR safe recovery — release candidate RC1 (TEST ONLY)

Base: v2.2.1 code plus changes from PR #6.
Source commit: a1029b45f329ee363364ba392c9c84b836e2c058
Branch: preview/safe-recovery-rc1

## Verified
- GitHub Actions CI #55 succeeded on source commit.
- Python unit and regression tests passed.
- Docker image build passed.
- Isolated synthetic MP3 and real FFmpeg worker test passed.
- Filename collision handling after restart and midnight was tested.

## Behavior
- Opt-in only: PRESERVE_RECOVERY_PARTS=true.
- Default remains false.
- Only scheduled one_file_per_program recordings get separate _part02, _part03, etc.
- Existing files are skipped, and FFmpeg uses -n in opt-in mode.
- Does not restore missing audio, merge fragments or prevent multi-container
  races with an atomic lock.

## Release boundaries
- This is a source preview branch, NOT a stable GitHub Release or GHCR image.
- Do not merge to main, publish latest, or auto-update the VPS.
- Do not reuse production /config or /recordings for evaluation.
- QNAP and Synology are out of scope.
- Next gate: manual review of branch differences and isolated soak test before
  any production deployment decision.

## Reproduce CI checks

```bash
python3 -m compileall -q recorder.py api.py schedules.py tests
python3 -m unittest discover -s tests -v
docker build -t irr-safe-recovery:rc1 .
docker run --rm --network none \
  --env IRR_DOCKER_RECOVERY_TEST=1 \
  --env PYTHONPATH=/app \
  --mount type=bind,src="$PWD/tests",dst=/tests,readonly \
  --tmpfs /config:rw,uid=1000,gid=1000 \
  --tmpfs /recordings:rw,uid=1000,gid=1000 \
  --entrypoint python3 irr-safe-recovery:rc1 \
  /tests/test_recovery_container.py
```

All commands above use temporary container storage. The Docker image itself is
built locally; the procedure neither starts the production recorder nor uses
NAS recording mounts.

## Rollback
No rollback of production is needed because this preview has not been deployed.
