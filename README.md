# ADos (Advanced Defensive/Offensive OS)

<p align="center">
  <b>Unified Open-Source Mobile Cybersecurity Operating System & Build Orchestrator</b><br>
  <i>Transform your Android smartphone (with specialized Samsung Galaxy support) into a high-performance, lightweight mobile penetration testing workstation.</i>
</p>

---

## 🚀 Overview

**ADos** consolidates the entire **Kali NetHunter** mobile ecosystem into a single, unified open-source repository and automated build system. 

Instead of juggling 12 disparate GitLab repositories with differing build pipelines, ADos provides a single entrypoint:

```bash
python3 build.py --device [phone_model] --release [os_version]
```

### ✨ Key Features
- **All-in-One NetHunter Suite:** Bundles the NetHunter App UI, Terminal, Desktop KeX, App Store client, Chroot installer, DuckHunter BadUSB tools, and external Wi-Fi firmware patches.
- **Dedicated Samsung Phone Optimization:** Engineered specifically for Samsung Galaxy phones (S9, S10, S20, Note 9, Note 10, A50, A52). Includes AnyKernel3 ramdisk patches that bypass Samsung Defex security daemons.
- **Lightweight Mobile Performance:** Includes automated OneUI/Knox debloater scripts (`scripts/debloat-samsung.sh`) and nano/minimal chroot profiles that free up **>1.5 GB of RAM** and prevent thermal throttling while running intensive security tools (Nmap, Metasploit, Aircrack-ng).
- **External Wi-Fi & Packet Injection:** Full support for external USB Wi-Fi dongles (Atheros AR9271, Realtek RTL8812AU, Ralink RT3070) via USB OTG.
- **BadUSB & DuckHunter HID:** Execute automated keystroke injection payloads over USB directly from the phone.
- **Curated Hacking Toolsets & Mobile Dashboard (`ados-menu`):** Instant access to Wi-Fi auditing (Aircrack/Wifite), MITM (Bettercap/Responder), Network Discovery (Nmap/Masscan), Web Exploitation (SQLMap/Gobuster), and Metasploit directly from a mobile-friendly touchscreen menu.
- **Cross-Platform Containerized Builds:** Pre-configured `Dockerfile` and `docker-compose.yml` to build flashable packages on Windows, Linux, or macOS.

---

## 📦 Consolidated Repositories Matrix

ADos combines and manages the following official Kali NetHunter repositories:

