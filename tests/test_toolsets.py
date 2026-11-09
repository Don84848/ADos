import unittest
import os
import json
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.builder_engine import ADosBuilderEngine
import build

class TestToolsetsAndMobileMenu(unittest.TestCase):
    def test_toolsets_json(self):
        toolsets_path = os.path.join(REPO_ROOT, "config", "toolsets.json")
        self.assertTrue(os.path.exists(toolsets_path), f"Missing {toolsets_path}")
        with open(toolsets_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertIn("toolsets", data)
        tools = data["toolsets"]
        self.assertIn("wireless", tools)
        self.assertIn("web", tools)
        self.assertIn("mitm", tools)
        self.assertIn("exploitation", tools)
        self.assertIn("passwords", tools)
        
        # Verify specific popular tools
        self.assertIn("nmap", tools["network"]["packages"])
        self.assertIn("aircrack-ng", tools["wireless"]["packages"])
        self.assertIn("wifite", tools["wireless"]["packages"])
        self.assertIn("sqlmap", tools["web"]["packages"])
        self.assertIn("metasploit-framework", tools["exploitation"]["packages"])

    def test_install_tools_script(self):
        script_path = os.path.join(REPO_ROOT, "scripts", "install-tools.sh")
        self.assertTrue(os.path.exists(script_path), f"Missing {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("#!/bin/"))
        self.assertIn("apt-get", content)
        self.assertIn("metasploit-framework", content)

    def test_ados_menu_script(self):
        menu_path = os.path.join(REPO_ROOT, "scripts", "ados-menu.sh")
        self.assertTrue(os.path.exists(menu_path), f"Missing {menu_path}")
        with open(menu_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ADos", content)
        self.assertIn("Network Recon", content)
        self.assertIn("Wi-Fi", content)

    def test_build_cli_tools_flag(self):
        parser = build.create_parser()
        args = parser.parse_args(["--device", "samsung_s10", "--release", "11", "--tools", "redteam"])
        self.assertEqual(args.tools, "redteam")

if __name__ == "__main__":
    unittest.main()
