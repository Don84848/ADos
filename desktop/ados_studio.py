#!/usr/bin/env python3
"""
ADos Studio — Full-Stack Security Platform Desktop Application
===============================================================
Desktop PC software interface connecting to ADos and ADos-Manager backends
and executing security tools locally or via backend HTTP APIs.
Pure Python standard library GUI using tkinter and tkinter.ttk (zero third-party packages).
Supports Windows/Linux/macOS with dark cybersecurity theme.
"""

import ast
from datetime import datetime
import io
import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
try:
    from tools.tool_installer import ensure_tools_bin_in_path, is_tool_installed, ensure_tool_ready, install_tool, TOOL_SPECS
    ensure_tools_bin_in_path()
except Exception:
    pass
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Path Resolution & Constants
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if os.path.isfile(os.path.join(REPO_ROOT, "core", "builder_engine.py")):
    ADOS_ROOT = REPO_ROOT
else:
    ADOS_ROOT = os.environ.get("ADOS_PATH") or os.path.abspath(os.path.join(REPO_ROOT, "..", "ADos"))

VERSION = "1.0.0"
ADOS_API_URL = os.environ.get("ADOS_API_URL", "http://127.0.0.1:8000")
MANAGER_API_URL = os.environ.get("MANAGER_API_URL", "http://127.0.0.1:8765")
BACKEND_URL = MANAGER_API_URL  # Backward compatibility alias

# Theme color palette
DARK_BG = "#1a1a2e"
PANEL_BG = "#16213e"
ACCENT = "#0f3460"
GREEN = "#00ff41"
RED = "#ff4444"
YELLOW = "#ffaa00"
WHITE = "#e0e0e0"

FONT_MONO = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 14, "bold")

# ---------------------------------------------------------------------------
# Hardware Devices Discovery
# ---------------------------------------------------------------------------

STANDARD_DEVICES = [
    "generic_arm64",
    "generic_armhf",
    "samsung_s9",
    "samsung_s10",
    "samsung_s20",
    "samsung_note9",
    "samsung_note10",
    "samsung_a50",
    "samsung_a52",
]


def load_device_choices() -> list[str]:
    """Load device names from config/devices.json or fallback to standard profiles."""
    candidate_paths = [
        os.path.join(ADOS_ROOT, "config", "devices.json"),
        os.path.join(REPO_ROOT, "config", "devices.json"),
    ]
    for p in candidate_paths:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    devices = list(data.get("devices", {}).keys())
                    if devices:
                        return devices
            except Exception:
                pass
    return list(STANDARD_DEVICES)


# ---------------------------------------------------------------------------
# Tool Catalog (ast.literal_eval compliant)
# ---------------------------------------------------------------------------

