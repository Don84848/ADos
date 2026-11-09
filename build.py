#!/usr/bin/env python3
"""
ADos (Advanced Defensive/Offensive OS) - Mobile NetHunter Builder
Unified builder for Kali NetHunter cybersecurity tools, Samsung optimizations,
and flashable Android packages.

Usage:
    python3 build.py --device [phone_model] --release [os_version] [options]
"""

import os
import sys
import argparse
import json
from typing import List

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.builder_engine import ADosBuilderEngine, DeviceNotFoundError, UnsupportedReleaseError
from core.package_generator import PackageGenerator

BANNER = r"""
    ___    ____            
   /   |  / __ \____  _____
  / /| | / / / / __ \/ ___/
 / ___ |/ /_/ / /_/ (__  ) 
/_/  |_/_____/\____/____/  
======================================================
  ADos - Mobile Cybersecurity Operating System Suite
  NetHunter Unified Open-Source Build Orchestrator
======================================================
"""


def start_server(port: int = 8000):
    """Start the ADos Full-Stack Backend API server."""
    import subprocess
    api_script = os.path.join(REPO_ROOT, "backend", "api.py")
    proc = subprocess.Popen([sys.executable, api_script, "--port", str(port)], cwd=REPO_ROOT)
    print(f"[*] ADos Backend API started on port {port} (PID: {proc.pid})")
    return proc

