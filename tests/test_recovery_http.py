"""Isolated long-running and HTTP disconnect tests for the actual IRR worker.

Runs only when IRR_DOCKER_NETWORK_TEST=1; never contacts public stations.
"""
import hashlib
import os
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import recorder


class RadioStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests += 1
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.end_headers()
        sent = 0
        try:
            while not self.server.stop_stream.is_set():
                for offset in range(0, len(self.server.sample), 2048):
                    if self.server.stop_stream.is_set():
                        break
                    self.wfile.write(self.server.sample[offset:offset + 2048])
                    self.wfile.flush()
                    sent += 1
                    time.sleep(0.08)
                    if self.server.disconnect and sent >= 24:
                        # No HTTP shutdown response; the TCP connection simply closes.
                        self.server.drops += 1
                        self.close_connection = True
                        return
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        self.close_connection = True

    def log_message(self, *_args):
        pass


@unittest.skipUnless(os.environ.get("IRR_DOCKER_NETWORK_TEST") == "1",
                     "isolated network integration test only")
class LiveHttpRecoveryTests(unittest.TestCase):
    def _exercise(self, disconnect, seconds):
        with tempfile.TemporaryDirectory(prefix="irr-http-test-") as tmp:
            root = Path(tmp)
            sample = root / "sample.mp3"
            subprocess.run([
                "ffmpeg", "-v", "error", "-nostdin", "-f", "lavfi",
                "-i", "sine=frequency=600:duration=2",
                "-c:a", "libmp3lame", "-b:a", "96k", str(sample)
            ], check=True, timeout=30)
            server = ThreadingHTTPServer(("127.0.0.1", 0), RadioStreamHandler)
            server.sample = sample.read_bytes()
            server.requests = 0
            server.drops = 0
            server.disconnect = disconnect
            server.stop_stream = threading.Event()
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()

            station = {"name": "Local Radio", "enabled": True,
                       "url": "http://127.0.0.1:%d/stream" % server.server_port,
                       "codec": "mp3", "one_file_per_program": True}
            slot = {"_identity": "local:single-program", "title": "Synthetic"}
            schedule = threading.Event()
            schedule.set()
            original = (recorder.running, recorder.procs, recorder.state)
            recordings = root / "recordings"
            recordings.mkdir()
            history = []

            def active(_station, _date):
                if schedule.is_set():
                    return True, "12:00-13:00", "Synthetic", slot
                return False, "poza harmonogramem", "", None

            try:
                recorder.running, recorder.procs, recorder.state = True, {}, {}
                with patch.object(recorder, "OUT", recordings), \
                     patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True), \
                     patch.object(recorder, "RETRY", 1), \
                     patch.object(recorder, "load", return_value=[station]), \
                     patch.object(recorder, "active", side_effect=active), \
                     patch.object(recorder, "next_schedule", return_value=None), \
                     patch.object(recorder, "ffprobe_info",
                                  return_value={"ok": True, "ext": "mp3", "codec": "mp3"}), \
                     patch.object(recorder, "notify"), \
                     patch.object(recorder, "add_exec", side_effect=history.append):
                    worker = threading.Thread(target=recorder.worker,
                                              args=(station["name"],), daemon=True)
                    worker.start()
                    try:
                        start = time.monotonic()
                        first_file = None
                        first_size = None
                        while time.monotonic() - start < seconds:
                            files = sorted(recordings.rglob("*.mp3"))
                            if files:
                                first_file = first_file or files[0]
                                if first_file.exists():
                                    n = first_file.stat().st_size
                                    if first_size is None and n > 3000:
                                        first_size = n
                            time.sleep(0.25)
                        self.assertIsNotNone(first_file, "no audio file created")
                        self.assertIsNotNone(first_size, "recorded no usable data")
                        self.assertGreater(first_file.stat().st_size, first_size,
                                           "audio stopped growing")
                        if disconnect:
                            self.assertGreaterEqual(server.drops, 2,
                                "server did not close at least two real HTTP connections")
                            self.assertGreaterEqual(server.requests, 3,
                                "FFmpeg did not reconnect to the HTTP server")
                        else:
                            self.assertEqual(server.drops, 0)

                        # End the simulated programme. The worker must stop and
                        # must not create further files once the schedule is closed.
                        schedule.clear()
                        deadline = time.monotonic() + 12
                        while time.monotonic() < deadline:
                            if station["name"] not in recorder.procs:
                                break
                            time.sleep(0.2)
                        self.assertNotIn(station["name"], recorder.procs)
                        files = sorted(recordings.rglob("*.mp3"))
                        checksums = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in files}
                        self.assertTrue(checksums)
                        time.sleep(2)
                        self.assertEqual(
                            checksums,
                            {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in recordings.rglob("*.mp3")}
                        )
                        print("HTTP_TEST_OK drops=%d requests=%d bytes=%d files=%d" % (
                            server.drops, server.requests,
                            sum(p.stat().st_size for p in files), len(files)))
                    finally:
                        schedule.clear()
                        recorder.running = False
                        worker.join(timeout=8)
                        if worker.is_alive():
                            self.fail("worker did not terminate")
            finally:
                recorder.running = False
                for process in list(recorder.procs.values()):
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=5)
                recorder.running, recorder.procs, recorder.state = original
                server.stop_stream.set()
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_continuous_recording_for_35_seconds(self):
        self._exercise(disconnect=False, seconds=35)

    def test_http_connection_drops_and_reconnects(self):
        self._exercise(disconnect=True, seconds=25)


if __name__ == "__main__":
    unittest.main()
