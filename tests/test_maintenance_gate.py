"""Verify the real Linux flock shared/exclusive coordination across processes."""
import fcntl
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