TOOLS = {
    "ADos Core & Mobile": {
        "ADos Mobile Builder": {
            "desc": "ADos NetHunter mobile OS packaging and builder engine",
            "args": "--device {device} --release {release} --rootfs {rootfs} --type {type} --tools {tools} {dry_run} {debloat}",
            "needs": ["device", "release", "rootfs", "type", "tools", "dry_run", "debloat"],
            "target_api": "ados",
            "api_endpoint": "/api/tools/builder/execute",
            "params": [
                {
                    "name": "device",
                    "label": "Device Model",
                    "type": "combobox",
                    "options": [
                        "generic_arm64",
                        "generic_armhf",
                        "samsung_s9",
                        "samsung_s10",
                        "samsung_s20",
                        "samsung_note9",
                        "samsung_note10",
                        "samsung_a50",
                        "samsung_a52",
                    ],
                    "default": "generic_arm64",
                    "flag": "--device",
                },
                {
                    "name": "release",
                    "label": "Android Release",
                    "type": "combobox",
                    "options": ["11", "10", "9", "12", "13", "14", "8", "7"],
                    "default": "11",
                    "flag": "--release",
                },
                {
                    "name": "rootfs",
                    "label": "Rootfs Mode",
                    "type": "combobox",
                    "options": ["minimal", "nano", "full"],
                    "default": "minimal",
                    "flag": "--rootfs",
                },
                {
                    "name": "type",
                    "label": "Package Type",
                    "type": "combobox",
                    "options": ["twrp", "magisk"],
                    "default": "twrp",
                    "flag": "--type",
                },
                {
                    "name": "tools",
                    "label": "Tools Profile",
                    "type": "combobox",
                    "options": ["all", "core", "wireless", "minimal", "forensics"],
                    "default": "all",
                    "flag": "--tools",
                },
                {
                    "name": "dry_run",
                    "label": "Dry Run (Validation Only)",
                    "type": "bool",
                    "default": True,
                    "flag": "--dry-run",
                },
                {
                    "name": "debloat",
                    "label": "Debloat Samsung Apps",
                    "type": "bool",
                    "default": False,
                    "flag": "--debloat-samsung",
                },
            ],
        },
        "DuckHunter BadUSB Compiler": {
            "desc": "Converts DuckyScript payloads into BadUSB HID commands",
            "args": "{payload} --output {output} --hid-dev {hid_dev}",
            "needs": ["payload", "output", "hid_dev"],
            "target_api": "ados",
            "api_endpoint": "/api/tools/duckhunter/compile",
            "params": [
                {
                    "name": "payload",
                    "label": "DuckyScript Payload File",
                    "type": "file",
                    "mode": "open",
                    "filetypes": [("DuckyScript", "*.txt *.ducky"), ("All Files", "*.*")],
                    "default": "",
                    "flag": "",
                },
                {
                    "name": "output",
                    "label": "Output Shell Script",
                    "type": "file",
                    "mode": "save",
                    "default": "output/badusb_payload.sh",
                    "flag": "--output",
                },
                {
                    "name": "hid_dev",
                    "label": "HID Device Node",
                    "type": "text",
                    "default": "/dev/hidg0",
                    "flag": "--hid-dev",
                },
            ],
        },
        "Samsung Debloater": {
            "desc": "Removes or restores Samsung OneUI telemetry and carrier bloatware",
            "args": "{action}",
            "needs": ["action"],
            "target_api": "ados",
            "params": [
                {
                    "name": "action",
                    "label": "Debloater Action",
                    "type": "combobox",
                    "options": ["--uninstall", "--restore"],
                    "default": "--uninstall",
                    "flag": "",
                },
            ],
        },
        "ADosManager APK Packager": {
            "desc": "Packages Android source tree into standalone ADosManager.apk",
            "args": "--output {output}",
            "needs": ["output"],
            "target_api": "manager",
            "api_endpoint": "/build-apk",
            "params": [
                {
                    "name": "output",
                    "label": "Target APK Path",
                    "type": "file",
                    "mode": "save",
                    "default": "output/ADosManager.apk",
                    "flag": "--output",
                },
            ],
        },
        "Wireless & Bluetooth Toolkit": {
            "desc": "Wireless monitor mode and Bluetooth reconnaissance toolkit",
            "args": "{action} {interface}",
            "needs": ["action", "interface"],
            "target_api": "ados",
            "params": [
                {
                    "name": "action",
                    "label": "Action",
                    "type": "combobox",
                    "options": ["scan", "monitor-mode", "managed-mode", "bt-scan", "bt-info"],
                    "default": "scan",
                    "flag": "",
                },
                {
                    "name": "interface",
                    "label": "Interface",
                    "type": "text",
                    "default": "wlan0",
                    "flag": "",
                },
            ],
        },
    },
    "Network": {
        "nmap": {
            "desc": "Network scanner and vulnerability discovery",
            "args": "-sV -sC {target}",
            "needs": ["target"],
            "params": [
                {"name": "target", "label": "Target Host/Subnet", "type": "text", "default": "127.0.0.1", "flag": ""},
            ],
        },
        "masscan": {
            "desc": "Mass IP port scanner",
            "args": "--rate=1000 -p1-65535 {target}",
            "needs": ["target"],
            "params": [
                {"name": "target", "label": "Target Host/CIDR", "type": "text", "default": "127.0.0.1", "flag": ""},
            ],
        },
        "netcat": {
            "desc": "TCP/UDP utility and port listener",
            "args": "-v {target} {port}",
            "needs": ["target", "port"],
            "params": [
                {"name": "target", "label": "Target IP/Host", "type": "text", "default": "127.0.0.1", "flag": ""},
                {"name": "port", "label": "Port", "type": "text", "default": "80", "flag": ""},
            ],
        },
        "ping": {
            "desc": "ICMP network ping",
            "args": "-c 4 {target}",
            "needs": ["target"],
            "params": [
                {"name": "target", "label": "Target Host/IP", "type": "text", "default": "127.0.0.1", "flag": ""},
            ],
        },
    },
    "Wi-Fi": {
        "aircrack-ng": {
            "desc": "WPA/WEP key cracker",
            "args": "-w {wordlist} {capture}",
            "needs": ["wordlist", "capture"],
            "params": [
                {"name": "wordlist", "label": "Wordlist File", "type": "file", "mode": "open", "default": "", "flag": "-w"},
                {"name": "capture", "label": "Packet Capture File (.cap/.pcap)", "type": "file", "mode": "open", "default": "", "flag": ""},
            ],
        },
        "airodump-ng": {
            "desc": "Wireless packet capture and station scanner",
            "args": "{interface}",
            "needs": ["interface"],
            "params": [
                {"name": "interface", "label": "Wireless Interface", "type": "text", "default": "wlan0mon", "flag": ""},
            ],
        },
        "aireplay-ng": {
            "desc": "Packet injection and deauthentication",
            "args": "--deauth 10 -a {bssid} {interface}",
            "needs": ["bssid", "interface"],
            "params": [
                {"name": "bssid", "label": "Access Point BSSID", "type": "text", "default": "", "flag": "-a"},
                {"name": "interface", "label": "Wireless Interface", "type": "text", "default": "wlan0mon", "flag": ""},
            ],
        },
        "bettercap": {
            "desc": "Network attack and monitoring framework",
            "args": "-iface {interface}",
            "needs": ["interface"],
            "params": [
                {"name": "interface", "label": "Network Interface", "type": "text", "default": "wlan0", "flag": "-iface"},
            ],
        },
    },
    "Web": {
        "sqlmap": {
            "desc": "Automated SQL injection and database takeover",
            "args": "-u {url} --batch --dbs",
            "needs": ["url"],
            "params": [
                {"name": "url", "label": "Target URL", "type": "text", "default": "http://example.com/item?id=1", "flag": "-u"},
            ],
        },
        "gobuster": {
            "desc": "Directory and DNS brute-forcing",
            "args": "dir -u {url} -w {wordlist}",
            "needs": ["url", "wordlist"],
            "params": [
                {"name": "url", "label": "Target URL", "type": "text", "default": "http://127.0.0.1", "flag": "-u"},
                {"name": "wordlist", "label": "Wordlist File", "type": "file", "mode": "open", "default": "", "flag": "-w"},
            ],
        },
        "nikto": {
            "desc": "Web server vulnerability scanner",
            "args": "-h {url}",
            "needs": ["url"],
            "params": [
                {"name": "url", "label": "Target Host / URL", "type": "text", "default": "http://127.0.0.1", "flag": "-h"},
            ],
        },
        "wfuzz": {
            "desc": "Web application fuzzer",
            "args": "-w {wordlist} {url}/FUZZ",
            "needs": ["url", "wordlist"],
            "params": [
                {"name": "url", "label": "Target URL (with /FUZZ)", "type": "text", "default": "http://127.0.0.1", "flag": ""},
                {"name": "wordlist", "label": "Fuzz Wordlist", "type": "file", "mode": "open", "default": "", "flag": "-w"},
            ],
        },
        "curl": {
            "desc": "Command-line HTTP client",
            "args": "-v {url}",
            "needs": ["url"],
            "params": [
                {"name": "url", "label": "URL to request", "type": "text", "default": "http://127.0.0.1:8765/status", "flag": ""},
            ],
        },
    },
    "Exploitation": {
        "msfconsole": {
            "desc": "Metasploit Framework Console",
            "args": "",
            "needs": [],
            "params": [],
        },
        "hydra": {
            "desc": "Fast network login password cracker",
            "args": "-l {username} -P {wordlist} {target} {service}",
            "needs": ["target", "username", "wordlist", "service"],
            "params": [
                {"name": "target", "label": "Target Host", "type": "text", "default": "127.0.0.1", "flag": ""},
                {"name": "username", "label": "Target Username", "type": "text", "default": "admin", "flag": "-l"},
                {"name": "wordlist", "label": "Password Wordlist", "type": "file", "mode": "open", "default": "", "flag": "-P"},
                {"name": "service", "label": "Protocol/Service", "type": "combobox", "options": ["ssh", "ftp", "http-get", "telnet", "rdp"], "default": "ssh", "flag": ""},
            ],
        },
        "john": {
            "desc": "John the Ripper password hash cracker",
            "args": "{hashfile}",
            "needs": ["hashfile"],
            "params": [
                {"name": "hashfile", "label": "Password Hash File", "type": "file", "mode": "open", "default": "", "flag": ""},
            ],
        },
        "hashcat": {
            "desc": "GPU-accelerated hash cracker",
            "args": "-m 0 {hashfile} {wordlist}",
            "needs": ["hashfile", "wordlist"],
            "params": [
                {"name": "hashfile", "label": "Hash File", "type": "file", "mode": "open", "default": "", "flag": ""},
                {"name": "wordlist", "label": "Wordlist File", "type": "file", "mode": "open", "default": "", "flag": ""},
            ],
        },
    },
    "Phone": {
        "adb devices": {
            "desc": "List attached Android devices",
            "args": "",
            "needs": [],
            "params": [],
        },
        "adb shell": {
            "desc": "Execute remote shell command on Android",
            "args": "shell {cmd}",
            "needs": ["cmd"],
            "params": [
                {"name": "cmd", "label": "Shell Command", "type": "text", "default": "getprop ro.product.model", "flag": ""},
            ],
        },
        "adb push": {
            "desc": "Copy file from PC to Android device",
            "args": "push {local} /sdcard/{remote}",
            "needs": ["local", "remote"],
            "params": [
                {"name": "local", "label": "Local File", "type": "file", "mode": "open", "default": "", "flag": ""},
                {"name": "remote", "label": "Remote Path (/sdcard/...)", "type": "text", "default": "download/", "flag": ""},
            ],
        },
        "adb pull": {
            "desc": "Copy file from Android device to PC",
            "args": "pull /sdcard/{remote} {local}",
            "needs": ["remote", "local"],
            "params": [
                {"name": "remote", "label": "Remote Path (/sdcard/...)", "type": "text", "default": "download/file.txt", "flag": ""},
                {"name": "local", "label": "Destination Local Path", "type": "file", "mode": "save", "default": "pulled_file.txt", "flag": ""},
            ],
        },
        "adb install": {
            "desc": "Install Android APK onto connected phone",
            "args": "install {apk}",
            "needs": ["apk"],
            "params": [
                {"name": "apk", "label": "Android APK File", "type": "file", "mode": "open", "filetypes": [("Android APK", "*.apk"), ("All Files", "*.*")], "default": "", "flag": ""},
            ],
        },
    },
    "Bug Bounty & Web Recon": {
        "subfinder": {
            "desc": "Passive Certificate Transparency & DNS subdomain reconnaissance",
            "args": "-d {domain}",
            "needs": ["domain"],
            "params": [
                {"name": "domain", "label": "Target Domain", "type": "text", "default": "example.com", "flag": "-d"},
            ],
        },
        "header-audit": {
            "desc": "HTTP security headers analyzer (CSP, HSTS, X-Frame-Options, CORS)",
            "args": "-u {url}",
            "needs": ["url"],
            "params": [
                {"name": "url", "label": "Target URL", "type": "text", "default": "https://example.com", "flag": "-u"},
            ],
        },
        "cors-scan": {
            "desc": "CORS origin reflection and credential misconfiguration auditor",
            "args": "-u {url}",
            "needs": ["url"],
            "params": [
                {"name": "url", "label": "Target URL", "type": "text", "default": "https://example.com", "flag": "-u"},
            ],
        },
        "cert-inspect": {
            "desc": "SSL/TLS certificate metadata inspector & SAN subdomain harvester",
            "args": "-d {host} -p {port}",
            "needs": ["host", "port"],
            "params": [
                {"name": "host", "label": "Host Domain", "type": "text", "default": "example.com", "flag": "-d"},
                {"name": "port", "label": "Port", "type": "text", "default": "443", "flag": "-p"},
            ],
        },
        "secret-scan": {
            "desc": "Client-side JS & file sensitive secret/token detector",
            "args": "-u {target}",
            "needs": ["target"],
            "params": [
                {"name": "target", "label": "Target URL or Local File", "type": "text", "default": "https://example.com", "flag": "-u"},
            ],
        },
        "tech-detect": {
            "desc": "Web technology stack, CMS, and framework fingerprinter",
            "args": "-u {url}",
            "needs": ["url"],
            "params": [
                {"name": "url", "label": "Target URL", "type": "text", "default": "https://example.com", "flag": "-u"},
            ],
        },
    },
}

