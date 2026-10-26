#!/usr/bin/env python3
"""Unit tests for the pure guard logic (no Docker or network)."""
import importlib.util
import json
from types import SimpleNamespace
from unittest.mock import patch
import pathlib
import unittest
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("irr_guard", ROOT/"deploy"/"irr-update-guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
NOW = datetime(2026, 10, 25, 20, 30, tzinfo=timezone.utc)

def sample(status="waiting", scheduled=False, next_at=None, schedule=None):
    return {"stations": [{"name":"Radio Test","enabled":True,"schedule": schedule if schedule is not None else {}}],
            "status": {"Radio Test": {"status":status,"scheduled":scheduled,
                                      "manual":False,"next":{"when":next_at} if next_at else None}}}

class GuardTests(unittest.TestCase):
    def test_idle(self):
        self.assertTrue(guard.check(sample(),NOW)[0])
    def test_recording(self):
        self.assertFalse(guard.check(sample("recording",True),NOW)[0])
    def test_connecting(self):
        self.assertFalse(guard.check(sample("connecting"),NOW)[0])
    def test_scheduled(self):
        self.assertFalse(guard.check(sample("waiting",True),NOW)[0])
    def test_manual(self):
        d=sample();d["status"]["Radio Test"]["manual"]=True
        self.assertFalse(guard.check(d,NOW)[0])
    def test_missing_status(self):
        d=sample();d["status"]={}
        self.assertFalse(guard.check(d,NOW)[0])
    def test_empty_stations(self):
        d=sample();d["stations"]=[]
        self.assertFalse(guard.check(d,NOW)[0])
    def test_next_soon(self):
        self.assertFalse(guard.check(sample(next_at=(NOW+timedelta(minutes=5)).isoformat()),NOW)[0])
    def test_next_later(self):
        self.assertTrue(guard.check(sample(next_at=(NOW+timedelta(hours=2)).isoformat()),NOW)[0])
    def test_malformed_next(self):
        self.assertFalse(guard.check(sample(next_at="bogus"),NOW)[0])
    def test_nonempty_schedule_missing_next(self):
        self.assertFalse(guard.check(sample(schedule={"sun":[{"start":"22:00"}]}), NOW)[0])
    def test_unsorted_api_next_but_soon_in_schedule(self):
        # UTC 20:30 = Warsaw 21:30; Sunday slot at 21:35 local.
        schedule={"sun":[{"start":"21:35","pre":0},{"start":"23:50","pre":0}]}
        self.assertFalse(guard.check(sample(next_at=(NOW+timedelta(hours=3)).isoformat(),schedule=schedule),NOW)[0])


class DockerProcessChecks(unittest.TestCase):
    def _run_guard(self, process_output):
        data = sample()
        def fake_run(argv, **_kwargs):
            if argv[1] == "inspect":
                return SimpleNamespace(returncode=0, stdout="true\\n", stderr="")
            if argv[-1] == guard.FFMPEG_SCAN:
                return SimpleNamespace(returncode=0, stdout=process_output, stderr="")
            if argv[-1] == guard.FETCH_JSON:
                return SimpleNamespace(returncode=0, stdout=json.dumps(data), stderr="")
            raise AssertionError("Unexpected command: " + repr(argv))
        with patch.object(guard.subprocess, "run", side_effect=fake_run):
            return guard.main()

    def test_scan_python_valid(self):
        compile(guard.FFMPEG_SCAN, "<FFMPEG_SCAN>", "exec")

    def test_idle_allows(self):
        self.assertEqual(self._run_guard("FFMPEG_IDLE\\n"), 0)

    def test_active_deferred(self):
        self.assertEqual(self._run_guard("FFMPEG_ACTIVE\\n"), 1)

    def test_unexpected_scan_output_deferred(self):
        self.assertEqual(self._run_guard(""), 1)

if __name__ == "__main__":
    unittest.main()
