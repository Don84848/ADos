import unittest
import json
import os
import configparser

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestDevicesConfigAndSubmodules(unittest.TestCase):
    def test_devices_json_exists_and_valid(self):
        config_path = os.path.join(REPO_ROOT, "config", "devices.json")
        self.assertTrue(os.path.exists(config_path), f"Missing {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertIn("devices", data)
        devices = data["devices"]
        
        # Verify generic devices
        self.assertIn("generic_arm64", devices)
        self.assertIn("generic_armhf", devices)
        
        # Verify Samsung devices
        samsung_models = [
            "samsung_s9", "samsung_s10", "samsung_s20",
            "samsung_note9", "samsung_note10", "samsung_a50", "samsung_a52"
        ]
        for model in samsung_models:
            self.assertIn(model, devices, f"Expected Samsung model {model} in devices.json")
            item = devices[model]
            self.assertIn("arch", item)
            self.assertIn("brand", item)
            self.assertEqual(item["brand"], "Samsung")
            self.assertIn("supported_releases", item)
            self.assertIn("anykernel", item)
            self.assertIn("ramdisk_patch", item)
            self.assertIn("debloat_profile", item)

    def test_gitmodules_contains_all_12_repos(self):
        gitmodules_path = os.path.join(REPO_ROOT, ".gitmodules")
        self.assertTrue(os.path.exists(gitmodules_path), f"Missing {gitmodules_path}")
        
        config = configparser.ConfigParser()
        config.read(gitmodules_path)
        
        # We need git submodules representing the primary repositories:
        expected_modules = [
            "apps/kali-nethunter-app",
            "apps/kali-nethunter-terminal",
            "apps/kali-nethunter-kex",
            "apps/kali-nethunter-store-client",
            "core/installer",
            "core/arm-rootfs",
            "devices/kernel-tree"
        ]
        
        module_paths = [config[section].get("path") for section in config.sections() if "path" in config[section]]
        for exp in expected_modules:
            self.assertIn(exp, module_paths, f"Expected submodule path {exp} in .gitmodules")

if __name__ == "__main__":
    unittest.main()