def launch_gui():
    """Launch the ADos Studio desktop GUI application."""
    import subprocess
    launcher = os.path.join(REPO_ROOT, "launch_studio.py")
    if not os.path.isfile(launcher):
        launcher = os.path.join(REPO_ROOT, "desktop", "ados_studio.py")
    proc = subprocess.Popen([sys.executable, launcher], cwd=REPO_ROOT)
    print(f"[*] ADos Studio Desktop GUI launched (PID: {proc.pid})")
    return proc

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ADos NetHunter Mobile Cybersecurity Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 build.py --device samsung_s10 --release 11
  python3 build.py --device samsung_s20 --release 12 --rootfs minimal --debloat-samsung
  python3 build.py --device generic_arm64 --release 13 --type magisk
  python3 build.py --list-devices
  python3 build.py --check-deps
        """
    )
    
    parser.add_argument(
        "-d", "--device",
        help="Target phone model codename (e.g., samsung_s10, samsung_s20, generic_arm64)"
    )
    parser.add_argument(
        "-r", "--release",
        help="Android OS release version (e.g., 9, 10, 11, 12, 13)"
    )
    parser.add_argument(
        "--rootfs",
        choices=["nano", "minimal", "full"],
        default="minimal",
        help="Kali NetHunter Rootfs size: nano (~200MB), minimal (~700MB, default), full (~1.8GB)"
    )
    parser.add_argument(
        "--tools",
        choices=["essential", "wireless", "web", "redteam", "full"],
        default="essential",
        help="Hacking tools arsenal profile: essential, wireless, web, redteam, full"
    )
    parser.add_argument(
        "-t", "--type",
        dest="pkg_type",
        choices=["twrp", "magisk"],
        default="twrp",
        help="Output package type: flashable recovery zip ('twrp') or Magisk module ('magisk')"
    )
    parser.add_argument(
        "--debloat-samsung",
        action="store_true",
        help="Include Samsung OneUI/Knox debloater script for lightweight RAM optimization"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all supported device models and configurations"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check environment dependencies (git, python, tar, etc.)"
    )
    parser.add_argument(
        "--init-submodules",
        action="store_true",
        help="Initialize and update all Git submodules"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the build process and validate configurations without creating zips"
    )
    parser.add_argument(
        "--launch-gui",
        action="store_true",
        help="Launch the ADos Studio desktop GUI on PC"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the ADos Full-Stack Backend API server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the Backend API server (default: 8000)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Custom output directory or file path for the generated ZIP"
    )

    return parser

def print_devices_table(devices: dict):
    print("\n[+] Supported Hardware Configurations:")
    print(f"{'Codename':<18} {'Brand':<10} {'Arch':<8} {'Releases':<18} {'Model Description'}")
    print("-" * 80)
    for name, p in devices.items():
        rels = ", ".join(p.get("supported_releases", []))
        brand = p.get("brand", "Unknown")
        arch = p.get("arch", "arm64")
        desc = p.get("model_name", name)
        print(f"{name:<18} {brand:<10} {arch:<8} {rels:<18} {desc}")
    print("-" * 80)

def main(args: List[str] = None):
    parser = create_parser()
    opts = parser.parse_args(args)
    
    print(BANNER)
    
    engine = ADosBuilderEngine(repo_root=REPO_ROOT)
    
    # 0. Action: Launch Desktop GUI
    if opts.launch_gui:
        launch_gui()
        return 0

    # 0. Action: Start Backend API Server
    if opts.serve:
        proc = start_server(opts.port)
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("[*] Stopping server...")
            proc.terminate()
        return 0

        # 1. Action: List Devices
    if opts.list_devices:
        print_devices_table(engine.list_devices())
        return 0

    # 2. Action: Check Dependencies
    if opts.check_deps:
        print("[*] Checking system dependencies...")
        deps = engine.check_dependencies()
        for tool, available in deps.items():
            status = "FOUND" if available else "MISSING (Optional/Recommended)"
            print(f"  - {tool:<15}: {status}")
            
        missing_subs = engine.verify_submodules()
        if missing_subs:
            print("\n[!] Uninitialized submodules detected:")
            for sub in missing_subs:
                print(f"  - {sub}")
            print("\n[Tip] Run with --init-submodules or 'git submodule update --init --recursive'")
        else:
            print("\n[+] All submodules are checked out.")
        return 0

    # 3. Action: Init Submodules
    if opts.init_submodules:
        print("[*] Updating submodules...")
        import subprocess
        res = subprocess.run(["git", "submodule", "update", "--init", "--recursive"], cwd=REPO_ROOT)
        return res.returncode

    # 4. Main Build Pipeline requires --device and --release
    if not opts.device or not opts.release:
        parser.print_help()
        print("\n[!] Error: Both --device and --release are required to build ADos.")
        print("Example: python3 build.py --device samsung_s10 --release 11")
        return 1

    try:
        profile = engine.get_device_profile(opts.device, opts.release)
    except (DeviceNotFoundError, UnsupportedReleaseError) as e:
        print(f"[!] Configuration Error: {e}")
        return 1

    print(f"[*] Target Device  : {profile.get('model_name', opts.device)} ({opts.device})")
    print(f"[*] Architecture   : {profile.get('arch', 'arm64')}")
    print(f"[*] Android Version: {opts.release}")
    print(f"[*] Rootfs Mode    : {opts.rootfs}")
    print(f"[*] Hacking Arsenal: {opts.tools.upper()}")
    print(f"[*] Package Format : {opts.pkg_type.upper()}")
    
    is_samsung = profile.get("brand") == "Samsung"
    if is_samsung:
        print("[+] Samsung Device Detected:")
        print(f"    - Ramdisk Patch : {profile.get('ramdisk_patch', 'samsung_exynos_oneui')}")
        print(f"    - Knox Bypass   : {profile.get('knox_mitigation', True)}")
        print(f"    - USB ConfigFS  : {profile.get('usb_gadget_driver', 'configfs')}")
        if opts.debloat_samsung:
            print("    - Lightweight Optimization: OneUI bloatware stripper ENABLED")

    # Resolve Rootfs
    rootfs_info = engine.resolve_rootfs(profile.get("arch", "arm64"), opts.rootfs)
    print(f"[*] Rootfs Bundle  : {rootfs_info['filename']} ({rootfs_info['description']})")

    if opts.dry_run:
        print("\n[+] DRY-RUN validation completed successfully. All configurations are valid!")
        return 0

    # Staging files
    staging = {
        "system/etc/ados-release": f"ADos 1.0 (Device: {opts.device}, Release: {opts.release})",
        "system/etc/ados/device_profile.json": json.dumps(profile, indent=2),
        "data/ados/rootfs_manifest.json": json.dumps(rootfs_info, indent=2)
    }

    # Include Samsung debloater if applicable
    debloat_script_path = os.path.join(REPO_ROOT, "scripts", "debloat-samsung.sh")
    if (opts.debloat_samsung or is_samsung) and os.path.exists(debloat_script_path):
        with open(debloat_script_path, "r", encoding="utf-8") as f:
            staging["data/ados/scripts/debloat-samsung.sh"] = f.read()

    # Include USB Gadget setup script
    gadget_script_path = os.path.join(REPO_ROOT, "scripts", "setup-usb-gadget.sh")
    if os.path.exists(gadget_script_path):
        with open(gadget_script_path, "r", encoding="utf-8") as f:
            staging["data/ados/scripts/setup-usb-gadget.sh"] = f.read()

    # Include Hacking Tools Installer & Mobile Menu
    tools_script_path = os.path.join(REPO_ROOT, "scripts", "install-tools.sh")
    if os.path.exists(tools_script_path):
        with open(tools_script_path, "r", encoding="utf-8") as f:
            staging["data/ados/scripts/install-tools.sh"] = f.read()

    menu_script_path = os.path.join(REPO_ROOT, "scripts", "ados-menu.sh")
    if os.path.exists(menu_script_path):
        with open(menu_script_path, "r", encoding="utf-8") as f:
            content = f.read()
            staging["data/ados/scripts/ados-menu.sh"] = content
            staging["system/bin/ados-menu"] = content

    toolsets_config_path = os.path.join(REPO_ROOT, "config", "toolsets.json")
    if os.path.exists(toolsets_config_path):
        with open(toolsets_config_path, "r", encoding="utf-8") as f:
            staging["data/ados/config/toolsets.json"] = f.read()

    # Determine Output Path
    out_dir = opts.output or os.path.join(REPO_ROOT, "output")
    if os.path.isdir(out_dir) or not out_dir.endswith(".zip"):
        zip_filename = f"ADos-{opts.device}-android{opts.release}-{opts.rootfs}-{opts.pkg_type}.zip"
        target_zip = os.path.join(out_dir, zip_filename)
    else:
        target_zip = out_dir

    print(f"\n[*] Packaging {opts.pkg_type.upper()} flashable ZIP...")
    generator = PackageGenerator(output_path=target_zip)
    
    manifest_data = {
        "name": "ADos-NetHunter",
        "version": "1.0.0",
        "device": opts.device,
        "release": opts.release,
        "arch": profile.get("arch", "arm64"),
        "type": opts.pkg_type,
        "rootfs": rootfs_info,
        "tools_profile": opts.tools,
        "is_samsung": is_samsung,
        "debloated": opts.debloat_samsung or is_samsung
    }

    pkg_path, checksum = generator.create_package(manifest_data, staging_files=staging)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Build generated successfully!")
    print(f" Package: {pkg_path}")
    print(f" SHA256 : {checksum}")
    print("=" * 60)
    print("\nNext Steps:")
    print(" 1. Copy the package to your phone storage or USB OTG flash drive.")
    print(" 2. Boot your phone into TWRP/OrangeFox recovery (or Magisk Manager if using Magisk).")
    print(" 3. Flash the ZIP and reboot.")
    print(" 4. Refer to docs/INSTALL_GUIDE.md and docs/SAMSUNG_GUIDE.md for complete details.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
