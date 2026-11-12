"""Isolated FFmpeg integration test; never touches user streams or recordings."""
import hashlib
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


class _StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.end_headers()
        try:
            # Send synthetic MP3, then deliberately cut the HTTP connection.
            for offset in range(0, len(self.server.audio), 1024):
                self.wfile.write(self.server.audio[offset:offset + 1024])
                self.wfile.flush()
                time.sleep(0.008)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        self.close_connection = True

    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg executable not installed")
class RecoveryIntegrationTests(unittest.TestCase):
    def test_forced_disconnect_then_restart_never_overwrites_fragment(self):
        with tempfile.TemporaryDirectory(prefix="irr-recovery-") as tmp:
            root = Path(tmp)
            audio = root / "synthetic.mp3"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
                "-f", "lavfi", "-i", "sine=frequency=1000:duration=12",
                "-c:a", "libmp3lame", "-b:a", "96k", str(audio)
            ], check=True, timeout=30)
            server = ThreadingHTTPServer(("127.0.0.1", 0), _StreamHandler)
            server.audio = audio.read_bytes()
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            st = {
                "name": "Synthetic Station",
                "url": "http://127.0.0.1:%d/audio.mp3" % server.server_port,
                "codec": "mp3",
                "one_file_per_program": True
            }
            slot = {"start": "12:00", "end": "13:00", "title": "Synthetic"}
            output_dir = root / "recordings"
            (output_dir / time.strftime("%Y-%m-%d")).mkdir(parents=True)
            outputs = []
            try:
                with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True):
                    for part in range(3):
                        cmd = recorder.build_cmd(st, output_dir, "Synthetic", slot, part)
                        output = Path(cmd[-1])
                        self.assertNotIn("-y", cmd)
                        process = subprocess.Popen(
                            cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        try:
                            deadline = time.monotonic() + 12
                            while time.monotonic() < deadline:
                                if output.exists() and output.stat().st_size > 1500:
                                    break
                                if process.poll() is not None:
                                    self.fail("ffmpeg exited before writing audio")
                                time.sleep(0.05)
                            else:
                                self.fail("ffmpeg did not produce audio")
                        finally:
                            # Simulate a sudden recording-process failure.
                            if process.poll() is None:
                                process.kill()
                            process.wait(timeout=5)
                        outputs.append((output, hashlib.sha256(output.read_bytes()).hexdigest()))
                        self.assertEqual(len({str(item[0]) for item in outputs}), len(outputs))
                        for previous, digest in outputs:
                            self.assertTrue(previous.exists())
                            self.assertGreater(previous.stat().st_size, 1500)
                            self.assertEqual(hashlib.sha256(previous.read_bytes()).hexdigest(), digest)
                self.assertEqual(len(outputs), 3)
                self.assertIn("_part02.mp3", outputs[1][0].name)
                self.assertIn("_part03.mp3", outputs[2][0].name)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
