"""End-to-end worker test in an isolated Docker container.

Starts a local synthetic MP3 HTTP server and the real recorder.worker.
Force-kills two real FFmpeg processes, then closes the artificial schedule.
No real stations, user settings or host recording mounts are used.
"""
import hashlib
import shutil
import subprocess
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import recorder


class SyntheticStream(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.end_headers()
        try:
            while True:
                self.wfile.write(self.server.audio)
                self.wfile.flush()
                time.sleep(0.08)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def log_message(self, *_args):
        pass


class ContainerRecoveryTests(unittest.TestCase):
    def test_real_worker_restores_after_failures_and_respects_schedule_end(self):
        if not shutil.which("ffmpeg"):
            self.skipTest("ffmpeg unavailable")
        with TemporaryDirectory(prefix="irr-container-") as directory:
            root = Path(directory)
            audio = root / "input.mp3"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
                "-f", "lavfi", "-i", "sine=frequency=700:duration=2",
                "-c:a", "libmp3lame", "-b:a", "96k", str(audio)
            ], check=True, timeout=25)
            server = ThreadingHTTPServer(("127.0.0.1", 0), SyntheticStream)
            server.audio = audio.read_bytes()
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()

            station = {"name": "Synthetic Radio", "enabled": True,
                       "url": "http://127.0.0.1:%s/audio.mp3" % server.server_port,
                       "codec": "mp3", "one_file_per_program": True}
            slot = {"_identity": "simulated:programme:1",
                    "start": "12:00", "end": "13:00", "title": "Test"}
            history = []
            schedule_open = threading.Event()
            schedule_open.set()
            prior_running, prior_state, prior_procs = (
                recorder.running, recorder.state, recorder.procs)
            recording_root = root / "recordings"
            recording_root.mkdir()

            def active_simulated(_station, _dt):
                if schedule_open.is_set():
                    return True, "12:00-13:00", "Test", slot
                return False, "poza harmonogramem", "", None

            def await_output(suffix, timeout=20):
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    candidates = list(recording_root.rglob("*" + suffix))
                    for p in candidates:
                        if p.is_file() and p.stat().st_size > 2048:
                            return p
                    time.sleep(0.1)
                self.fail("No output with suffix %s" % suffix)

            try:
                recorder.running, recorder.state, recorder.procs = True, {}, {}
                with patch.object(recorder, "OUT", recording_root), \
                     patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True), \
                     patch.object(recorder, "RETRY", 1), \
                     patch.object(recorder, "load", return_value=[station]), \
                     patch.object(recorder, "active", side_effect=active_simulated), \
                     patch.object(recorder, "next_schedule", return_value=None), \
                     patch.object(recorder, "ffprobe_info", return_value={"ok": True, "ext": "mp3", "codec": "mp3"}), \
                     patch.object(recorder, "add_exec", side_effect=history.append), \
                     patch.object(recorder, "notify"):
                    worker = threading.Thread(target=recorder.worker,
                                              args=(station["name"],), daemon=True)
                    worker.start()
                    try:
                        preserved = []
                        for suffix in ("_Test.mp3", "_Test_part02.mp3", "_Test_part03.mp3"):
                            output = await_output(suffix)
                            proc = recorder.procs.get(station["name"])
                            self.assertIsNotNone(proc)
                            self.assertIsNone(proc.poll())
                            proc.kill()
                            proc.wait(timeout=5)
                            deadline = time.monotonic() + 10
                            while time.monotonic() < deadline and proc is recorder.procs.get(station["name"]):
                                time.sleep(0.05)
                            digest = hashlib.sha256(output.read_bytes()).hexdigest()
                            preserved.append((output, digest))
                            for old, checksum in preserved:
                                self.assertTrue(old.is_file())
                                self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(), checksum)

                        # After three failures, the schedule closes: no fourth recording.
                        schedule_open.clear()
                        deadline = time.monotonic() + 10
                        while time.monotonic() < deadline and len(history) < 3:
                            time.sleep(0.1)
                        self.assertGreaterEqual(len(history), 3)
                        count = len(list(recording_root.rglob("*.mp3")))
                        time.sleep(3)
                        self.assertEqual(len(list(recording_root.rglob("*.mp3"))), count)
                        self.assertEqual(count, 3)
                        self.assertGreaterEqual(recorder.state[station["name"]]["reconnects"], 2)
                    finally:
                        schedule_open.clear()
                        recorder.running = False
                        worker.join(timeout=8)
                        if worker.is_alive():
                            self.fail("worker did not stop")
            finally:
                recorder.running = False
                for process in list(recorder.procs.values()):
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=5)
                recorder.procs, recorder.state = prior_procs, prior_state
                recorder.running = prior_running
                server.shutdown()
                server.server_close()
                server_thread.join(timeout=4)


if __name__ == "__main__":
    unittest.main()
