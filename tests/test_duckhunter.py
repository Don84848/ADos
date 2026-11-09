import unittest
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.duckhunter.duckhunter import DuckHunterCompiler

class TestDuckHunterAndSecurityTools(unittest.TestCase):
    def setUp(self):
        self.compiler = DuckHunterCompiler()

    def test_duckhunter_string_compilation(self):
        ducky_script = "STRING Hello"
        hid_commands = self.compiler.compile(ducky_script)
        self.assertTrue(len(hid_commands) > 0)
        # Should contain keydown and keyup for characters
        self.assertTrue(any("hidg0" in cmd for cmd in hid_commands))

    def test_duckhunter_gui_and_delay(self):
        ducky_script = """
        REM Test comment
        DELAY 500
        GUI r
        DELAY 200
        STRING cmd
        ENTER
        """
        hid_commands = self.compiler.compile(ducky_script)
        # Verify delay command translated into sleep
        self.assertTrue(any("sleep 0.5" in cmd for cmd in hid_commands))
        self.assertTrue(any("sleep 0.2" in cmd for cmd in hid_commands))

    def test_firmware_manifest(self):
        fw_path = os.path.join(REPO_ROOT, "tools", "firmware", "firmware_manifest.json")
        self.assertTrue(os.path.exists(fw_path))
        import json
        with open(fw_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("adapters", data)
        self.assertIn("ath9k_htc", data["adapters"])
        self.assertIn("rtl8812au", data["adapters"])

    def test_wireless_and_bt_scripts(self):
        wl_script = os.path.join(REPO_ROOT, "tools", "wireless", "wireless_toolkit.sh")
        bt_script = os.path.join(REPO_ROOT, "tools", "bluetooth", "bt_recon.sh")
        self.assertTrue(os.path.exists(wl_script))
        self.assertTrue(os.path.exists(bt_script))

if __name__ == "__main__":
    unittest.main()
