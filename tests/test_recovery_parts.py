"""Regression tests for opt-in preservation of recording fragments."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import recorder


class RecoveryPartsTests(unittest.TestCase):
    def setUp(self):
        self.station = {
            "name": "Test Radio",
            "url": "https://example.invalid/stream.mp3",
            "codec": "mp3",
            "one_file_per_program": True,
        }
        self.slot = {"start": "12:00", "end": "13:00", "title": "Test"}

    def output_path(self, directory, part):
        return recorder.build_cmd(self.station, Path(directory), "Test", self.slot,
                                  recovery_part=part)[-1]

    def test_disabled_keeps_original_filenames(self):
        with TemporaryDirectory() as directory:
            with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", False):
                original = self.output_path(directory, 0)
                retry = self.output_path(directory, 1)
                self.assertEqual(original, retry)
                self.assertTrue(original.endswith(".mp3"))

    def test_enabled_creates_distinct_recovery_fragments(self):
        with TemporaryDirectory() as directory:
            with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True):
                first = self.output_path(directory, 0)
                second = self.output_path(directory, 1)
                third = self.output_path(directory, 2)
                self.assertNotEqual(first, second)
                self.assertNotEqual(second, third)
                self.assertIn("_part02.mp3", second)
                self.assertIn("_part03.mp3", third)

    def test_segmented_mode_is_unchanged(self):
        with TemporaryDirectory() as directory:
            st = dict(self.station, one_file_per_program=False)
            with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True):
                original = recorder.build_cmd(st, Path(directory), "Test", self.slot, 0)
                retry = recorder.build_cmd(st, Path(directory), "Test", self.slot, 1)
                self.assertEqual(original, retry)


if __name__ == "__main__":
    unittest.main()
