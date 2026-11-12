"""Deterministic schedule-boundary and worker retry regression tests.

No network, Docker, radio station or user recording directory is used.
"""
import io
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import recorder


class ScheduleBoundaryTests(unittest.TestCase):
    def test_adjacent_programs_switch_at_exact_boundary(self):
        st = {"enabled": True, "schedule": {
            "mon": [
                {"start": "12:00", "end": "13:00", "title": "First"},
                {"start": "13:00", "end": "14:00", "title": "Second", "pre": 4},
            ]}}
        before = datetime(2026, 10, 26, 12, 59, 59, tzinfo=timezone.utc)
        boundary = before + timedelta(seconds=1)
        self.assertEqual(recorder.active(st, before)[2], "First")
        self.assertEqual(recorder.active(st, boundary)[2], "Second")
        self.assertNotEqual(recorder.active(st, before)[3]["_identity"],
                            recorder.active(st, boundary)[3]["_identity"])

    def test_crossing_midnight_ends_at_correct_boundary(self):
        st = {"enabled": True, "schedule": {"mon": [
            {"start": "23:55", "end": "00:05", "title": "Overnight"}
        ]}}
        during = datetime(2026, 10, 27, 0, 4, 59, tzinfo=timezone.utc)
        after = during + timedelta(seconds=1)
        self.assertTrue(recorder.active(st, during)[0])
        self.assertFalse(recorder.active(st, after)[0])

    def test_no_restart_after_schedule_end(self):
        st = {"enabled": True, "schedule": {"mon": [
            {"start": "12:00", "end": "13:00", "title": "First"}
        ]}}
        at_end = datetime(2026, 10, 26, 13, 0, tzinfo=timezone.utc)
        self.assertFalse(recorder.active(st, at_end)[0])


class _ExitedProcess:
    """A failed FFmpeg process: no child process ever remains running."""
    def __init__(self):
        self.returncode = 1
        self.stderr = io.StringIO("network disconnected\\n")

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


class WorkerRestartTests(unittest.TestCase):
    def test_retries_increment_suffix_without_touching_real_files(self):
        station = {"name": "Synthetic", "url": "http://example.invalid/audio",
                   "codec": "mp3", "enabled": True,
                   "one_file_per_program": True}
        slot = {"_identity": "mon:0:2026-10-26T12:00:00+00:00",
                "start": "12:00", "end": "13:00", "title": "Synthetic"}
        commands = []
        old_running = recorder.running
        old_procs, old_state = recorder.procs, recorder.state
        old_workers = recorder.workers
        with tempfile.TemporaryDirectory(prefix="irr-worker-test-") as directory:
            def spawn(command, **kwargs):
                commands.append(command)
                if len(commands) == 3:
                    recorder.running = False
                return _ExitedProcess()

            try:
                recorder.running = True
                recorder.procs, recorder.state, recorder.workers = {}, {}, {}
                with patch.object(recorder, "OUT", Path(directory)), \
                     patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True), \
                     patch.object(recorder, "load", return_value=[station]), \
                     patch.object(recorder, "active", return_value=(True, "12:00-13:00", "Synthetic", slot)), \
                     patch.object(recorder, "next_schedule", return_value=None), \
                     patch.object(recorder, "ffprobe_info", return_value={"ok": True, "ext": "mp3", "codec": "mp3"}), \
                     patch.object(recorder, "recording_result", return_value={"file": None, "size": 0, "empty": True}), \
                     patch.object(recorder, "notify"), \
                     patch.object(recorder, "add_exec"), \
                     patch.object(recorder.threading, "Thread") as thread, \
                     patch.object(recorder.subprocess, "Popen", side_effect=spawn), \
                     patch.object(recorder.time, "sleep"):
                    thread.return_value.start.return_value = None
                    recorder.worker("Synthetic")
                self.assertEqual(len(commands), 3)
                paths = [cmd[-1] for cmd in commands]
                self.assertEqual(len(set(paths)), 3)
                self.assertTrue(paths[1].endswith("_part02.mp3"))
                self.assertTrue(paths[2].endswith("_part03.mp3"))
            finally:
                recorder.running = old_running
                recorder.procs, recorder.state, recorder.workers = old_procs, old_state, old_workers


if __name__ == "__main__":
    unittest.main()
