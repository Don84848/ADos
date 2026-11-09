#!/usr/bin/env python3
"""Tests for the ADos On-Demand Tool Resolver & Installer."""
import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.tool_installer import (
    ensure_tool_ready,
    ensure_tools_bin_in_path,
    install_tool,
    is_tool_installed,
    TOOL_SPECS,
)


class TestADosToolInstaller(unittest.TestCase):
    def test_installer_script_exists_and_pure_stdlib(self):
        inst_path = os.path.join(REPO_ROOT, "tools", "tool_installer.py")
        self.assertTrue(os.path.exists(inst_path))
        with open(inst_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pkg in ["requests", "fastapi", "flask", "aiohttp", "httpx"]:
            self.assertNotIn(f"import {pkg}", content)

    def test_tool_specs_catalog(self):
        self.assertIn("john", TOOL_SPECS)
        self.assertIn("sqlmap", TOOL_SPECS)
        self.assertIn("nmap", TOOL_SPECS)
        self.assertIn("gobuster", TOOL_SPECS)
        self.assertIn("netcat", TOOL_SPECS)

    def test_ensure_john_ready(self):
        ok, path = ensure_tool_ready("john")
        self.assertTrue(ok)
        inst, resolved = is_tool_installed("john")
        self.assertTrue(inst)
        self.assertTrue(len(resolved) > 0)

    def test_ensure_netcat_ready(self):
        ok, path = ensure_tool_ready("netcat")
        self.assertTrue(ok)
        inst, resolved = is_tool_installed("netcat")
        self.assertTrue(inst)

    def test_ensure_gobuster_ready(self):
        ok, path = ensure_tool_ready("gobuster")
        self.assertTrue(ok)
        inst, resolved = is_tool_installed("gobuster")
        self.assertTrue(inst)

    def test_install_script_flag_support(self):
        script_path = os.path.join(REPO_ROOT, "scripts", "install-tools.sh")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("--tool", content)
        self.assertIn("tool_installer.py", content)

    def test_backend_api_has_installer_endpoints(self):
        api_path = os.path.join(REPO_ROOT, "backend", "api.py")
        with open(api_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("handle_install_tool", content)
        self.assertIn("handle_list_installed_tools", content)
        self.assertIn("/api/tools/installed", content)


if __name__ == "__main__":
    unittest.main()
