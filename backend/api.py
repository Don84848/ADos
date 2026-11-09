#!/usr/bin/env python3
"""
ADos Backend API Server
=======================
Pure Python standard library HTTP API server (http.server + subprocess).
Listens on 127.0.0.1:8000 by default. Zero external dependencies.

Endpoints
---------
GET  /api/health                  -> {"status": "ok", "service": "ADos-API", "version": "1.0.0", "uptime": ...}
GET  /api/status, /status         -> {"status": "running", "service": "ADos-API", ...}
GET  /api/devices, /devices       -> list of supported devices from config/devices.json
GET  /api/devices/<model>         -> hardware profile for specific device
GET  /api/toolsets, /toolsets     -> toolsets and profiles from config/toolsets.json
GET  /api/firmware, /firmware     -> wireless firmware manifest
POST /api/tools/builder/execute   -> execute ADos builder / package generation (supports dry_run)
POST /build                       -> alias for builder execute
POST /api/tools/duckhunter/compile-> compile DuckyScript into BadUSB shell commands
POST /duckhunter/compile          -> alias for duckhunter compile
POST /api/tools/<name>/execute    -> run tool subprocess (pid returned)
POST /run-tool                    -> alias for tool execution
POST /api/tools/<name>/stop       -> terminate running tool by pid
POST /stop-tool                   -> alias for tool termination
GET  /api/logs/<job_id>           -> retrieve buffered output for a process
GET  /tool-output/<pid>           -> alias for log output
GET  /api/ram-stats, /ram-stats   -> system RAM statistics
OPTIONS *                         -> CORS pre-flight response
"""

import argparse
import io
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
try:
    from http.server import ThreadingHTTPServer
except ImportError:
    class ThreadingHTTPServer(HTTPServer):
        """Fallback threaded HTTPServer."""
        def process_request(self, request, client_address):
            t = threading.Thread(target=self._handle_request, args=(request, client_address), daemon=True)
            t.start()

        def _handle_request(self, request, client_address):
            try:
                self.finish_request(request, client_address)
            except Exception:
                self.handle_error(request, client_address)
            finally:
                self.shutdown_request(request)

from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Repo Root Resolution & Core Imports
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.builder_engine import ADosBuilderEngine, DeviceNotFoundError, UnsupportedReleaseError
from core.package_generator import PackageGenerator
from tools.duckhunter.duckhunter import DuckHunterCompiler

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION = "1.0.0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
START_TIME = time.time()

SUPPORTED_TOOLS = [
    "builder",
    "duckhunter",
    "nmap",
    "sqlmap",
    "aircrack-ng",
    "wifite",
    "hydra",
    "hashcat",
    "bettercap",
    "gobuster",
    "msfconsole",
    "nikto",
    "masscan",
    "john",
    "wfuzz",
    "netcat",
    "wireshark",
    "adb",
    "ping",
    "python",
    "python3",
    "bash",
    "sh",
]

# ---------------------------------------------------------------------------
# Process Store
# ---------------------------------------------------------------------------

_processes: dict[int, dict] = {}
_processes_lock = threading.Lock()


def _reader_thread(pid: int) -> None:
    """Read stdout+stderr from a Popen process and buffer it safely."""
    with _processes_lock:
        entry = _processes.get(pid)
    if entry is None:
        return

    proc: subprocess.Popen = entry["proc"]
    lock: threading.Lock = entry["lock"]
    buf: io.StringIO = entry["output"]

    try:
        for line in proc.stdout:
            with lock:
                buf.write(line)
    except Exception:
        pass
    finally:
        proc.wait()
        with lock:
            entry["returncode"] = proc.returncode


# ---------------------------------------------------------------------------
# Response Helpers
# ---------------------------------------------------------------------------

