import copy
import unittest
from datetime import datetime, timezone

import recorder
from web import merge_station_configs


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
