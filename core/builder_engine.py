import os
import sys
import json
import shutil
import hashlib
from typing import Dict, Any, List, Tuple

class DeviceNotFoundError(Exception):
    """Raised when the requested device model is not in configuration."""
    pass

class UnsupportedReleaseError(Exception):
    """Raised when the OS release is not supported for the device."""
    pass

class ADosBuilderEngine:
    def __init__(self, config_path: str = None, repo_root: str = None):
        self.repo_root = repo_root or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.config_path = config_path or os.path.join(self.repo_root, "config", "devices.json")
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.devices = self.config.get("devices", {})

    def list_devices(self) -> Dict[str, Any]:
        """Returns the dictionary of all supported devices."""
        return self.devices

    def get_device_profile(self, device_name: str, release: str = None) -> Dict[str, Any]:
        """Validates and retrieves the hardware profile for a given device and release."""
        if device_name not in self.devices:
            available = ", ".join(self.devices.keys())
            raise DeviceNotFoundError(
                f"Device '{device_name}' not found. Available devices: {available}"
            )
        
        profile = self.devices[device_name]
        
        if release:
            # release might be passed as string '11' or int
            rel_str = str(release).strip()
            supported = [str(r) for r in profile.get("supported_releases", [])]
            if supported and rel_str not in supported:
                raise UnsupportedReleaseError(
                    f"Android release '{rel_str}' is not supported for {device_name}. "
                    f"Supported releases: {', '.join(supported)}"
                )
        
        return profile

    def check_dependencies(self) -> Dict[str, bool]:
        """Checks required build tools in the system environment."""
        tools = ["git", "python", "tar"]
        # On Windows or Linux, check zip or python zipfile capability
        status = {}
        for tool in tools:
            status[tool] = shutil.which(tool) is not None
        # Always True for zip since Python's standard zipfile handles zip generation
        status["zip_support"] = True
        return status

    def verify_submodules(self) -> List[str]:
        """Checks if all required submodules are checked out or initialized."""
        submodule_paths = [
            "apps/kali-nethunter-app",
            "apps/kali-nethunter-terminal",
            "apps/kali-nethunter-kex",
            "apps/kali-nethunter-store-client",
            "core/installer",
            "core/arm-rootfs",
            "devices/kernel-tree"
        ]
        missing = []
        for rel_path in submodule_paths:
            full_path = os.path.join(self.repo_root, rel_path)
            # A submodule is missing if the directory doesn't exist or is empty
            if not os.path.exists(full_path) or not os.listdir(full_path):
                missing.append(rel_path)
        return missing

    def resolve_rootfs(self, arch: str, mode: str = "minimal") -> Dict[str, str]:
        """Resolves target rootfs parameters and download URL / recipe."""
        base_url = "https://kali.download/nethunter-images/current"
        
        # Determine mode
        # 'nano' = lightweight ultra-minimal chroot (~200MB)
        # 'minimal' = essential pentest tools + nethunter core (~700MB)
        # 'full' = complete Kali Linux package set (~1.8GB)
        filename_map = {
            ("arm64", "nano"): f"kalifs-arm64-nano.tar.xz",
            ("arm64", "minimal"): f"kalifs-arm64-minimal.tar.xz",
            ("arm64", "full"): f"kalifs-arm64-full.tar.xz",
            ("armhf", "nano"): f"kalifs-armhf-nano.tar.xz",
            ("armhf", "minimal"): f"kalifs-armhf-minimal.tar.xz",
            ("armhf", "full"): f"kalifs-armhf-full.tar.xz",
        }
        
        target_file = filename_map.get((arch, mode), f"kalifs-{arch}-{mode}.tar.xz")
        return {
            "mode": mode,
            "arch": arch,
            "filename": target_file,
            "url": f"{base_url}/{target_file}",
            "description": f"Kali NetHunter {arch.upper()} {mode.capitalize()} Rootfs"
        }