def _send_json(handler: BaseHTTPRequestHandler, code: int, data) -> None:
    body = json.dumps(data, indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _send_error(handler: BaseHTTPRequestHandler, code: int, message: str) -> None:
    _send_json(handler, code, {"error": message})


def _read_body(handler: BaseHTTPRequestHandler) -> dict:
    """Read and parse a JSON request body."""
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8"))


# ---------------------------------------------------------------------------
# Builder Execution Logic
# ---------------------------------------------------------------------------

def execute_build(params: dict) -> dict:
    device = params.get("device", "").strip()
    release = str(params.get("release", "")).strip()
    rootfs = params.get("rootfs", "minimal").strip()
    tools_profile = params.get("tools", "essential").strip()
    pkg_type = params.get("type", "twrp").strip().lower()
    debloat_samsung = bool(params.get("debloat_samsung", False))
    dry_run = bool(params.get("dry_run", False))
    output_custom = params.get("output")

    if not device or not release:
        raise ValueError("Both 'device' and 'release' are required.")

    engine = ADosBuilderEngine(repo_root=REPO_ROOT)
    profile = engine.get_device_profile(device, release)
    rootfs_info = engine.resolve_rootfs(profile.get("arch", "arm64"), rootfs)

    if dry_run:
        return {
            "status": "success",
            "dry_run": True,
            "device": device,
            "release": release,
            "profile": profile,
            "rootfs": rootfs_info,
            "package_path": None,
            "sha256": None,
            "message": "DRY-RUN validation completed successfully. All configurations are valid!"
        }

    # Staging files
    staging = {
        "system/etc/ados-release": f"ADos 1.0 (Device: {device}, Release: {release})",
        "system/etc/ados/device_profile.json": json.dumps(profile, indent=2),
        "data/ados/rootfs_manifest.json": json.dumps(rootfs_info, indent=2)
    }

    is_samsung = profile.get("brand") == "Samsung"
    debloat_script_path = os.path.join(REPO_ROOT, "scripts", "debloat-samsung.sh")
    if (debloat_samsung or is_samsung) and os.path.exists(debloat_script_path):
        with open(debloat_script_path, "r", encoding="utf-8") as f:
            staging["data/ados/scripts/debloat-samsung.sh"] = f.read()

    gadget_script_path = os.path.join(REPO_ROOT, "scripts", "setup-usb-gadget.sh")
    if os.path.exists(gadget_script_path):
        with open(gadget_script_path, "r", encoding="utf-8") as f:
            staging["data/ados/scripts/setup-usb-gadget.sh"] = f.read()

    tools_script_path = os.path.join(REPO_ROOT, "scripts", "install-tools.sh")
    if os.path.exists(tools_script_path):
        with open(tools_script_path, "r", encoding="utf-8") as f:
            staging["data/ados/scripts/install-tools.sh"] = f.read()

    menu_script_path = os.path.join(REPO_ROOT, "scripts", "ados-menu.sh")
    if os.path.exists(menu_script_path):
        with open(menu_script_path, "r", encoding="utf-8") as f:
            content = f.read()
            staging["data/ados/scripts/ados-menu.sh"] = content
            staging["system/bin/ados-menu"] = content

    toolsets_config_path = os.path.join(REPO_ROOT, "config", "toolsets.json")
    if os.path.exists(toolsets_config_path):
        with open(toolsets_config_path, "r", encoding="utf-8") as f:
            staging["data/ados/config/toolsets.json"] = f.read()

    out_dir = output_custom or os.path.join(REPO_ROOT, "output")
    if os.path.isdir(out_dir) or not out_dir.endswith(".zip"):
        zip_filename = f"ADos-{device}-android{release}-{rootfs}-{pkg_type}.zip"
        target_zip = os.path.join(out_dir, zip_filename)
    else:
        target_zip = out_dir

    generator = PackageGenerator(output_path=target_zip)
    manifest_data = {
        "name": "ADos-NetHunter",
        "version": "1.0.0",
        "device": device,
        "release": release,
        "arch": profile.get("arch", "arm64"),
        "type": pkg_type,
        "rootfs": rootfs_info,
        "tools_profile": tools_profile,
        "is_samsung": is_samsung,
        "debloated": debloat_samsung or is_samsung
    }

    pkg_path, checksum = generator.create_package(manifest_data, staging_files=staging)
    return {
        "status": "success",
        "dry_run": False,
        "device": device,
        "release": release,
        "package_path": pkg_path,
        "sha256": checksum
    }


# ---------------------------------------------------------------------------
# Endpoint Handlers
# ---------------------------------------------------------------------------

def handle_health(handler: BaseHTTPRequestHandler) -> None:
    _send_json(handler, 200, {
        "status": "ok",
        "service": "ADos-API",
        "version": VERSION,
        "uptime": round(time.time() - START_TIME, 2),
    })


def handle_status(handler: BaseHTTPRequestHandler) -> None:
    engine = ADosBuilderEngine(repo_root=REPO_ROOT)
    devices = engine.list_devices()
    _send_json(handler, 200, {
        "status": "running",
        "service": "ADos-API",
        "version": VERSION,
        "uptime": round(time.time() - START_TIME, 2),
        "tools": SUPPORTED_TOOLS,
        "devices_count": len(devices),
    })


def handle_devices(handler: BaseHTTPRequestHandler) -> None:
    engine = ADosBuilderEngine(repo_root=REPO_ROOT)
    devices = engine.list_devices()
    _send_json(handler, 200, {"devices": devices})


def handle_device_model(handler: BaseHTTPRequestHandler, model: str) -> None:
    engine = ADosBuilderEngine(repo_root=REPO_ROOT)
    try:
        profile = engine.get_device_profile(model)
        _send_json(handler, 200, profile)
    except DeviceNotFoundError as e:
        _send_error(handler, 404, str(e))


def handle_toolsets(handler: BaseHTTPRequestHandler) -> None:
    path = os.path.join(REPO_ROOT, "config", "toolsets.json")
    if not os.path.exists(path):
        _send_error(handler, 404, "toolsets.json not found")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _send_json(handler, 200, data)


def handle_firmware(handler: BaseHTTPRequestHandler) -> None:
    path = os.path.join(REPO_ROOT, "tools", "firmware", "firmware_manifest.json")
    if not os.path.exists(path):
        _send_error(handler, 404, "firmware_manifest.json not found")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _send_json(handler, 200, data)


def handle_builder_execute(handler: BaseHTTPRequestHandler) -> None:
    try:
        body = _read_body(handler)
    except (json.JSONDecodeError, ValueError) as exc:
        _send_error(handler, 400, f"Invalid JSON body: {exc}")
        return

    try:
        res = execute_build(body)
        _send_json(handler, 200, res)
    except (ValueError, DeviceNotFoundError, UnsupportedReleaseError) as exc:
        _send_error(handler, 400, str(exc))
    except Exception as exc:
        _send_error(handler, 500, f"Build execution failed: {exc}")


def handle_duckhunter_compile(handler: BaseHTTPRequestHandler) -> None:
    try:
        body = _read_body(handler)
    except (json.JSONDecodeError, ValueError) as exc:
        _send_error(handler, 400, f"Invalid JSON body: {exc}")
        return

    script = body.get("script", "")
    if not script:
        _send_error(handler, 400, "Missing 'script' field in request body")
        return

    hid_dev = body.get("hid_dev", "/dev/hidg0")
    try:
        compiler = DuckHunterCompiler(hid_dev=hid_dev)
        commands = compiler.compile(script)
        shell_script = compiler.to_executable_script(script)
        _send_json(handler, 200, {
            "status": "compiled",
            "commands_count": len(commands),
            "commands": commands,
            "shell_script": shell_script,
        })
    except Exception as exc:
        _send_error(handler, 500, f"Compilation failed: {exc}")


def handle_run_tool(handler: BaseHTTPRequestHandler, tool_from_path: str = None) -> None:
    """Start a tool subprocess or execute internal tool, returning PID / job_id."""
    try:
        body = _read_body(handler)
    except (json.JSONDecodeError, ValueError) as exc:
        _send_error(handler, 400, f"Invalid JSON body: {exc}")
        return

    tool = body.get("tool", "").strip() or (tool_from_path or "").strip()
    args_str = body.get("args", "").strip()

    if not tool:
        _send_error(handler, 400, "Missing 'tool' field")
        return

    # Check internal tools
    if tool == "builder":
        try:
            res = execute_build(body)
            _send_json(handler, 200, res)
            return
        except (ValueError, DeviceNotFoundError, UnsupportedReleaseError) as exc:
            _send_error(handler, 400, str(exc))
            return
        except Exception as exc:
            _send_error(handler, 500, f"Builder execution failed: {exc}")
            return

    if tool == "duckhunter":
        script = body.get("script", "")
        if script:
            try:
                compiler = DuckHunterCompiler(hid_dev=body.get("hid_dev", "/dev/hidg0"))
                commands = compiler.compile(script)
                shell_script = compiler.to_executable_script(script)
                _send_json(handler, 200, {
                    "status": "compiled",
                    "commands_count": len(commands),
                    "commands": commands,
                    "shell_script": shell_script,
                })
                return
            except Exception as exc:
                _send_error(handler, 500, f"Duckhunter execution failed: {exc}")
                return

    if tool not in SUPPORTED_TOOLS:
        _send_error(handler, 400, f"Unsupported tool '{tool}'. Supported: {SUPPORTED_TOOLS}")
        return

    try:
        cmd_args = shlex.split(args_str, posix=(os.name != "nt"))
        if os.name == "nt":
            cmd_args = [
                a[1:-1] if (len(a) >= 2 and ((a[0] == '"' and a[-1] == '"') or (a[0] == "'" and a[-1] == "'"))) else a
                for a in cmd_args
            ]
    except Exception:
        cmd_args = args_str.split() if args_str else []
    cmd = [tool] + cmd_args
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        _send_error(handler, 500, f"Tool '{tool}' not found on PATH")
        return
    except OSError as exc:
        _send_error(handler, 500, f"Failed to start '{tool}': {exc}")
        return

    pid = proc.pid
    entry = {
        "proc": proc,
        "tool": tool,
        "args": args_str,
        "output": io.StringIO(),
        "lock": threading.Lock(),
        "started": time.time(),
        "returncode": None,
    }
    with _processes_lock:
        _processes[pid] = entry

    t = threading.Thread(target=_reader_thread, args=(pid,), daemon=True)
    t.start()

    _send_json(handler, 200, {
        "pid": pid,
        "job_id": pid,
        "tool": tool,
        "args": args_str,
        "status": "started"
    })


def handle_stop_tool(handler: BaseHTTPRequestHandler) -> None:
    """Terminate a running process by PID."""
    try:
        body = _read_body(handler)
    except (json.JSONDecodeError, ValueError) as exc:
        _send_error(handler, 400, f"Invalid JSON body: {exc}")
        return

    pid = body.get("pid")
    if pid is None:
        _send_error(handler, 400, "Missing 'pid' field")
        return

    try:
        pid = int(pid)
    except (TypeError, ValueError):
        _send_error(handler, 400, "'pid' must be an integer")
        return

    with _processes_lock:
        entry = _processes.get(pid)

    if entry is None:
        _send_error(handler, 404, f"No process with PID {pid}")
        return

    proc: subprocess.Popen = entry["proc"]
    try:
        proc.terminate()
        time.sleep(0.3)
        if proc.poll() is None:
            proc.kill()
        _send_json(handler, 200, {"pid": pid, "job_id": pid, "status": "stopped"})
    except OSError as exc:
        _send_error(handler, 500, f"Failed to stop process {pid}: {exc}")


def handle_tool_output(handler: BaseHTTPRequestHandler, pid_str: str) -> None:
    """Return buffered stdout/stderr for a process by PID or job_id."""
    try:
        pid = int(pid_str)
    except (TypeError, ValueError):
        _send_error(handler, 400, "PID/job_id must be an integer")
        return

    with _processes_lock:
        entry = _processes.get(pid)

    if entry is None:
        _send_error(handler, 404, f"No process with PID {pid}")
        return

    with entry["lock"]:
        output = entry["output"].getvalue()

    returncode = entry["returncode"]

    _send_json(handler, 200, {
        "pid": pid,
        "job_id": pid,
        "tool": entry["tool"],
        "args": entry["args"],
        "output": output,
        "returncode": returncode,
        "running": returncode is None,
    })


def handle_ram_stats(handler: BaseHTTPRequestHandler) -> None:
    """Return system RAM statistics across Linux or Windows."""
    stats: dict = {}

    # Linux /proc/meminfo
    meminfo_path = "/proc/meminfo"
    if os.path.exists(meminfo_path):
        try:
            with open(meminfo_path, "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(":")
                        val = int(parts[1])
                        stats[key] = val
        except (OSError, ValueError):
            pass

    # Fallback: Linux free command
    if not stats:
        try:
            result = subprocess.run(
                ["free", "-k"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = result.stdout.strip().splitlines()
            if len(lines) >= 2:
                labels = ["total", "used", "free", "shared", "buff_cache", "available"]
                values = lines[1].split()
                for i, label in enumerate(labels):
                    idx = i + 1
                    if idx < len(values):
                        try:
                            stats[label] = int(values[idx])
                        except ValueError:
                            pass
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    # Windows fallback via wmic
    if not stats:
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/value"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    if v.strip().isdigit():
                        stats[k.strip()] = int(v.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    if not stats:
        stats["note"] = "RAM info unavailable on this platform"

    _send_json(handler, 200, stats)


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class ADosAPIHandler(BaseHTTPRequestHandler):
    """Route HTTP requests to appropriate handlers."""

    def log_message(self, fmt, *args):
        # Suppress noisy logging
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path in ("/api/health", "/health"):
            handle_health(self)
        elif path in ("/api/status", "/status"):
            handle_status(self)
        elif path in ("/api/devices", "/devices"):
            handle_devices(self)
        elif path.startswith("/api/devices/"):
            model = path[len("/api/devices/"):]
            handle_device_model(self, model)
        elif path in ("/api/toolsets", "/toolsets"):
            handle_toolsets(self)
        elif path in ("/api/firmware", "/firmware"):
            handle_firmware(self)
        elif path in ("/api/ram-stats", "/ram-stats"):
            handle_ram_stats(self)
        elif re.match(r"^/(api/logs|tool-output)/(\d+)$", path):
            m = re.match(r"^/(api/logs|tool-output)/(\d+)$", path)
            handle_tool_output(self, m.group(2))
        else:
            _send_error(self, 404, f"Unknown endpoint: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path in ("/api/tools/builder/execute", "/build"):
            handle_builder_execute(self)
        elif path in ("/api/tools/duckhunter/compile", "/duckhunter/compile"):
            handle_duckhunter_compile(self)
        elif path in ("/run-tool",):
            handle_run_tool(self)
        elif path in ("/stop-tool",):
            handle_stop_tool(self)
        else:
            m_exec = re.match(r"^/api/tools/([a-zA-Z0-9_\-]+)/execute$", path)
            if m_exec:
                handle_run_tool(self, tool_from_path=m_exec.group(1))
                return
            m_stop = re.match(r"^/api/tools/([a-zA-Z0-9_\-]+)/stop$", path)
            if m_stop:
                handle_stop_tool(self)
                return
            _send_error(self, 404, f"Unknown endpoint: {path}")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ---------------------------------------------------------------------------
# Server Startup
# ---------------------------------------------------------------------------

def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    server = ThreadingHTTPServer((host, port), ADosAPIHandler)
    print(f"[*] ADos API server listening on http://{host}:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...", file=sys.stderr)
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ADos Core Backend API Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Bind host (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Bind port (default: {DEFAULT_PORT})")
    args = parser.parse_args()
    run_server(args.host, args.port)
