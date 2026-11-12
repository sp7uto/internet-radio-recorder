"""Safety regressions for midnight filenames and concurrent FFmpeg writers.

All files live in TemporaryDirectory and no external network is used.
"""
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime as RealDateTime
from pathlib import Path
from unittest.mock import patch

import recorder


class FrozenDatetime:
    instant = RealDateTime(2026, 10, 26, 23, 59, 58)

    @classmethod
    def now(cls):
        return cls.instant


class BoundaryAndConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.station = {
            "name": "Synthetic Radio",
            "url": "synthetic-input",
            "codec": "mp3",
            "one_file_per_program": True,
        }
        self.slot = {"_identity": "mon:23:55-00:05", "title": "Night"}

    def test_midnight_retry_uses_new_date_and_never_reuses_filename(self):
        with tempfile.TemporaryDirectory(prefix="irr-midnight-") as tmp:
            with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True), \
                 patch.object(recorder, "datetime", FrozenDatetime):
                first = Path(recorder.build_cmd(
                    self.station, Path(tmp), "Night", self.slot, 0)[-1])
                first.parent.mkdir(parents=True)
                first.write_bytes(b"untouched-before-midnight")
                FrozenDatetime.instant = RealDateTime(2026, 10, 27, 0, 0, 2)
                next_file = Path(recorder.build_cmd(
                    self.station, Path(tmp), "Night", self.slot, 1)[-1])
            self.assertNotEqual(first, next_file)
            self.assertEqual(first.parent.name, "2026-10-26")
            self.assertEqual(next_file.parent.name, "2026-10-27")
            self.assertIn("_part02.mp3", next_file.name)
            self.assertEqual(first.read_bytes(), b"untouched-before-midnight")

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "ffmpeg and ffprobe required")
    def test_competing_writers_cannot_overwrite_same_output(self):
        with tempfile.TemporaryDirectory(prefix="irr-concurrent-") as tmp:
            root = Path(tmp)
            input_path = root / "input.mp3"
            subprocess.run([
                "ffmpeg", "-v", "error", "-nostdin", "-f", "lavfi",
                "-i", "sine=frequency=440:duration=3",
                "-c:a", "libmp3lame", "-b:a", "96k", str(input_path)
            ], check=True, timeout=30)
            self.station["url"] = str(input_path)
            with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True):
                command = recorder.build_cmd(
                    self.station, root / "output", "Night", self.slot, 0)
            destination = Path(command[-1])
            destination.parent.mkdir(parents=True)
            self.assertIn("-n", command)
            writers = [
                subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE)
                for _ in range(2)
            ]
            try:
                results = [p.communicate(timeout=20) for p in writers]
                codes = [p.returncode for p in writers]
            finally:
                for p in writers:
                    if p.poll() is None:
                        p.kill()
                        p.wait(timeout=5)
            self.assertEqual(codes.count(0), 1, str(results))
            self.assertTrue(destination.is_file())
            self.assertGreater(destination.stat().st_size, 1000)
            subprocess.run([
                "ffprobe", "-v", "error", "-show_entries",
                "stream=codec_name", "-of", "default=nw=1",
                str(destination)
            ], check=True, timeout=15, capture_output=True)


if __name__ == "__main__":
    unittest.main()