# ---------------------------------------------------------------------------
# Pre-Flight Binary Existence Verifier
# ---------------------------------------------------------------------------

def check_binary_available(binary_name: str) -> tuple[bool, str]:
    """
    Check if a command or binary is available in the local PATH or environment.
    Returns (is_available, resolved_path_or_message).
    """
    if not binary_name:
        return False, "No binary specified"

    clean_bin = binary_name.strip()
    # Normalize common multi-word commands (e.g. 'adb devices' -> 'adb')
    first_token = clean_bin.split()[0] if clean_bin else ""

    # Python aliases
    if first_token in ("python", "python3"):
        return True, sys.executable

    # Absolute or relative file paths
    if os.path.isfile(first_token):
        return True, os.path.abspath(first_token)

    # Use shutil.which to inspect system PATH
    resolved = shutil.which(first_token)
    if resolved:
        return True, resolved

    # On Windows, try common binary extensions
    if sys.platform.startswith("win"):
        for ext in (".exe", ".cmd", ".bat"):
            if not first_token.lower().endswith(ext):
                resolved = shutil.which(first_token + ext)
                if resolved:
                    return True, resolved

    return False, f"Binary '{first_token}' not found on system PATH"


# ---------------------------------------------------------------------------
# Main Application Class
# ---------------------------------------------------------------------------

class ADosStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"ADos Studio v{VERSION} — Security Platform")
        self.geometry("1280x820")
        self.minsize(920, 620)
        self.configure(bg=DARK_BG)

        # Process and connection state
        self.running_procs = {}
        self.current_proc = None
        self.current_backend_pid = None
        self.current_backend_url = None
        self.ados_api_online = False
        self.manager_api_online = False
        self.backend_online = False

        # Selection state
        self.current_tool = None
        self.arg_entries = {}
        self.arg_widgets = {}

        self._build_ui()
        self.after(300, self._check_backend)
        self.after(1500, self._refresh_devices)

    # -----------------------------------------------------------------------
    # UI Construction
    # -----------------------------------------------------------------------

    def _build_ui(self):
        # Header bar
        hdr = tk.Frame(self, bg=ACCENT, height=52)
        hdr.pack(fill=tk.X, side=tk.TOP)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⚡ ADos Studio", font=FONT_TITLE, bg=ACCENT, fg=GREEN).pack(side=tk.LEFT, padx=16)

        # Right-aligned status indicators and controls
        tk.Button(
            hdr, text="⟳ Refresh Status", command=self._check_backend,
            bg=PANEL_BG, fg=WHITE, bd=0, font=FONT_LABEL, padx=8, pady=2
        ).pack(side=tk.RIGHT, padx=12)

        self.manager_status_lbl = tk.Label(
            hdr, text="● Manager (8765): Checking...", font=FONT_LABEL, bg=ACCENT, fg=YELLOW
        )
        self.manager_status_lbl.pack(side=tk.RIGHT, padx=10)

        self.ados_status_lbl = tk.Label(
            hdr, text="● ADos API (8000): Checking...", font=FONT_LABEL, bg=ACCENT, fg=YELLOW
        )
        self.ados_status_lbl.pack(side=tk.RIGHT, padx=10)

        # Backward compatibility label
        self.status_lbl = tk.Label(
            hdr, text="● Backend: Checking...", font=FONT_LABEL, bg=ACCENT, fg=YELLOW
        )
        # Hidden by default in favor of dual badges, but kept for test inspection

        # Main Paned window
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=DARK_BG, sashwidth=4)
        pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Left panel — tool catalog and devices
        left = tk.Frame(pane, bg=PANEL_BG, width=300)
        pane.add(left, minsize=220)

        tk.Label(
            left, text="TOOL CATALOG", font=("Segoe UI", 9, "bold"),
            bg=PANEL_BG, fg=YELLOW
        ).pack(anchor=tk.W, padx=8, pady=(6, 2))

        # Styled treeview for tools
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=PANEL_BG, foreground=WHITE, fieldbackground=PANEL_BG, font=FONT_LABEL)
        style.configure("Treeview.Heading", background=ACCENT, foreground=WHITE)
        style.map("Treeview", background=[('selected', ACCENT)])

        self.tool_tree = ttk.Treeview(left, selectmode='browse', show='tree headings')
        self.tool_tree.heading('#0', text='Category / Tool')
        self.tool_tree.column('#0', width=260)

        for cat, tools_in_cat in TOOLS.items():
            icon = "⚡" if "ADos" in cat else ("🎯" if "Bug Bounty" in cat else "📂")
            cat_id = self.tool_tree.insert('', 'end', text=f'{icon} {cat}', open=True)
            for tool_name in tools_in_cat:
                self.tool_tree.insert(cat_id, 'end', text=f'  🔧 {tool_name}', values=(cat, tool_name))

        self.tool_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        tk.Button(
            left, text="📥 Install / Verify All Tools", command=self._install_all_tools,
            bg=ACCENT, fg=WHITE, bd=0, font=("Segoe UI", 9)
        ).pack(fill=tk.X, padx=4, pady=(2, 6))
        self.tool_tree.bind('<<TreeviewSelect>>', self._on_tool_select)

        # Connected Devices listbox
        tk.Label(
            left, text="CONNECTED DEVICES (ADB)", font=("Segoe UI", 9, "bold"),
            bg=PANEL_BG, fg=YELLOW
        ).pack(anchor=tk.W, padx=8, pady=(8, 2))

        self.devices_lb = tk.Listbox(left, bg=DARK_BG, fg=GREEN, font=FONT_MONO, height=5, bd=0)
        self.devices_lb.pack(fill=tk.X, padx=4, pady=2)

        tk.Button(
            left, text="⟳ Refresh Devices", command=self._refresh_devices,
            bg=ACCENT, fg=WHITE, bd=0, font=("Segoe UI", 9)
        ).pack(padx=4, pady=3, fill=tk.X)

        # Right panel — tabbed interface
        right = tk.Frame(pane, bg=DARK_BG)
        pane.add(right, minsize=620)

        self.notebook = ttk.Notebook(right)
        style.configure("TNotebook", background=DARK_BG)
        style.configure("TNotebook.Tab", background=ACCENT, foreground=WHITE, font=FONT_LABEL, padding=[10, 4])
        style.map("TNotebook.Tab", background=[('selected', GREEN), ('active', PANEL_BG)], foreground=[('selected', DARK_BG)])
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Run Tool
        self.run_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.run_tab, text='▶ Run Tool')
        self._build_run_tab()

        # Tab 2: Terminal
        self.term_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.term_tab, text='⬛ Terminal')
        self._build_term_tab()

        # Tab 3: Phone Manager
        self.phone_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.phone_tab, text='📱 Phone')
        self._build_phone_tab()

        # Tab 4: APK Builder
        self.apk_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.apk_tab, text='📦 Build APK')
        self._build_apk_tab()

        # Tab 5: About
        self.about_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.about_tab, text='ℹ About')
        self._build_about_tab()

    def _build_run_tab(self):
        f = self.run_tab

        # Dual-Mode Execution Selector Frame
        mode_box = tk.LabelFrame(f, text="Execution Engine Mode", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL)
        mode_box.grid(row=0, column=0, columnspan=3, sticky=tk.EW, padx=8, pady=(6, 4))

        self.exec_mode = tk.StringVar(value="local")

        tk.Radiobutton(
            mode_box, text="Local Subprocess (run locally on PC via subprocess)",
            variable=self.exec_mode, value="local",
            bg=DARK_BG, fg=WHITE, selectcolor=ACCENT, activebackground=DARK_BG,
            activeforeground=GREEN, font=FONT_LABEL
        ).pack(side=tk.LEFT, padx=12, pady=4)

        tk.Radiobutton(
            mode_box, text="Backend API (dispatch remotely to HTTP API server)",
            variable=self.exec_mode, value="api",
            bg=DARK_BG, fg=WHITE, selectcolor=ACCENT, activebackground=DARK_BG,
            activeforeground=GREEN, font=FONT_LABEL
        ).pack(side=tk.LEFT, padx=12, pady=4)

        tk.Label(mode_box, text="API Target:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).pack(side=tk.LEFT, padx=(20, 4))
        self.api_target_var = tk.StringVar(value="auto")
        self.api_target_combo = ttk.Combobox(
            mode_box, textvariable=self.api_target_var,
            values=["auto", "ADos API (8000)", "Manager API (8765)"],
            state="readonly", width=18, font=FONT_LABEL
        )
        self.api_target_combo.pack(side=tk.LEFT, padx=4)

        # Selected Tool Overview
        tk.Label(f, text="Selected Tool:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=1, column=0, sticky=tk.W, padx=8, pady=2)
        self.tool_name_lbl = tk.Label(f, text="(select a tool from the left panel)", bg=DARK_BG, fg=WHITE, font=FONT_MONO)
        self.tool_name_lbl.grid(row=1, column=1, sticky=tk.W, padx=4, pady=2)

        tk.Label(f, text="Description:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=2, column=0, sticky=tk.W, padx=8)
        self.tool_desc_lbl = tk.Label(f, text="", bg=DARK_BG, fg=WHITE, font=FONT_LABEL)
        self.tool_desc_lbl.grid(row=2, column=1, sticky=tk.W, padx=4)

        tk.Label(f, text="Tool Status:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=3, column=0, sticky=tk.W, padx=8)
        self.tool_status_lbl = tk.Label(f, text="● Not Selected", bg=DARK_BG, fg=WHITE, font=FONT_LABEL)
        self.tool_status_lbl.grid(row=3, column=1, sticky=tk.W, padx=4)

        # Dynamic arguments container
        self.args_frame = tk.LabelFrame(f, text="Tool Arguments & Parameters", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL)
        self.args_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, padx=8, pady=6)

        # Extra args
        tk.Label(f, text="Extra args:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=5, column=0, sticky=tk.W, padx=8)
        self.extra_args_entry = tk.Entry(f, bg=PANEL_BG, fg=WHITE, font=FONT_MONO)
        self.extra_args_entry.grid(row=5, column=1, sticky=tk.EW, padx=4, pady=2)
        f.columnconfigure(1, weight=1)

        # Control buttons
        btn_frame = tk.Frame(f, bg=DARK_BG)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=6, padx=8, sticky=tk.W)

        self.run_btn = tk.Button(
            btn_frame, text="▶ START / RUN", command=self._run_selected_tool,
            bg=GREEN, fg=DARK_BG, font=("Segoe UI", 11, "bold"), width=12, bd=0
        )
        self.run_btn.pack(side=tk.LEFT, padx=4)

        self.install_btn = tk.Button(
            btn_frame, text="📥 Install Tool", command=self._install_current_tool,
            bg="#ffaa00", fg=DARK_BG, font=("Segoe UI", 10, "bold"), width=14, bd=0
        )
        self.install_btn.pack(side=tk.LEFT, padx=4)

        self.stop_btn = tk.Button(
            btn_frame, text="■ STOP", command=self._stop_tool,
            bg=RED, fg=WHITE, font=("Segoe UI", 11, "bold"), width=12, bd=0
        )
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_frame, text="🗑 Clear Log", command=self._clear_log,
            bg=ACCENT, fg=WHITE, font=FONT_LABEL, bd=0, width=12
        ).pack(side=tk.LEFT, padx=4)

        self.auto_install_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            btn_frame, text="Auto-Install On-Demand", variable=self.auto_install_var,
            bg=DARK_BG, fg=WHITE, selectcolor=PANEL_BG, activebackground=DARK_BG, activeforeground=WHITE
        ).pack(side=tk.LEFT, padx=8)

        # Output console
        tk.Label(f, text="Console Output:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=7, column=0, sticky=tk.NW, padx=8, pady=(4, 2))
        self.output_txt = scrolledtext.ScrolledText(
            f, bg="#0d0d0d", fg=GREEN, font=FONT_MONO,
            insertbackground=GREEN, wrap=tk.WORD, height=14
        )
        self.output_txt.grid(row=8, column=0, columnspan=3, sticky=tk.NSEW, padx=8, pady=4)
        f.rowconfigure(8, weight=1)

    def _build_term_tab(self):
        f = self.term_tab
        cmd_frame = tk.Frame(f, bg=DARK_BG)
        cmd_frame.pack(fill=tk.X, padx=4, pady=4)

        tk.Label(cmd_frame, text="$", bg=DARK_BG, fg=GREEN, font=FONT_MONO).pack(side=tk.LEFT)
        self.term_entry = tk.Entry(cmd_frame, bg=PANEL_BG, fg=WHITE, font=FONT_MONO, insertbackground=WHITE)
        self.term_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.term_entry.bind('<Return>', self._run_terminal_cmd)

        tk.Button(
            cmd_frame, text="Run", command=self._run_terminal_cmd,
            bg=GREEN, fg=DARK_BG, font=FONT_LABEL, bd=0
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            cmd_frame, text="Clear", command=lambda: self.term_txt.delete(1.0, tk.END),
            bg=ACCENT, fg=WHITE, font=FONT_LABEL, bd=0
        ).pack(side=tk.LEFT)

        self.term_txt = scrolledtext.ScrolledText(
            f, bg="#0d0d0d", fg=GREEN, font=FONT_MONO,
            insertbackground=GREEN, wrap=tk.WORD
        )
        self.term_txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._term_append(f"ADos Studio Terminal v{VERSION}\nType command and press Enter\n{'='*50}\n")

    def _build_phone_tab(self):
        f = self.phone_tab
        actions = [
            ("🔄 List Devices", "adb devices"),
            ("📱 Device Info", "adb shell getprop ro.product.model"),
            ("🔋 Battery", "adb shell dumpsys battery"),
            ("💾 Storage", "adb shell df"),
            ("📡 WiFi Info", "adb shell dumpsys wifi"),
            ("🔑 Enable Root", "adb shell su -c id"),
            ("⚙ RAM Stats", "adb shell cat /proc/meminfo"),
            ("📋 Running Apps", "adb shell ps"),
        ]
        btn_frame = tk.LabelFrame(f, text="ADB Quick Actions", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL)
        btn_frame.pack(fill=tk.X, padx=8, pady=8)

        for i, (label, cmd) in enumerate(actions):
            tk.Button(
                btn_frame, text=label, command=lambda c=cmd: self._run_adb(c),
                bg=ACCENT, fg=WHITE, font=FONT_LABEL, bd=0, width=18
            ).grid(row=i // 4, column=i % 4, padx=4, pady=4)

        tk.Label(f, text="Custom ADB Command:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).pack(anchor=tk.W, padx=8)
        adb_frame = tk.Frame(f, bg=DARK_BG)
        adb_frame.pack(fill=tk.X, padx=8)

        self.adb_entry = tk.Entry(adb_frame, bg=PANEL_BG, fg=WHITE, font=FONT_MONO)
        self.adb_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.adb_entry.insert(0, "adb shell ")
        self.adb_entry.bind('<Return>', lambda e: self._run_adb(self.adb_entry.get()))

        tk.Button(
            adb_frame, text="Run", command=lambda: self._run_adb(self.adb_entry.get()),
            bg=GREEN, fg=DARK_BG, font=FONT_LABEL, bd=0
        ).pack(side=tk.LEFT, padx=4)

        self.phone_out = scrolledtext.ScrolledText(f, bg="#0d0d0d", fg=GREEN, font=FONT_MONO, height=20)
        self.phone_out.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def _build_apk_tab(self):
        f = self.apk_tab
        tk.Label(f, text="ADosManager.apk Packager", font=FONT_TITLE, bg=DARK_BG, fg=GREEN).pack(pady=16)

        info = tk.Label(
            f, text=(
                "Packages Android source code and assets into ADosManager.apk.\n"
                "Executable locally or via Backend API (port 8765 /build-apk).\n"
                "Produces a validated standalone APK with SHA256 checksum."
            ), bg=DARK_BG, fg=WHITE, font=FONT_LABEL, justify=tk.LEFT
        )
        info.pack(padx=16)

        tk.Button(
            f, text="📦 Build APK Now", command=self._build_apk,
            bg=GREEN, fg=DARK_BG, font=("Segoe UI", 12, "bold"), bd=0, width=20
        ).pack(pady=16)

        self.apk_out = scrolledtext.ScrolledText(f, bg="#0d0d0d", fg=GREEN, font=FONT_MONO, height=20)
        self.apk_out.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def _build_about_tab(self):
        f = self.about_tab
        about_text = f"""
        ⚡ ADos Studio v{VERSION}
        ═════════════════════════════════════════════════════════
        Full-Stack Production Cybersecurity Desktop Platform.
        Zero Third-Party Pip Dependencies (Pure Python stdlib).

        Integrated Capabilities:
        • ADos Core & Mobile: NetHunter OS Builder, BadUSB Compiler,
          Samsung OneUI Debloater, APK Packager, Wireless Toolkit
        • Network: nmap, masscan, netcat, ping
        • Wi-Fi: aircrack-ng, airodump-ng, aireplay-ng, bettercap
        • Web: sqlmap, gobuster, nikto, wfuzz, curl
        • Exploitation: msfconsole, hydra, john, hashcat
        • Phone: ADB device and chroot management

        Dual Execution Modes:
        1. Local Subprocess: Direct execution with pre-flight binary check
        2. Backend API: Dispatches to ADos (8000) or Manager (8765) APIs

        Endpoints:
        • ADos Core API:    {ADOS_API_URL}
        • ADos-Manager API: {MANAGER_API_URL}

        Repositories:
        • Public:  https://github.com/Don84848/ADos
        • Manager: https://github.com/Don84848/ADos-Manager
        """
        tk.Label(f, text=about_text, bg=DARK_BG, fg=WHITE, font=FONT_MONO, justify=tk.LEFT).pack(pady=20, padx=20, anchor=tk.W)

    # -----------------------------------------------------------------------
    # Dynamic Form Handlers
    # -----------------------------------------------------------------------

    def _on_tool_select(self, event):
        sel = self.tool_tree.selection()
        if not sel:
            return
        item = self.tool_tree.item(sel[0])
        values = item.get('values')
        if not values or len(values) < 2:
            return

        cat, tool_name = values[0], values[1]
        tool_info = TOOLS.get(cat, {}).get(tool_name, {})
        self.current_tool = (cat, tool_name, tool_info)
        self.tool_name_lbl.config(text=f"{tool_name} [{cat}]")
        self.tool_desc_lbl.config(text=tool_info.get('desc', ''))
        self._refresh_tool_status()

        # Clear existing argument inputs
        for w in self.args_frame.winfo_children():
            w.destroy()
        self.arg_entries = {}
        self.arg_widgets = {}

        params = tool_info.get('params')
        if params:
            for i, p in enumerate(params):
                pname = p.get('name')
                plabel = p.get('label', pname)
                ptype = p.get('type', 'text')
                pdefault = p.get('default', '')

                tk.Label(self.args_frame, text=f"{plabel}:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=i, column=0, sticky=tk.W, padx=6, pady=3)

                if ptype == "combobox":
                    options = p.get('options', [])
                    # If this is device dropdown, refresh dynamically if possible
                    if pname == "device" and tool_name == "ADos Mobile Builder":
                        discovered = load_device_choices()
                        if discovered:
                            options = discovered
                    var = tk.StringVar(value=str(pdefault))
                    cb = ttk.Combobox(self.args_frame, textvariable=var, values=options, state="readonly", font=FONT_LABEL)
                    cb.grid(row=i, column=1, sticky=tk.EW, padx=6, pady=3)
                    self.arg_entries[pname] = var
                    self.arg_widgets[pname] = cb

                elif ptype == "file":
                    f_frame = tk.Frame(self.args_frame, bg=DARK_BG)
                    f_frame.grid(row=i, column=1, sticky=tk.EW, padx=6, pady=3)
                    var = tk.StringVar(value=str(pdefault))
                    ent = tk.Entry(f_frame, textvariable=var, bg=PANEL_BG, fg=WHITE, font=FONT_MONO)
                    ent.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    mode = p.get('mode', 'open')
                    ftypes = p.get('filetypes', [("All Files", "*.*")])

                    def _browse(v=var, m=mode, ft=ftypes):
                        if m == 'save':
                            fn = filedialog.asksaveasfilename(filetypes=ft)
                        else:
                            fn = filedialog.askopenfilename(filetypes=ft)
                        if fn:
                            v.set(fn)

                    tk.Button(f_frame, text="Browse...", command=_browse, bg=ACCENT, fg=WHITE, font=("Segoe UI", 9), bd=0).pack(side=tk.RIGHT, padx=4)
                    self.arg_entries[pname] = var
                    self.arg_widgets[pname] = ent

                elif ptype == "bool":
                    flag = p.get('flag', '')

                    class BoolWrapper:
                        def __init__(self, bvar, flag_str):
                            self.bvar = bvar
                            self.flag_str = flag_str

                        def get(self):
                            return self.flag_str if self.bvar.get() else ""

                    bvar = tk.BooleanVar(value=bool(pdefault))
                    chk = ttk.Checkbutton(self.args_frame, text=f"Enable {flag}".strip(), variable=bvar)
                    chk.grid(row=i, column=1, sticky=tk.W, padx=6, pady=3)
                    wrapper = BoolWrapper(bvar, flag)
                    self.arg_entries[pname] = wrapper
                    self.arg_widgets[pname] = chk

                else:  # Text input
                    var = tk.StringVar(value=str(pdefault))
                    ent = tk.Entry(self.args_frame, textvariable=var, bg=PANEL_BG, fg=WHITE, font=FONT_MONO)
                    ent.grid(row=i, column=1, sticky=tk.EW, padx=6, pady=3)
                    self.arg_entries[pname] = var
                    self.arg_widgets[pname] = ent

                self.args_frame.columnconfigure(1, weight=1)
        else:
            # Fallback for tools with only 'needs'
            needs = tool_info.get('needs', [])
            for i, arg in enumerate(needs):
                tk.Label(self.args_frame, text=f"{arg}:", bg=DARK_BG, fg=YELLOW, font=FONT_LABEL).grid(row=i, column=0, sticky=tk.W, padx=6, pady=3)
                entry = tk.Entry(self.args_frame, bg=PANEL_BG, fg=WHITE, font=FONT_MONO)
                entry.grid(row=i, column=1, sticky=tk.EW, padx=6, pady=3)
                self.args_frame.columnconfigure(1, weight=1)
                self.arg_entries[arg] = entry
                self.arg_widgets[arg] = entry

    # -----------------------------------------------------------------------
    def _refresh_tool_status(self):
        """Update the status indicator for the currently selected tool."""
        if not self.current_tool or not hasattr(self, 'tool_status_lbl'):
            return
        cat, tool_name, tool_info = self.current_tool
        first_token = tool_name.split()[0]
        avail, path = check_binary_available(first_token)
        if avail:
            self.tool_status_lbl.config(text=f"● Installed: {os.path.basename(path)} (Ready)", fg=GREEN)
        else:
            self.tool_status_lbl.config(text="● Not Installed (Auto-installs when RUN)", fg=YELLOW)

    def _install_current_tool(self):
        """Explicitly install the currently selected tool on-demand."""
        if not self.current_tool:
            messagebox.showinfo("No Tool", "Please select a tool from the catalog first.")
            return
        cat, tool_name, tool_info = self.current_tool
        binary = tool_name.split()[0]
        def _task():
            self._log(f"\n[{datetime.now().strftime('%H:%M:%S')}] [*] Manual install requested for: {binary}\n")
            try:
                from tools.tool_installer import install_tool, ensure_tools_bin_in_path
                ensure_tools_bin_in_path()
                ok, p = install_tool(binary, log_cb=self._log)
                if ok:
                    self._log(f"[+] Successfully deployed and configured '{binary}' at:\n    {p}\n")
                    self.after(0, self._refresh_tool_status)
                else:
                    self._log(f"[!] Could not install '{binary}': {p}\n")
            except Exception as ex:
                self._log(f"[!] Installation error: {ex}\n")
        threading.Thread(target=_task, daemon=True).start()

    def _install_all_tools(self):
        """Batch on-demand installer for all tools in catalog."""
        def _task():
            self._log(f"\n[{datetime.now().strftime('%H:%M:%S')}] [*] Initiating automated setup for all security tools...\n")
            try:
                from tools.tool_installer import TOOL_SPECS, ensure_tool_ready, ensure_tools_bin_in_path
                ensure_tools_bin_in_path()
                for name in TOOL_SPECS:
                    self._log(f"[*] Processing tool: {name}")
                    ok, p = ensure_tool_ready(name, log_cb=self._log)
                    status_text = "READY" if ok else "FAILED"
                    self._log(f"    --> {name}: [{status_text}]\n")
                self._log("[+] All tool configurations processed!\n")
                self.after(0, self._refresh_tool_status)
            except Exception as ex:
                self._log(f"[!] Batch installation error: {ex}\n")
        threading.Thread(target=_task, daemon=True).start()

    # Dual-Mode Execution Routing
    # -----------------------------------------------------------------------

    def _run_selected_tool(self):
        if not self.current_tool:
            messagebox.showwarning("No Tool Selected", "Please select a tool from the tool catalog.")
            return

        cat, tool_name, tool_info = self.current_tool
        args_template = tool_info.get('args', '')

        # Build formatted arguments string
        try:
            param_values = {k: v.get() for k, v in self.arg_entries.items()}
            filled_args = args_template.format(**param_values)
        except KeyError as e:
            messagebox.showerror("Missing Argument", f"Required argument missing: {e}")
            return

        extra = self.extra_args_entry.get().strip()
        full_args = f"{filled_args} {extra}".strip()

        mode = self.exec_mode.get()

        if mode == "api":
            self._run_via_backend(cat, tool_name, tool_info, full_args)
        else:
            self._run_via_local_subprocess(cat, tool_name, tool_info, full_args)

    def _run_via_local_subprocess(self, cat, tool_name, tool_info, full_args):
        """Execute command locally via subprocess with pre-flight binary check."""
        base_cmd = ""
        binary_to_check = ""

        if cat == "ADos Core & Mobile":
            # Map ADos tools to local python scripts or shell scripts
            if tool_name == "ADos Mobile Builder":
                script_path = os.path.join(ADOS_ROOT, "build.py")
                if not os.path.isfile(script_path):
                    self._log(
                        f"\n[!] PRE-FLIGHT CHECK WARNING: ADos builder script not found at:\n    {script_path}\n"
                        f"[*] Suggestion: Switch Execution Mode to 'Backend API' to run remotely via ADos API.\n"
                    )
                    if self.ados_api_online:
                        self._log("[*] ADos Core API is online. Auto-routing execution to Backend API mode...\n")
                        self._run_via_backend(cat, tool_name, tool_info, full_args)
                    return
                base_cmd = f'"{sys.executable}" "{script_path}" {full_args}'
                binary_to_check = sys.executable

            elif tool_name == "DuckHunter BadUSB Compiler":
                script_path = os.path.join(ADOS_ROOT, "tools", "duckhunter", "duckhunter.py")
                if not os.path.isfile(script_path):
                    self._log(
                        f"\n[!] PRE-FLIGHT CHECK WARNING: DuckHunter script not found at:\n    {script_path}\n"
                        f"[*] Suggestion: Switch Execution Mode to 'Backend API'.\n"
                    )
                    if self.ados_api_online:
                        self._log("[*] ADos Core API is online. Auto-routing execution to Backend API mode...\n")
                        self._run_via_backend(cat, tool_name, tool_info, full_args)
                    return
                base_cmd = f'"{sys.executable}" "{script_path}" {full_args}'
                binary_to_check = sys.executable

            elif tool_name == "Samsung Debloater":
                script_path = os.path.join(ADOS_ROOT, "scripts", "debloat-samsung.sh")
                avail, _ = check_binary_available("bash")
                if not avail:
                    self._log(
                        f"\n[!] PRE-FLIGHT CHECK WARNING: 'bash' executable not found on local PATH.\n"
                        f"[*] Suggestion: Switch Execution Mode to 'Backend API' to run via phone/chroot.\n"
                    )
                    if self.ados_api_online or self.manager_api_online:
                        self._log("[*] Backend server is online. Routing to Backend API mode...\n")
                        self._run_via_backend(cat, tool_name, tool_info, full_args)
                    return
                base_cmd = f'bash "{script_path}" {full_args}'
                binary_to_check = "bash"

            elif tool_name == "ADosManager APK Packager":
                script_path = os.path.join(REPO_ROOT, "tools", "build_apk.py")
                base_cmd = f'"{sys.executable}" "{script_path}" {full_args}'
                binary_to_check = sys.executable

            elif tool_name == "Wireless & Bluetooth Toolkit":
                script_path = os.path.join(ADOS_ROOT, "tools", "wireless", "wireless_toolkit.sh")
                avail, _ = check_binary_available("bash")
                if not avail:
                    self._log(
                        f"\n[!] PRE-FLIGHT CHECK WARNING: 'bash' executable not found on local PATH.\n"
                        f"[*] Suggestion: Switch Execution Mode to 'Backend API'.\n"
                    )
                    if self.ados_api_online:
                        self._log("[*] ADos Core API is online. Routing to Backend API mode...\n")
                        self._run_via_backend(cat, tool_name, tool_info, full_args)
                    return
                base_cmd = f'bash "{script_path}" {full_args}'
                binary_to_check = "bash"
        else:
            # Standard external security tools (nmap, aircrack-ng, sqlmap, adb, etc.)
            binary_to_check = tool_name.split()[0]
            base_cmd = f"{tool_name} {full_args}".strip()

        # Run pre-flight binary check
        avail, msg = check_binary_available(binary_to_check)
        if not avail:
            # Check auto install toggle
            if hasattr(self, 'auto_install_var') and self.auto_install_var.get() and binary_to_check not in (sys.executable, "bash"):
                self._log(f"\n[*] ON-DEMAND INSTALLER: '{binary_to_check}' not detected in system PATH.\n")
                self._log(f"[*] Automatically deploying and configuring '{binary_to_check}' on-demand...\n")
                def _install_and_run():
                    try:
                        from tools.tool_installer import ensure_tool_ready, ensure_tools_bin_in_path
                        ensure_tools_bin_in_path()
                        ok, path_or_msg = ensure_tool_ready(binary_to_check, log_cb=self._log)
                        if ok:
                            self._log(f"\n[+] '{binary_to_check}' installed and ready at:\n    {path_or_msg}\n")
                            self.after(0, self._refresh_tool_status)
                            # Re-resolve and run immediately!
                            self._log(f"\n[{datetime.now().strftime('%H:%M:%S')}] [RUNNING TOOL] {base_cmd}\n{'─'*60}\n")
                            self._execute_command(base_cmd, self.output_txt)
                            return
                        else:
                            self._log(f"\n[!] Auto-installation could not complete: {path_or_msg}\n")
                    except Exception as e:
                        self._log(f"\n[!] Error during auto-install: {e}\n")
                    if self.backend_online:
                        self._log("[*] Routing execution to remote Backend API server...\n")
                        self._run_via_backend(cat, tool_name, tool_info, full_args)
                threading.Thread(target=_install_and_run, daemon=True).start()
                return

            self._log(
                f"\n[!] PRE-FLIGHT CHECK: Executable '{binary_to_check}' was not found on your local system PATH.\n"
                f"[*] Local execution cannot proceed without the required binary.\n"
                f"[*] Suggestions:\n"
                f"    1. Click '📥 Install Tool' to automatically install this tool.\n"
                f"    2. Switch Execution Engine Mode to 'Backend API' to execute remotely via ADos / NetHunter.\n"
            )
            if self.backend_online:
                self._log("[*] Notice: Backend API server is ONLINE. Auto-routing execution to Backend API mode...\n")
                self._run_via_backend(cat, tool_name, tool_info, full_args)
            return

        self._log(f"\n[{datetime.now().strftime('%H:%M:%S')}] [LOCAL SUBPROCESS] Running: {base_cmd}\n{'─'*60}\n")
        self._execute_command(base_cmd, self.output_txt)

    def _execute_command(self, cmd, output_widget):
        """Spawn local subprocess in background thread and stream output to widget."""
        def _run():
            try:
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                self.current_proc = proc
                for line in proc.stdout:
                    self._append_to(output_widget, line)
                proc.wait()
                self._append_to(output_widget, f"\n[Process exited with return code {proc.returncode}]\n")
            except Exception as ex:
                self._append_to(output_widget, f"\n[ERROR] Execution failed: {ex}\n")
            finally:
                self.current_proc = None

        threading.Thread(target=_run, daemon=True).start()

    def _run_via_backend(self, cat, tool_name, tool_info, full_args):
        """Dispatch tool execution to remote HTTP Backend API server."""
        def _execute():
            target_url = None
            target_api = tool_info.get("target_api", "auto")

            # Route by tool requirement or user target preference
            user_choice = self.api_target_var.get() if hasattr(self, 'api_target_var') else "auto"

            if "8000" in user_choice and self.ados_api_online:
                target_url = ADOS_API_URL
            elif "8765" in user_choice and self.manager_api_online:
                target_url = MANAGER_API_URL
            elif target_api == "ados" and self.ados_api_online:
                target_url = ADOS_API_URL
            elif target_api == "manager" and self.manager_api_online:
                target_url = MANAGER_API_URL
            elif self.ados_api_online and cat == "ADos Core & Mobile":
                target_url = ADOS_API_URL
            elif self.manager_api_online:
                target_url = MANAGER_API_URL
            elif self.ados_api_online:
                target_url = ADOS_API_URL

            if not target_url:
                self._log(
                    f"\n[!] BACKEND API ERROR: Neither backend server is currently online.\n"
                    f"    Checked: ADos API ({ADOS_API_URL}) and Manager API ({MANAGER_API_URL})\n"
                    f"[*] Please start the server using 'python build.py --start-backend' or switch to Local Subprocess mode.\n"
                )
                return

            self._log(f"\n[{datetime.now().strftime('%H:%M:%S')}] [BACKEND API: {target_url}] Dispatching: {tool_name}\n{'─'*60}\n")

            try:
                # Specialized endpoints for dedicated builder and compiler tools
                if tool_name == "ADos Mobile Builder" and target_url == ADOS_API_URL:
                    builder_payload = {
                        "device": self.arg_entries["device"].get() if "device" in self.arg_entries else "generic_arm64",
                        "release": self.arg_entries["release"].get() if "release" in self.arg_entries else "11",
                        "rootfs": self.arg_entries["rootfs"].get() if "rootfs" in self.arg_entries else "minimal",
                        "type": self.arg_entries["type"].get() if "type" in self.arg_entries else "twrp",
                        "tools": self.arg_entries["tools"].get() if "tools" in self.arg_entries else "all",
                        "dry_run": bool(self.arg_entries["dry_run"].get()) if "dry_run" in self.arg_entries else True,
                        "debloat_samsung": bool(self.arg_entries["debloat"].get()) if "debloat" in self.arg_entries else False,
                    }
                    req = urllib.request.Request(
                        f"{target_url}/api/tools/builder/execute",
                        data=json.dumps(builder_payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "User-Agent": "ADosStudio/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=40) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        self._log(f"[+] Builder Engine Response:\n{json.dumps(res_data, indent=2)}\n")
                    return

                if tool_name == "DuckHunter BadUSB Compiler" and target_url == ADOS_API_URL:
                    payload_file = self.arg_entries.get("payload", "").get() if "payload" in self.arg_entries else ""
                    script_content = ""
                    if payload_file and os.path.isfile(payload_file):
                        with open(payload_file, "r", encoding="utf-8") as f:
                            script_content = f.read()
                    else:
                        script_content = "REM Default BadUSB Payload\nDELAY 500\nSTRING Hello from ADos Studio\nENTER\n"

                    hid_dev = self.arg_entries["hid_dev"].get() if "hid_dev" in self.arg_entries else "/dev/hidg0"
                    duck_payload = {"script": script_content, "hid_dev": hid_dev}
                    req = urllib.request.Request(
                        f"{target_url}/api/tools/duckhunter/compile",
                        data=json.dumps(duck_payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "User-Agent": "ADosStudio/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        self._log(f"[+] DuckHunter Compiler Response:\nCommands generated: {res_data.get('commands_count')}\n")
                        out_script = self.arg_entries["output"].get() if "output" in self.arg_entries else ""
                        if out_script:
                            out_dir = os.path.dirname(out_script)
                            if out_dir:
                                os.makedirs(out_dir, exist_ok=True)
                            with open(out_script, "w", encoding="utf-8") as out_f:
                                out_f.write(res_data.get("shell_script", ""))
                            self._log(f"[+] Generated script written to: {out_script}\n")
                    return

                if tool_name == "ADosManager APK Packager" and target_url == MANAGER_API_URL:
                    out_path = self.arg_entries["output"].get() if "output" in self.arg_entries else ""
                    apk_payload = {"output": out_path, "output_path": out_path} if out_path else {}
                    req = urllib.request.Request(
                        f"{target_url}/build-apk",
                        data=json.dumps(apk_payload).encode("utf-8"),
                        headers={"Content-Type": "application/json", "User-Agent": "ADosStudio/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        self._log(f"[+] APK Packager Response:\n{json.dumps(res_data, indent=2)}\n")
                    return

                # Standard asynchronous process execution via POST /run-tool
                base_tool = tool_name.split()[0].lower()
                run_payload = {"tool": base_tool, "args": full_args}
                req = urllib.request.Request(
                    f"{target_url}/run-tool",
                    data=json.dumps(run_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "ADosStudio/1.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))

                pid = resp_data.get("pid")
                if not pid:
                    self._log(f"[!] Server dispatch returned: {resp_data}\n")
                    return

                self.current_backend_pid = pid
                self.current_backend_url = target_url
                self._log(f"[+] Tool launched on remote backend with PID {pid}. Streaming logs...\n")

                # Poll live logs until completion
                last_len = 0
                poll_url = f"{target_url}/tool-output/{pid}"

                while True:
                    time.sleep(0.4)
                    try:
                        poll_req = urllib.request.Request(poll_url, headers={"User-Agent": "ADosStudio/1.0"})
                        with urllib.request.urlopen(poll_req, timeout=5) as log_resp:
                            log_data = json.loads(log_resp.read().decode("utf-8"))

                        full_output = log_data.get("output", "")
                        if len(full_output) > last_len:
                            new_text = full_output[last_len:]
                            self._log(new_text)
                            last_len = len(full_output)

                        if not log_data.get("running", False):
                            rc = log_data.get("returncode", 0)
                            self._log(f"\n[Remote backend process {pid} finished with exit code {rc}]\n")
                            break
                    except Exception as poll_err:
                        self._log(f"\n[!] Log polling ended: {poll_err}\n")
                        break

            except urllib.error.HTTPError as http_err:
                try:
                    err_content = http_err.read().decode("utf-8")
                    self._log(f"\n[!] Backend HTTP Error {http_err.code}: {err_content}\n")
                except Exception:
                    self._log(f"\n[!] Backend HTTP Error {http_err.code}: {http_err.reason}\n")
            except Exception as ex:
                self._log(f"\n[!] Backend Dispatch Error: {ex}\n")
            finally:
                self.current_backend_pid = None
                self.current_backend_url = None

        threading.Thread(target=_execute, daemon=True).start()

    def _stop_tool(self):
        """Stop local running process or dispatch stop request to remote backend."""
        stopped = False
        if self.current_proc:
            try:
                self.current_proc.terminate()
                self._log("\n[!] Local subprocess terminated by user.\n")
                stopped = True
            except Exception as e:
                self._log(f"\n[ERROR] Could not terminate local subprocess: {e}\n")
            finally:
                self.current_proc = None

        if self.current_backend_pid and self.current_backend_url:
            try:
                pid = self.current_backend_pid
                target_url = self.current_backend_url
                req = urllib.request.Request(
                    f"{target_url}/stop-tool",
                    data=json.dumps({"pid": pid}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "ADosStudio/1.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    self._log(f"\n[!] Termination dispatched to backend: {res}\n")
                stopped = True
            except Exception as ex:
                self._log(f"\n[ERROR] Could not terminate backend process: {ex}\n")
            finally:
                self.current_backend_pid = None
                self.current_backend_url = None

        if not stopped:
            self._log("\n[i] No active subprocess or backend job currently running to stop.\n")

    # -----------------------------------------------------------------------
    # Logging and Output Helpers
    # -----------------------------------------------------------------------

    def _clear_log(self):
        self.output_txt.delete(1.0, tk.END)

    def _log(self, text):
        self._append_to(self.output_txt, text)

    def _append_to(self, widget, text):
        def _do():
            try:
                widget.insert(tk.END, text)
                widget.see(tk.END)
            except Exception:
                pass
        self.after(0, _do)

    # -----------------------------------------------------------------------
    # Terminal, ADB & APK Builders
    # -----------------------------------------------------------------------

    def _run_terminal_cmd(self, event=None):
        cmd = self.term_entry.get().strip()
        if not cmd:
            return
        self.term_entry.delete(0, tk.END)
        self._term_append(f"\n$ {cmd}\n")
        self._execute_command(cmd, self.term_txt)

    def _term_append(self, text):
        self._append_to(self.term_txt, text)

    def _run_adb(self, cmd):
        clean_cmd = cmd.strip()
        if not clean_cmd:
            return
        avail, _ = check_binary_available("adb")
        if not avail:
            self._append_to(
                self.phone_out,
                f"\n[!] PRE-FLIGHT CHECK WARNING: 'adb' binary was not found in system PATH.\n"
                f"[*] Please install Android Platform Tools and ensure 'adb' is available.\n"
            )
            return
        self._append_to(self.phone_out, f"\n$ {clean_cmd}\n")
        self._execute_command(clean_cmd, self.phone_out)

    def _build_apk(self):
        self.apk_out.delete(1.0, tk.END)
        script = os.path.join(REPO_ROOT, 'tools', 'build_apk.py')
        self._execute_command(f'"{sys.executable}" "{script}"', self.apk_out)

    # -----------------------------------------------------------------------
    # Health and Status Monitoring
    # -----------------------------------------------------------------------

    def _check_backend(self):
        """Asynchronously query health endpoints of BOTH backend servers."""
        def _check():
            # 1. ADos API (port 8000)
            ados_ok = False
            try:
                req = urllib.request.Request(f"{ADOS_API_URL}/api/health", headers={"User-Agent": "ADosStudio/1.0"})
                with urllib.request.urlopen(req, timeout=2) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    if data.get("status") in ("ok", "running"):
                        ados_ok = True
            except Exception:
                ados_ok = False

            # 2. ADos-Manager API (port 8765)
            mgr_ok = False
            try:
                req = urllib.request.Request(f"{MANAGER_API_URL}/api/health", headers={"User-Agent": "ADosStudio/1.0"})
                with urllib.request.urlopen(req, timeout=2) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    if data.get("status") in ("ok", "running"):
                        mgr_ok = True
            except Exception:
                # Fallback to /status
                try:
                    req = urllib.request.Request(f"{MANAGER_API_URL}/status", headers={"User-Agent": "ADosStudio/1.0"})
                    with urllib.request.urlopen(req, timeout=2) as r:
                        data = json.loads(r.read().decode("utf-8"))
                        if data.get("status") in ("ok", "running"):
                            mgr_ok = True
                except Exception:
                    mgr_ok = False

            self.ados_api_online = ados_ok
            self.manager_api_online = mgr_ok
            self.backend_online = ados_ok or mgr_ok

            def _update():
                try:
                    if hasattr(self, 'ados_status_lbl'):
                        ados_text = "● ADos Core (8000): Online" if ados_ok else "● ADos Core (8000): Offline"
                        self.ados_status_lbl.config(text=ados_text, fg=GREEN if ados_ok else RED)

                    if hasattr(self, 'manager_status_lbl'):
                        mgr_text = "● Manager (8765): Online" if mgr_ok else "● Manager (8765): Offline"
                        self.manager_status_lbl.config(text=mgr_text, fg=GREEN if mgr_ok else RED)

                    if hasattr(self, 'status_lbl'):
                        if ados_ok and mgr_ok:
                            self.status_lbl.config(text="● Backends: 2/2 Online", fg=GREEN)
                        elif ados_ok or mgr_ok:
                            self.status_lbl.config(text="● Backends: 1/2 Online", fg=YELLOW)
                        else:
                            self.status_lbl.config(text="● Backends: Offline", fg=RED)
                except Exception:
                    pass

            self.after(0, _update)

        threading.Thread(target=_check, daemon=True).start()

    def _refresh_devices(self):
        """Asynchronously query adb devices to populate device list."""
        def _get():
            try:
                avail, _ = check_binary_available("adb")
                if not avail:
                    self.after(0, lambda: self._update_devices([]))
                    return
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
                lines = [l for l in result.stdout.strip().split('\n')[1:] if l.strip() and 'device' in l]
                self.after(0, lambda: self._update_devices(lines))
            except Exception:
                self.after(0, lambda: self._update_devices([]))

        threading.Thread(target=_get, daemon=True).start()

    def _update_devices(self, devices):
        try:
            self.devices_lb.delete(0, tk.END)
            if devices:
                for d in devices:
                    self.devices_lb.insert(tk.END, d.split()[0])
            else:
                self.devices_lb.insert(tk.END, "(no devices detected)")
        except Exception:
            pass


# Compatibility alias
ADosStudioGUI = ADosStudio


def main():
    app = ADosStudio()
    app.mainloop()


if __name__ == '__main__':
    main()