| Component | Upstream GitLab Repository | Role in ADos |
| :--- | :--- | :--- |
| **Main Installer & Builder** | [`kalilinux/nethunter/build-scripts/kali-nethunter-installer`](https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-installer) | Core packaging engine & flashable zip generator (`core/installer`) |
| **Mobile Control App** | [`kalilinux/nethunter/apps/kali-nethunter-app`](https://gitlab.com/kalilinux/nethunter/apps/kali-nethunter-app) | Main Android management application (`apps/kali-nethunter-app`) |
| **Custom Terminal App** | [`kalilinux/nethunter/apps/kali-nethunter-terminal`](https://gitlab.com/kalilinux/nethunter/apps/kali-nethunter-terminal) | Kali terminal emulator client (`apps/kali-nethunter-terminal`) |
| **Desktop KeX Extension** | [`kalilinux/nethunter/apps/kali-nethunter-kex`](https://gitlab.com/kalilinux/nethunter/apps/kali-nethunter-kex) | Desktop-on-Mobile graphical VNC engine (`apps/kali-nethunter-kex`) |
| **Dedicated Store Client** | [`kalilinux/nethunter/apps/kali-nethunter-store-client`](https://gitlab.com/kalilinux/nethunter/apps/kali-nethunter-store-client) | F-Droid security tools package repository (`apps/kali-nethunter-store-client`) |
| **Device Kernel Trees** | [`kalilinux/nethunter/build-scripts/kali-nethunter-project`](https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-project) | Device kernel configs and patches (`devices/kernel-tree`) |
| **ARM Rootfs Recipes** | [`kalilinux/build-scripts/kali-arm`](https://gitlab.com/kalilinux/build-scripts/kali-arm) | Kali Linux ARM core chroot generation recipes (`core/arm-rootfs`) |
| **Assets & Wallpapers** | NetHunter installer assets | Visual branding, wallpapers, and boot animations |
| **DuckHunter HID** | NetHunter BadUSB utilities | Rubber Ducky payload compiler & HID emulator (`tools/duckhunter`) |
| **Bluetooth/NFC Tools** | NetHunter wireless utilities | Bluetooth LE scanner & sniffing helper scripts (`tools/bluetooth`) |
| **External Wi-Fi Firmware** | NetHunter firmware patches | Firmware drivers for AR9271, RTL8812AU, RT3070 (`tools/firmware`) |
| **Documentation & Guides** | NetHunter official docs | Step-by-step flashing & hardware manuals (`docs/`) |

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone --recurse-submodules https://github.com/your-username/ADos.git
cd ADos
```

*(If you already cloned without submodules, run `python3 build.py --init-submodules`)*

### 2. Check Supported Devices
```bash
python3 build.py --list-devices
```

Supported device presets include:
- `samsung_s9` (Galaxy S9 / S9+)
- `samsung_s10` (Galaxy S10 / S10e / S10+)
- `samsung_s20` (Galaxy S20 / S20+ / S20 Ultra)
- `samsung_note9` (Galaxy Note 9)
- `samsung_note10` (Galaxy Note 10 / Note 10+)
- `samsung_a50` (Galaxy A50)
- `samsung_a52` (Galaxy A52 / A52s 5G)
- `generic_arm64` (All Generic 64-bit ARM Android devices / GSI)
- `generic_armhf` (Generic 32-bit ARM devices)

### 3. Build Your Package
Build a lightweight package for a Samsung Galaxy S10 with the Red Team hacking arsenal:
```bash
python3 build.py --device samsung_s10 --release 11 --rootfs minimal --tools redteam --debloat-samsung
```

#### Available Toolset Profiles (`--tools`):
- `essential`: Nmap, Masscan, Aircrack-ng, Wifite, Metasploit, SQLMap, Netcat (Default)
- `wireless`: Full Wi-Fi arsenal (Aircrack, Wifite, Hcxdumptool, Mdk4, Reaver, Bully, Kismet)
- `web`: Web penetration testing (SQLMap, Gobuster, FFuF, Nikto, WPScan, Commix, WhatWeb)
- `redteam`: Full offensive suite (Network, Wi-Fi, MITM, Web, Metasploit, John, Hydra, Hashcat)
- `full`: Complete Kali toolkit including Software Defined Radio (RTL-SDR, HackRF) and Bluetooth

---

## 📱 Mobile Interactive Pentest Dashboard (`ados-menu`)

Inside the phone's terminal, simply type `ados-menu` to launch the touchscreen-friendly dashboard:

```text
    ___    ____            
   /   |  / __ \____  _____
  / /| | / / / / __ \/ ___/
 / ___ |/ /_/ / /_/ (__  ) 
/_/  |_/_____/\____/____/  
======================================================
  ADos - Mobile Cybersecurity Operating System
  Interactive Offensive Security Dashboard
======================================================
 [1] Network Recon (Nmap & Host Discovery)
 [2] Wi-Fi Auditing & Monitor Mode (Wifite & Aircrack)
 [3] Man-in-the-Middle (Bettercap & Responder)
 [4] Web Vulnerability Scanner (SQLMap & Gobuster)
 [5] BadUSB & DuckHunter Payloads (/dev/hidg0)
 [6] Metasploit Framework Console (msfconsole)
 [7] NetHunter KeX (Graphical Desktop)
 [8] Install / Update Hacking Toolsets
 [0] Exit to Shell
```

Or for a generic ARM64 phone running Android 13:
```bash
python3 build.py --device generic_arm64 --release 13 --type twrp
```

The output flashable ZIP and its SHA256 checksum will be generated in `output/`.

---

## 🐳 Building with Docker (Zero Setup)

You don't need to configure Android SDKs, cross-compilers, or Linux packages on your host machine.

- **Windows:**
  ```cmd
  run_docker.bat --device samsung_s10 --release 11 --debloat-samsung
  ```
- **Linux / macOS:**
  ```bash
  chmod +x run_docker.sh
  ./run_docker.sh --device samsung_s10 --release 11 --debloat-samsung
  ```

---

## 📖 In-Depth Installation & Device Guides

- **[Complete Installation Guide](docs/INSTALL_GUIDE.md):** Step-by-step instructions for unlocking bootloaders, flashing TWRP/OrangeFox, rooting with Magisk, installing ADos packages, configuring the Kali chroot, and running the KeX desktop GUI.
- **[Samsung Galaxy Setup & Optimization Guide](docs/SAMSUNG_GUIDE.md):** Dedicated guide for Samsung owners: Odin flashing, Knox mitigation, vbmeta disabling, RAM debloating, and Exynos/Snapdragon tips.
- **[Developer & Porting Guide](docs/DEVELOPER_GUIDE.md):** Learn how to add new device profiles, customize AnyKernel3 scripts, and build companion APKs from source.

---

## ⚖️ License & Credits

- Licensed under the **GNU General Public License v3.0 (GPLv3)**.
- Based on the open-source engineering of **OffSec / Kali Linux NetHunter** project.
