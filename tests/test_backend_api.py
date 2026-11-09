#!/usr/bin/env python3
"""
Unit and Integration Tests for ADos Backend API Server
======================================================
Tests pure standard library API server endpoints, CORS headers, process management,
builder execution, and DuckHunter compilation.
"""

import json
import os
import sys
import threading
import time
import unittest
import urllib.request
import urllib.error

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.api import (
    ADosAPIHandler,
    ThreadingHTTPServer,
    VERSION,
    SUPPORTED_TOOLS,
    execute_build,
)


class TestADosBackendAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start ThreadingHTTPServer on an ephemeral port (port 0)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ADosAPIHandler)
        cls.host, cls.port = cls.server.server_address
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        # Give server time to bind
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"

    def _get(self, path: str):
        req = urllib.request.Request(self._url(path), method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return resp.status, resp.headers, data

    def _post(self, path: str, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self._url(path),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return resp.status, resp.headers, data

    # 1. Stdlib check
    def test_api_uses_only_stdlib(self):
        api_path = os.path.join(REPO_ROOT, "backend", "api.py")
        with open(api_path, "r", encoding="utf-8") as f:
            content = f.read()
        forbidden = ["fastapi", "uvicorn", "flask", "aiohttp", "requests", "django"]
        for pkg in forbidden:
            self.assertNotIn(f"import {pkg}", content)
            self.assertNotIn(f"from {pkg}", content)

    # 2. Health Endpoint
    def test_health_endpoint(self):
        status, headers, data = self._get("/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "ADos-API")
        self.assertEqual(data.get("version"), VERSION)
        self.assertIn("uptime", data)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "*")

    # 3. Status Endpoint
    def test_status_endpoint(self):
        for path in ("/api/status", "/status"):
            status, _, data = self._get(path)
            self.assertEqual(status, 200)
            self.assertEqual(data.get("status"), "running")
            self.assertEqual(data.get("service"), "ADos-API")
            self.assertIsInstance(data.get("tools"), list)
            self.assertGreaterEqual(data.get("devices_count", 0), 2)

    # 4. Devices Endpoints
    def test_devices_list(self):
        for path in ("/api/devices", "/devices"):
            status, _, data = self._get(path)
            self.assertEqual(status, 200)
            self.assertIn("devices", data)
            devices = data["devices"]
            self.assertIn("samsung_s10", devices)
            self.assertIn("generic_arm64", devices)

    def test_device_model_found(self):
        status, _, data = self._get("/api/devices/samsung_s10")
        self.assertEqual(status, 200)
        self.assertEqual(data.get("brand"), "Samsung")
        self.assertEqual(data.get("arch"), "arm64")

    def test_device_model_not_found(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/api/devices/nonexistent_model_xyz")
        self.assertEqual(ctx.exception.code, 404)
        err_data = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("error", err_data)

    # 5. Toolsets and Firmware Endpoints
    def test_toolsets_endpoint(self):
        for path in ("/api/toolsets", "/toolsets"):
            status, _, data = self._get(path)
            self.assertEqual(status, 200)
            self.assertIn("toolsets", data)
            self.assertIn("profiles", data)

    def test_firmware_endpoint(self):
        for path in ("/api/firmware", "/firmware"):
            status, _, data = self._get(path)
            self.assertEqual(status, 200)
            self.assertIn("adapters", data)

    # 6. Builder Execution (Dry Run & Real validation)
    def test_builder_dry_run(self):
        payload = {
            "device": "samsung_s10",
            "release": "11",
            "rootfs": "minimal",
            "tools": "essential",
            "type": "twrp",
            "dry_run": True,
        }
        for path in ("/api/tools/builder/execute", "/build"):
            status, _, data = self._post(path, payload)
            self.assertEqual(status, 200)
            self.assertEqual(data.get("status"), "success")
            self.assertTrue(data.get("dry_run"))
            self.assertEqual(data.get("device"), "samsung_s10")

    def test_builder_missing_device_raises_400(self):
        payload = {"release": "11", "dry_run": True}
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("/api/tools/builder/execute", payload)
        self.assertEqual(ctx.exception.code, 400)
        err = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("error", err)

    def test_builder_unsupported_release_raises_400(self):
        payload = {"device": "samsung_s9", "release": "14", "dry_run": True}
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("/api/tools/builder/execute", payload)
        self.assertEqual(ctx.exception.code, 400)

    # 7. DuckHunter Compilation
    def test_duckhunter_compile(self):
        payload = {
            "script": "STRING Hello World\nDELAY 200\nENTER",
            "hid_dev": "/dev/hidg0"
        }
        for path in ("/api/tools/duckhunter/compile", "/duckhunter/compile"):
            status, _, data = self._post(path, payload)
            self.assertEqual(status, 200)
            self.assertEqual(data.get("status"), "compiled")
            self.assertGreater(data.get("commands_count", 0), 0)
            self.assertIn("shell_script", data)

    def test_duckhunter_missing_script(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("/api/tools/duckhunter/compile", {})
        self.assertEqual(ctx.exception.code, 400)

    # 8. Process Execution, Logging & Stopping
    def test_run_tool_python_process_and_logs(self):
        # Run standard python process via API
        payload = {
            "tool": "python",
            "args": '-c "import time; print(\'API_PROCESS_OUTPUT_TEST\'); time.sleep(0.2)"'
        }
        status, _, data = self._post("/api/tools/python/execute", payload)
        self.assertEqual(status, 200)
        pid = data.get("pid")
        self.assertIsInstance(pid, int)
        self.assertEqual(data.get("status"), "started")

        # Give process time to emit output and finish
        time.sleep(0.4)

        # Retrieve log output
        for log_path in (f"/api/logs/{pid}", f"/tool-output/{pid}"):
            l_status, _, log_data = self._get(log_path)
            self.assertEqual(l_status, 200)
            self.assertEqual(log_data.get("pid"), pid)
            self.assertIn("API_PROCESS_OUTPUT_TEST", log_data.get("output", ""))

    def test_run_tool_unsupported_rejected(self):
        payload = {"tool": "not_in_supported_tools_xyz", "args": ""}
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("/run-tool", payload)
        self.assertEqual(ctx.exception.code, 400)

    def test_stop_tool_nonexistent(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("/stop-tool", {"pid": 99999999})
        self.assertEqual(ctx.exception.code, 404)

    # 9. RAM Stats
    def test_ram_stats(self):
        for path in ("/api/ram-stats", "/ram-stats"):
            status, _, data = self._get(path)
            self.assertEqual(status, 200)
            self.assertIsInstance(data, dict)

    # 10. CORS Pre-Flight Options
    def test_cors_options(self):
        req = urllib.request.Request(self._url("/api/health"), method="OPTIONS")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
            self.assertIn("GET", resp.headers.get("Access-Control-Allow-Methods", ""))

    # 11. Unknown Endpoint 404
    def test_unknown_endpoint_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/api/unknown_route_404")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
