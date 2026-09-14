import copy
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import recorder
from schedules import merge_station_configs


def empty_schedule():
    return {d: [] for d in recorder.DAYS}


class ScheduleTests(unittest.TestCase):
    def station(self):
        s = {
            "name": "Test",
            "url": "https://example.invalid/live",
            "enabled": True,
            "one_file_per_program": True,
            "schedule": empty_schedule(),
        }
        return s

    def test_nominal_next_program_beats_previous_post_padding(self):
        st = self.station()
        st["schedule"]["tue"] = [
            {"start": "20:00", "end": "21:00", "title": "A", "pre": 2, "post": 3},
            {"start": "21:00", "end": "23:00", "title": "B", "pre": 2, "post": 3},
        ]
        before = datetime(2026, 9, 1, 20, 59, 59, tzinfo=timezone.utc)
        boundary = datetime(2026, 9, 1, 21, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(recorder.active(st, before)[2], "A")
        self.assertEqual(recorder.active(st, boundary)[2], "B")

    def test_midnight_program_is_active_after_midnight(self):
        st = self.station()
        st["schedule"]["tue"] = [
            {"start": "22:30", "end": "01:00", "title": "Night", "pre": 2, "post": 3},
        ]
        dt = datetime(2026, 9, 2, 0, 30, 0, tzinfo=timezone.utc)
        ok, _, title, _ = recorder.active(st, dt)
        self.assertTrue(ok)
        self.assertEqual(title, "Night")

    def test_post_padding_is_active(self):
        st = self.station()
        st["schedule"]["tue"] = [
            {"start": "20:00", "end": "21:00", "title": "A", "pre": 0, "post": 3},
        ]
        dt = datetime(2026, 9, 1, 21, 2, 0, tzinfo=timezone.utc)
        self.assertEqual(recorder.active(st, dt)[2], "A")


class RecordingFormatTests(unittest.TestCase):
    def test_build_cmd_uses_mp3_container_without_transcoding(self):
        station = {
            "name": "Radio Kampus",
            "url": "https://stream.radiokampus.fm/kampus",
            "detected_ext": "mp3",
            "segment_minutes": 60,
        }
        cmd = recorder.build_cmd(station, Path("/recordings/Radio_Kampus"), "", None)
        self.assertIn("copy", cmd)
        self.assertEqual(cmd[cmd.index("-segment_format") + 1], "mp3")
        self.assertTrue(cmd[-1].endswith(".mp3"))

    def test_recording_result_does_not_reuse_an_old_file(self):
        previous_out = recorder.OUT
        try:
            with tempfile.TemporaryDirectory() as temp:
                recorder.OUT = Path(temp)
                station_dir = recorder.OUT / "Radio_Kampus" / "2026-09-14"
                station_dir.mkdir(parents=True)
                old = station_dir / "old.mp3"
                old.write_bytes(b"old recording")
                started = datetime.fromtimestamp(old.stat().st_mtime + 10, tz=timezone.utc)
                self.assertTrue(recorder.recording_result("Radio Kampus", started)["empty"])
        finally:
            recorder.OUT = previous_out

    def test_recording_result_reports_new_empty_file(self):
        previous_out = recorder.OUT
        try:
            with tempfile.TemporaryDirectory() as temp:
                recorder.OUT = Path(temp)
                station_dir = recorder.OUT / "Radio_Kampus" / "2026-09-14"
                station_dir.mkdir(parents=True)
                started = datetime.now(timezone.utc)
                output = station_dir / "new.mp3"
                output.touch()
                result = recorder.recording_result("Radio Kampus", started)
                self.assertTrue(result["empty"])
                self.assertEqual(result["file"], "Radio_Kampus/2026-09-14/new.mp3")
        finally:
            recorder.OUT = previous_out

    def test_logged_ffmpeg_command_hides_stream_url(self):
        command = ["ffmpeg", "-i", "https://radio.example/live?token=secret", "-c:a", "copy"]
        logged = recorder.command_for_log(command)
        self.assertNotIn("secret", logged)
        self.assertIn("<stream-url>", logged)


class MergeTests(unittest.TestCase):
    def test_merge_preserves_existing_settings_and_appends_new_station(self):
        existing = [{
            "name": "Radio A",
            "url": "https://old.example/live",
            "schedule": {"mon": [{"start": "10:00", "end": "11:00", "title": "Old"}]},
        }]
        incoming = [
            {
                "name": "radio a",
                "url": "https://new.example/live",
                "schedule": {"mon": [
                    {"start": "10:00", "end": "11:00", "title": "Old"},
                    {"start": "11:00", "end": "12:00", "title": "New"},
                ]},
            },
            {"name": "Radio B", "url": "https://b.example/live", "schedule": {}},
        ]
        merged, stats = merge_station_configs(copy.deepcopy(existing), incoming)
        self.assertEqual([x["name"] for x in merged], ["Radio A", "Radio B"])
        self.assertEqual(merged[0]["url"], "https://old.example/live")
        self.assertEqual([x["title"] for x in merged[0]["schedule"]["mon"]], ["Old", "New"])
        self.assertEqual(stats["stations_added"], 1)
        self.assertEqual(stats["schedules_added"], 1)
        self.assertEqual(stats["duplicates_skipped"], 1)

    def test_merge_skips_overlapping_slot(self):
        existing = [{
            "name": "Radio A",
            "url": "x",
            "schedule": {"mon": [{"start": "10:00", "end": "11:00", "title": "Old"}]},
        }]
        incoming = [{
            "name": "Radio A",
            "url": "y",
            "schedule": {"mon": [{"start": "10:30", "end": "11:30", "title": "Conflict"}]},
        }]
        merged, stats = merge_station_configs(existing, incoming)
        self.assertEqual(len(merged[0]["schedule"]["mon"]), 1)
        self.assertEqual(stats["conflicts_skipped"], 1)


if __name__ == "__main__":
    unittest.main()
