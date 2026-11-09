import unittest
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestDockerEnvironment(unittest.TestCase):
    def test_dockerfile_contents(self):
        dockerfile = os.path.join(REPO_ROOT, "Dockerfile")
        self.assertTrue(os.path.exists(dockerfile), f"Missing {dockerfile}")
        with open(dockerfile, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("FROM", content)
        self.assertIn("python3", content)
        self.assertIn("ENTRYPOINT", content)
        self.assertIn("build.py", content)

    def test_docker_compose_contents(self):
        dc_file = os.path.join(REPO_ROOT, "docker-compose.yml")
        self.assertTrue(os.path.exists(dc_file), f"Missing {dc_file}")
        with open(dc_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("services:", content)
        self.assertIn("volumes:", content)

    def test_run_scripts_exist(self):
        sh_script = os.path.join(REPO_ROOT, "run_docker.sh")
        bat_script = os.path.join(REPO_ROOT, "run_docker.bat")
        self.assertTrue(os.path.exists(sh_script))
        self.assertTrue(os.path.exists(bat_script))

if __name__ == "__main__":
    unittest.main()
