import unittest
import os
import sys
import json
import tempfile
import zipfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.builder_engine import ADosBuilderEngine, DeviceNotFoundError, UnsupportedReleaseError
from core.package_generator import PackageGenerator
import build

class TestBuildCLIAndEngine(unittest.TestCase):
    def setUp(self):
        self.config_path = os.path.join(REPO_ROOT, "config", "devices.json")
        self.engine = ADosBuilderEngine(config_path=self.config_path)

    def test_list_devices(self):
        devices = self.engine.list_devices()
        self.assertIn("generic_arm64", devices)
        self.assertIn("samsung_s10", devices)

    def test_validate_valid_device_and_release(self):
        profile = self.engine.get_device_profile("samsung_s10", "11")
        self.assertEqual(profile["brand"], "Samsung")
        self.assertEqual(profile["arch"], "arm64")

    def test_validate_invalid_device_raises(self):
        with self.assertRaises(DeviceNotFoundError):
            self.engine.get_device_profile("unknown_phone_xyz", "11")

    def test_validate_unsupported_release_raises(self):
        with self.assertRaises(UnsupportedReleaseError):
            self.engine.get_device_profile("samsung_s9", "14")

    def test_cli_parser_defaults(self):
        parser = build.create_parser()
        args = parser.parse_args(["--device", "samsung_s10", "--release", "11"])
        self.assertEqual(args.device, "samsung_s10")
        self.assertEqual(args.release, "11")
        self.assertEqual(args.rootfs, "minimal")
        self.assertEqual(args.pkg_type, "twrp")
        self.assertFalse(args.dry_run)

    def test_cli_parser_options(self):
        parser = build.create_parser()
        args = parser.parse_args([
            "--device", "generic_arm64",
            "--release", "12",
            "--rootfs", "nano",
            "--type", "magisk",
            "--debloat-samsung",
            "--dry-run"
        ])
        self.assertEqual(args.rootfs, "nano")
        self.assertEqual(args.pkg_type, "magisk")
        self.assertTrue(args.debloat_samsung)
        self.assertTrue(args.dry_run)

    def test_package_generator_creates_valid_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_zip = os.path.join(tmpdir, "test_package.zip")
            generator = PackageGenerator(output_path=out_zip)
            
            manifest_info = {
                "name": "ADos-NetHunter",
                "device": "samsung_s10",
                "release": "11",
                "arch": "arm64",
                "type": "twrp"
            }
            
            created_path, sha256_hash = generator.create_package(
                manifest=manifest_info,
                staging_files={"system/etc/ados-release": "ADos 1.0 (Mobile Pentest)"}
            )
            
            self.assertTrue(os.path.exists(created_path))
            self.assertTrue(len(sha256_hash) == 64)
            
            # Verify zip contents
            with zipfile.ZipFile(created_path, "r") as z:
                names = z.namelist()
                self.assertIn("META-INF/com/google/android/updater-script", names)
                self.assertIn("system/etc/ados-release", names)
                self.assertIn("ados_manifest.json", names)

if __name__ == "__main__":
    unittest.main()
