# ADos Developer & Porting Guide

This guide details the internal architecture of **ADos**, explaining how to add support for new smartphone models, build Android companion APKs from source, compile custom kernels, and extend the build system.

---

## 🏗️ Architecture Overview

ADos operates as a meta-repository and build orchestrator. Rather than duplicating gigabytes of independent repositories directly, it coordinates official upstream repositories via Git submodules and automates the integration pipeline through `build.py`.

```
ADos/
├── build.py                     # Main CLI orchestrator
├── Dockerfile                   # Build container definition
├── docker-compose.yml           # Container orchestration
├── config/
│   └── devices.json             # Device hardware specifications
├── core/
│   ├── builder_engine.py        # Dependency and configuration resolver
│   └── package_generator.py     # Flashable ZIP & Magisk packager
├── devices/
│   ├── samsung/                 # Samsung profiles & AnyKernel ramdisk scripts
│   └── kernel-tree/             # Submodule: kali-nethunter-project kernels
├── apps/                        # Submodules for Android companion apps
│   ├── kali-nethunter-app
│   ├── kali-nethunter-terminal
│   ├── kali-nethunter-kex
│   └── kali-nethunter-store-client
├── scripts/
│   ├── debloat-samsung.sh       # Lightweight RAM & Knox optimizer
│   └── setup-usb-gadget.sh      # Linux ConfigFS USB gadget controller
├── tools/
│   ├── duckhunter/              # Rubber Ducky to Android HID compiler
│   ├── firmware/                # Wireless adapter firmware definitions
│   ├── wireless/                # Monitor mode & injection toolkit
│   └── bluetooth/               # Bluetooth LE reconnaissance
└── docs/                        # Installation & device manuals
```

---

## 📱 Adding a New Device Profile

To add support for a new smartphone, add its hardware specifications to `config/devices.json`:

```json
"oneplus_7_pro": {
  "model_name": "OnePlus 7 Pro",
  "brand": "OnePlus",
  "arch": "arm64",
  "codename": "guacamole",
  "supported_releases": ["10", "11", "12"],
  "kernel_source": "upstream_generic",
  "anykernel": true,
  "ramdisk_patch": "standard",
  "debloat_profile": "oxygenos",
  "notes": "Full kernel injection and HID support supported"
}
```

Verify your new configuration by running:
```bash
python3 build.py --device oneplus_7_pro --release 11 --dry-run
```

---

## 🔄 Managing Git Submodules

ADos tracks the latest official Kali NetHunter components. To sync or update all submodules to the latest upstream revisions:

```bash
# Update all submodules to latest remote commits
git submodule update --remote --merge
```

To add a new component repository:
```bash
git submodule add https://gitlab.com/kalilinux/nethunter/new-repo.git path/to/component
```

---

## ☕ Building Companion Android Apps from Source

If you want to modify or rebuild the Android APKs (e.g. NetHunter App or NetHunter Terminal) from source code:

1. Ensure you have **Android Studio** or Android SDK command-line tools and **OpenJDK 17** installed.
2. Navigate to the app directory:
   ```bash
   cd apps/kali-nethunter-app
   ```
3. Build the release APK with Gradle:
   ```bash
   ./gradlew assembleRelease
   ```
4. The compiled APK will be generated in `app/build/outputs/apk/release/`.

---

## 🐧 Generating Custom Kali ARM Rootfs Tarballs

The `core/arm-rootfs` directory points to `kalilinux/build-scripts/kali-arm`. You can build a completely custom Kali Linux rootfs using Debian live-build / debos:

```bash
cd core/arm-rootfs
# Build minimal arm64 rootfs recipe
sudo ./build-rootfs.sh arm64 minimal
```

This packages a lightweight rootfs tarball containing exactly the security tools you select.

---

## 🧪 Running the Test Suite

ADos includes an automated unit test suite covering device profiles, CLI parsers, DuckHunter compiler, and Docker configurations:

```bash
# Run all tests using Python standard library
python3 -m unittest discover -s tests
```
