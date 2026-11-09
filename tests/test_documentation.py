import unittest
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestDocumentationIntegrity(unittest.TestCase):
    def test_readme_content(self):
        readme_path = os.path.join(REPO_ROOT, "README.md")
        self.assertTrue(os.path.exists(readme_path), f"Missing {readme_path}")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ADos", content)
        self.assertIn("python3 build.py --device", content)
        self.assertIn("docs/INSTALL_GUIDE.md", content)
        self.assertIn("docs/SAMSUNG_GUIDE.md", content)
        self.assertIn("kali-nethunter-installer", content)

    def test_install_guide_content(self):
        guide_path = os.path.join(REPO_ROOT, "docs", "INSTALL_GUIDE.md")
        self.assertTrue(os.path.exists(guide_path), f"Missing {guide_path}")
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("TWRP", content)
        self.assertIn("Magisk", content)
        self.assertIn("KeX", content)
        self.assertIn("Chroot", content)
        self.assertIn("Monitor Mode", content)

    def test_samsung_guide_content(self):
        guide_path = os.path.join(REPO_ROOT, "docs", "SAMSUNG_GUIDE.md")
        self.assertTrue(os.path.exists(guide_path), f"Missing {guide_path}")
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Odin", content)
        self.assertIn("Knox", content)
        self.assertIn("vbmeta", content)
        self.assertIn("debloat", content.lower())

    def test_developer_guide_content(self):
        guide_path = os.path.join(REPO_ROOT, "docs", "DEVELOPER_GUIDE.md")
        self.assertTrue(os.path.exists(guide_path), f"Missing {guide_path}")
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("config/devices.json", content)
        self.assertIn("submodule", content.lower())

if __name__ == "__main__":
    unittest.main()
