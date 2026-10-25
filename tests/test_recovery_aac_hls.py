"""AAC ADTS and HLS/AAC integration tests using local synthetic sources only."""
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


class AudioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests += 1
        if self.path == "/radio.aac":
            self.send_response(200)
            self.send_header("Content-Type", "audio/aac")
            self.end_headers()
            try:
                # Repeatedly terminate a genuine HTTP AAC connection.
                for pos in range(0, len(self.server.aac), 768):
                    self.wfile.write(self.server.aac[pos:pos+768])
                    self.wfile.flush()
                    time.sleep(0.025)
                self.server.drops += 1
            except (OSError, BrokenPipeError, ConnectionResetError):
                pass
            self.close_connection = True
            return
        p = (self.server.hls / self.path.lstrip("/")).resolve()
        if not p.is_relative_to(self.server.hls.resolve()) or not p.is_file():
            self.send_error(404)
            return
        data = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.apple.mpegurl"
                         if p.suffix == ".m3u8" else "video/MP2T")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            for pos in range(0, len(data), 512):
                self.wfile.write(data[pos:pos+512])
                self.wfile.flush()
                time.sleep(0.01)
        except (OSError, BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *_args):
        pass


@unittest.skipUnless(os.environ.get("IRR_DOCKER_AAC_HLS_TEST") == "1",
                     "dedicated isolated AAC/HLS tests only")
class AacHlsTests(unittest.TestCase):
    def test_local_adts_aac_http_reconnect(self):
        with tempfile.TemporaryDirectory(prefix="irr-aac-") as tmp:
            root = Path(tmp)
            src = root / "source.aac"
            subprocess.run(["ffmpeg", "-v", "error", "-nostdin",
                            "-f", "lavfi", "-i", "sine=frequency=800:duration=3",
                            "-c:a", "aac", "-b:a", "96k", "-f", "adts",
                            str(src)], check=True, timeout=25)
            server = ThreadingHTTPServer(("127.0.0.1", 0), AudioHandler)
            server.aac = src.read_bytes()
            server.hls = root
            server.requests = server.drops = 0
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            output = root / "recordings"
            output.mkdir()
            station = {"name":"SyntheticAAC", "url":
                       "http://127.0.0.1:%d/radio.aac" % server.server_port,
                       "codec":"aac", "one_file_per_program":True}
            try:
                with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True):
                    cmd = recorder.build_cmd(station, output, "Test",
                                             {"_identity":"one"}, 0)
                Path(cmd[-1]).parent.mkdir(parents=True, exist_ok=True)
                p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.PIPE)
                try:
                    time.sleep(10)
                finally:
                    if p.poll() is None:
                        p.terminate()
                    p.communicate(timeout=10)
                result = Path(cmd[-1])
                self.assertGreater(result.stat().st_size, 5000)
                self.assertGreaterEqual(server.requests, 2)
                self.assertGreaterEqual(server.drops, 1)
                print("AAC_OK bytes=%d requests=%d drops=%d" %
                      (result.stat().st_size, server.requests, server.drops))
            finally:
                server.shutdown()
                server.server_close()
                t.join(timeout=5)

    def test_hls_aac_restart_writes_new_fragment(self):
        with tempfile.TemporaryDirectory(prefix="irr-hls-") as tmp:
            root = Path(tmp)
            hls = root / "hls"
            hls.mkdir()
            subprocess.run([
                "ffmpeg", "-v", "error", "-nostdin", "-f", "lavfi",
                "-i", "sine=frequency=900:duration=8",
                "-c:a", "aac", "-b:a", "96k", "-f", "hls",
                "-hls_time", "1", "-hls_list_size", "0",
                "-hls_playlist_type", "vod", str(hls/"index.m3u8")
            ], check=True, timeout=30)
            server = ThreadingHTTPServer(("127.0.0.1", 0), AudioHandler)
            server.aac = b""
            server.hls = hls
            server.requests = server.drops = 0
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            output = root / "recordings"
            output.mkdir()
            station = {"name":"SyntheticHLS", "url":
                       "http://127.0.0.1:%d/index.m3u8" % server.server_port,
                       "codec":"aac", "one_file_per_program":True}
            files = []
            try:
                for part in range(2):
                    with patch.object(recorder, "PRESERVE_RECOVERY_PARTS", True):
                        cmd = recorder.build_cmd(station, output, "HLS",
                                                {"_identity":"one"}, part)
                    target = Path(cmd[-1])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                            stderr=subprocess.PIPE)
                    try:
                        deadline = time.monotonic() + 20
                        while time.monotonic() < deadline:
                            if target.exists() and target.stat().st_size > 5000:
                                break
                            if proc.poll() is not None:
                                self.fail("HLS FFmpeg ended early: " +
                                          proc.stderr.read().decode(errors="replace")[-1000:])
                            time.sleep(0.1)
                        else:
                            self.fail("HLS FFmpeg wrote no audio")
                    finally:
                        if proc.poll() is None:
                            proc.terminate()
                        proc.communicate(timeout=10)
                    self.assertGreater(target.stat().st_size, 5000)
                    files.append(target)
                self.assertNotEqual(files[0], files[1])
                self.assertIn("_part02.aac", files[1].name)
                self.assertGreaterEqual(server.requests, 4)
                print("HLS_AAC_OK parts=%d sizes=%s requests=%d" %
                      (len(files), [p.stat().st_size for p in files], server.requests))
            finally:
                server.shutdown()
                server.server_close()
                t.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
