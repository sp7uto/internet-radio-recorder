"""Verify the real Linux flock shared/exclusive coordination across processes."""
import fcntl
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import recorder

from maintenance_gate import acquire_shared, release_shared


class MaintenanceGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / ".irr-maintenance.lock"

    def tearDown(self):
        self.directory.cleanup()

    def exclusive(self):
        fd = os.open(self.path, os.O_RDONLY | os.O_CREAT, 0o644)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd

    def test_gate_file_is_created_and_persistent(self):
        shared = acquire_shared(self.path)
        self.assertIsNotNone(shared)
        self.assertTrue(self.path.is_file())
        release_shared(shared)
        self.assertTrue(self.path.is_file(), "Lock path must never be removed on release")

    def test_maintenance_exclusive_blocks_ffmpeg_start(self):
        exclusive = self.exclusive()
        try:
            self.assertIsNone(acquire_shared(self.path))
        finally:
            os.close(exclusive)
        shared = acquire_shared(self.path)
        self.assertIsNotNone(shared)
        release_shared(shared)

    def test_recording_shared_blocks_maintenance(self):
        shared = acquire_shared(self.path)
        self.assertIsNotNone(shared)
        other = os.open(self.path, os.O_RDONLY)
        try:
            with self.assertRaises(BlockingIOError):
                fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(other)
            release_shared(shared)
        exclusive = self.exclusive()
        os.close(exclusive)

    def test_multiple_simultaneous_recording_workers(self):
        first = acquire_shared(self.path)
        second = acquire_shared(self.path)
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        other = os.open(self.path, os.O_RDONLY)
        try:
            with self.assertRaises(BlockingIOError):
                fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            release_shared(first)
            with self.assertRaises(BlockingIOError):
                fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            release_shared(second)
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(other)

    def test_separate_process_cannot_take_exclusive_during_recording(self):
        shared = acquire_shared(self.path)
        self.assertIsNotNone(shared)
        script = """import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.exit(23)
sys.exit(0)
"""
        try:
            p = subprocess.run([sys.executable, "-c", script, str(self.path)], check=False)
            self.assertEqual(p.returncode, 23)
        finally:
            release_shared(shared)
        p = subprocess.run([sys.executable, "-c", script, str(self.path)], check=False)
        self.assertEqual(p.returncode, 0)

    def test_permission_problem_does_not_allow_recording(self):
        missing_directory = Path(self.directory.name) / "missing" / "gate"
        with self.assertRaises(FileNotFoundError):
            acquire_shared(missing_directory)




class RecordingWorkerGateTests(unittest.TestCase):
    def setUp(self):
        self.original_running = recorder.running
        self.original_out = recorder.OUT
        self.original_state = recorder.state
        self.original_procs = recorder.procs
        self.tmp = tempfile.TemporaryDirectory()
        recorder.OUT = Path(self.tmp.name)
        recorder.state = {}
        recorder.procs = {}
        recorder.running = True
        self.station = {
            "name": "Radio Test",
            "url": "https://invalid.example/stream",
            "enabled": True,
            "schedule": {},
        }

    def tearDown(self):
        recorder.running = self.original_running
        recorder.OUT = self.original_out
        recorder.state = self.original_state
        recorder.procs = self.original_procs
        self.tmp.cleanup()

    def halt_after_sleep(self, _seconds):
        recorder.running = False

    def test_exclusive_maintenance_prevents_ffprobe_and_ffmpeg(self):
        with patch.object(recorder, "load", return_value=[self.station]), \
             patch.object(recorder, "active", return_value=(True, "slot", "Test", None)), \
             patch.object(recorder, "next_schedule", return_value=None), \
             patch.object(recorder, "acquire_shared", return_value=None), \
             patch.object(recorder, "ffprobe_info") as probe, \
             patch.object(recorder.subprocess, "Popen") as popen, \
             patch.object(recorder.time, "sleep", side_effect=self.halt_after_sleep):
            recorder.worker(self.station["name"])
        probe.assert_not_called()
        popen.assert_not_called()
        self.assertEqual(recorder.state["Radio Test"]["status"], "maintenance")

    def test_successful_recording_releases_gate(self):
        child = SimpleNamespace(
            poll=lambda: 0,
            wait=lambda timeout=None: 0,
            returncode=0,
            stderr=[],
        )
        with patch.object(recorder, "load", return_value=[self.station]), \
             patch.object(recorder, "active", return_value=(True, "slot", "Test", None)), \
             patch.object(recorder, "next_schedule", return_value=None), \
             patch.object(recorder, "acquire_shared", return_value=123) as acquire, \
             patch.object(recorder, "release_shared") as release, \
             patch.object(recorder, "ffprobe_info", return_value={"ok":False}), \
             patch.object(recorder.subprocess, "Popen", return_value=child), \
             patch.object(recorder, "recording_result", return_value={"file":"test.mp3","size":100,"empty":False}), \
             patch.object(recorder, "add_exec"), \
             patch.object(recorder.time, "sleep", side_effect=self.halt_after_sleep):
            recorder.worker(self.station["name"])
        acquire.assert_called_once()
        release.assert_called_once_with(123)

if __name__ == "__main__":
    unittest.main()
