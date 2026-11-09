import unittest
import os
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestSamsungScriptsAndProfiles(unittest.TestCase):
    def test_samsung_profiles_json(self):
        profile_path = os.path.join(REPO_ROOT, "devices", "samsung", "samsung_profiles.json")
        self.assertTrue(os.path.exists(profile_path), f"Missing {profile_path}")
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertIn("samsung_devices", data)
        devices = data["samsung_devices"]
        self.assertIn("samsung_s10", devices)
        self.assertIn("partition_scheme", devices["samsung_s10"])
        self.assertIn("knox_services", data)
        self.assertTrue(len(data["knox_services"]) > 5)

    def test_debloat_script_exists_and_valid(self):
        script_path = os.path.join(REPO_ROOT, "scripts", "debloat-samsung.sh")
        self.assertTrue(os.path.exists(script_path), f"Missing {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertTrue(content.startswith("#!/"), "Script must start with a shebang")
        # Check for key bloatware target packages
        expected_pkgs = [
            "com.samsung.android.bixby.agent",
            "com.sec.enterprise.knox.attestation",
            "com.samsung.android.game.gametools",
            "com.facebook.katana"
        ]
        for pkg in expected_pkgs:
            self.assertIn(pkg, content, f"Expected debloat package {pkg} in debloat script")
        
        self.assertIn("pm uninstall", content)

    def test_anykernel_samsung_script(self):
        script_path = os.path.join(REPO_ROOT, "devices", "samsung", "anykernel_samsung.sh")
        self.assertTrue(os.path.exists(script_path), f"Missing {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("samsung", content.lower())
        self.assertIn("defex", content.lower())

    def test_setup_usb_gadget_script(self):
        script_path = os.path.join(REPO_ROOT, "scripts", "setup-usb-gadget.sh")
        self.assertTrue(os.path.exists(script_path), f"Missing {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("configfs", content.lower())
        self.assertIn("hidg0", content.lower())

if __name__ == "__main__":
    unittest.main()
