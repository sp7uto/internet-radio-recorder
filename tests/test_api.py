import json
import tempfile
import threading
import unittest
from pathlib import Path

from api import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = self.root / "config"
        self.recordings = self.root / "recordings"
        self.config.mkdir(); self.recordings.mkdir()
        self.stations = [{"name": "Test", "url": "https://example.invalid/live", "enabled": True, "schedule": {}}]
        self.ensure_calls = 0

        def load(): return self.stations
        def save(stations): self.stations = stations
        def ensure(): self.ensure_calls += 1

        app = create_app(load, save, {}, threading.RLock(), ensure,
                         lambda url: {"ok": bool(url)}, self.recordings, self.config)
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_frontend_is_served_from_template_and_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/static/app.js", response.data)
        self.assertNotIn(b"function render()", response.data)
        asset = self.client.get("/static/app.js")
        self.assertEqual(asset.status_code, 200)
        asset.close()

    def test_data_and_save_routes(self):
        self.assertEqual(self.client.get("/api/data").get_json()["stations"][0]["name"], "Test")
        response = self.client.post("/api/save", json={"stations": [{"name": "Nowa", "schedule": {}}]})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["ok"])
        self.assertEqual(self.stations[0]["name"], "Nowa")
        self.assertEqual(self.ensure_calls, 1)

    def test_invalid_save_is_rejected(self):
        response = self.client.post("/api/save", json={"stations": "not-a-list"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["ok"])

    def test_media_path_traversal_is_rejected(self):
        outside = self.root / "secret.txt"
        outside.write_text("secret", encoding="utf-8")
        self.assertEqual(self.client.get("/media?path=../secret.txt").status_code, 404)
        self.assertEqual(self.client.post("/api/delete?path=../secret.txt").status_code, 404)
        self.assertTrue(outside.exists())

    def test_backup_and_replace_import(self):
        (self.config / "stations.json").write_text(json.dumps(self.stations), encoding="utf-8")
        backup = self.client.get("/api/backup")
        self.assertEqual(backup.status_code, 200)
        response = self.client.post("/api/import-backup?mode=replace",
                                    json={"stations": [{"name": "Imported", "schedule": {}}]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.stations[0]["name"], "Imported")
        self.assertTrue(list(self.config.glob("stations.before-import-*.json")))


if __name__ == "__main__":
    unittest.main()
