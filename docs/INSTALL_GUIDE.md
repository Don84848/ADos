# ADos Full Installation & Setup Guide

This guide walks you through transforming your Android smartphone into a complete cybersecurity workstation with **ADos (NetHunter)**.

---

## 📋 Prerequisites

Before starting, ensure you have:
1. **An Android Smartphone** with an unlockable bootloader (e.g. Samsung Galaxy S/Note/A series, Xiaomi, OnePlus, Google Pixel, or generic ARM64 device).
2. **A PC** (Windows, Linux, or macOS) with ADB & Fastboot tools installed.
3. **USB Cable & USB OTG Adapter** (for external Wi-Fi card or USB storage).
4. **Custom Recovery** (TWRP / OrangeFox) or **Magisk Root** installed on the device.
5. **At least 10–15 GB of free internal storage** on your phone (for the Kali Linux chroot and pentest toolsets).

---

## 🛠️ Step 1: Build Your ADos Package

On your computer, clone the ADos repository and run the unified builder:

```bash
# Clone the repository
git clone --recurse-submodules https://github.com/your-username/ADos.git
cd ADos

# Check supported devices
python3 build.py --list-devices

# Build the package for your device and Android version
# (Example: Samsung Galaxy S10 on Android 11 with minimal lightweight rootfs)
python3 build.py --device samsung_s10 --release 11 --rootfs minimal --debloat-samsung
```

*(If you are on Windows and don't have Python or build tools configured, simply run `run_docker.bat --device samsung_s10 --release 11`)*

The builder creates a flashable ZIP file in the `output/` folder, for example:
`output/ADos-samsung_s10-android11-minimal-twrp.zip`.

---

## 📲 Step 2: Transfer the Package to Your Phone

Connect your phone to your PC via USB and copy the generated ZIP:

```bash
adb push output/ADos-*.zip /sdcard/
```

Alternatively, copy the ZIP onto a USB flash drive and connect it via USB OTG.

---

## 🧹 How to Completely Delete the Current OS & Install Fresh (NO TERMUX)

> [!IMPORTANT]
> **NO TERMUX REQUIRED:** ADos does NOT use Termux. Termux runs as an unprivileged Android user app in a restricted sandbox. ADos is a **native system-level OS installation** with full root access, kernel injection, and native NetHunter terminal.

Follow these steps to completely wipe your current stock phone OS and install the clean cybersecurity OS from scratch:

### 1. Boot into Custom Recovery (TWRP or OrangeFox)
- Power off your phone completely.
- Press and hold your recovery key combination:
  - **Samsung (S9/S10/Note9/Note10):** Hold **Volume Up + Bixby + Power**
  - **Samsung (S20/A52/modern):** Connect to PC via USB cable, hold **Volume Up + Power**
  - **Google Pixel / Xiaomi / OnePlus:** Hold **Volume Down + Power** (or **Volume Up + Power**)

### 2. Completely Format & Delete the Existing OS
1. In TWRP, tap **Wipe**.
2. Tap **Format Data** → Type `yes` and press Enter. *(This decrypts the partition and wipes old user locks).*
3. Go back to **Wipe** → Tap **Advanced Wipe**.
4. Check the following partitions to **completely delete the existing OS**:
   - ✅ **Dalvik / ART Cache**
   - ✅ **Cache**
   - ✅ **System** *(This purges the current Samsung / Android OS entirely)*
   - ✅ **Vendor** *(Purges old manufacturer framework files)*
   - ✅ **Data**
   > [!CAUTION]
   > Do **NOT** check *Internal Storage* or *MicroSD / USB OTG* if your install zips are saved there.
5. Swipe the slider: **Swipe to Wipe**.
6. Your old OS is now completely erased from the phone.

---

### 3. Flash the New Clean System Image & ADos
There are two ways to flash the fresh OS:

#### Method 1: Using USB OTG or MicroSD Card (Recommended)
1. In TWRP, tap **Install**.
2. Tap **Select Storage** → Choose **Micro SD card** or **USB OTG**.
3. **Flash Clean Base ROM:** Select your clean AOSP / LineageOS / NetHunter Base ROM zip → **Swipe to confirm flash**.
4. **Flash Root:** Select `Magisk.zip` (or KernelSU) → **Swipe to confirm flash**.
5. **Flash ADos:** Select `ADos-[device]-android[version]-[rootfs]-twrp.zip` → **Swipe to confirm flash**.
6. Tap **Reboot System**.

#### Method 2: ADB Sideload from PC (If phone storage is wiped)
If your phone storage is empty, flash directly from your computer terminal over USB:
1. In TWRP, go to **Advanced** → **ADB Sideload** → Swipe to start sideload.
2. On your PC terminal, run:
   ```bash
   # 1. Sideload Base OS (e.g. LineageOS)
   adb sideload lineage-os-base.zip

   # 2. Sideload Root
   adb sideload Magisk-v27.0.zip

   # 3. Sideload ADos
   adb sideload output/ADos-samsung_s10-android11-minimal-twrp.zip
   ```
3. Tap **Reboot System** on your phone.

---

### 4. First Boot & Native Zero-Termux Operation
1. The phone will boot into the fresh, lightweight system.
2. Complete the initial basic setup (skip Google account setup for maximum privacy).
3. Open the pre-installed **NetHunter App** (granted root automatically by Magisk).
4. Open the pre-installed **NetHunter Terminal** (native Kali shell with full root `/dev/` access, zero Termux needed).
5. All tools (`nmap`, `metasploit`, `aircrack-ng`, `wireshark`, `kex`) run natively through the Kali chroot!

---

### Method A: Flashing via TWRP / OrangeFox Recovery (Recommended)
1. Turn off your phone.
2. Boot into Recovery mode (e.g., hold **Volume Up + Bixby + Power** on Samsung, or **Volume Up + Power** on other devices).
3. In TWRP, tap **Install**.
4. Navigate to `/sdcard/` and select your `ADos-*.zip` file.
5. Swipe to confirm flash.
6. Once installation completes, tap **Reboot System**.

### Method B: Installing via Magisk App
If you built the package using `--type magisk`:
1. Open the **Magisk App** on your phone.
2. Navigate to the **Modules** tab.
3. Tap **Install from storage** and select the ADos zip.
4. Reboot your phone after installation completes.

---

## 🛡️ Step 4: NetHunter Companion Apps Setup

After your phone reboots, you will see the Kali NetHunter suite installed:
- **NetHunter App (Manager)**
- **NetHunter Terminal**
- **NetHunter KeX (VNC Desktop)**
- **NetHunter Store**

1. Launch the **NetHunter App**.
2. Grant **Superuser (Root) Permissions** when prompted by Magisk.
3. Grant storage and terminal permissions.
4. If prompted to install or initialize Chroot, select **Kali Chroot Manager** → **Install Kali Chroot** → **Download Latest / Use Staged Rootfs**.

---

## 🖥️ Step 5: Launching NetHunter KeX (Desktop GUI on Mobile)

NetHunter KeX gives you a full Kali Linux desktop environment (XFCE) running directly on your phone's screen:

1. Open the **NetHunter App** and navigate to the **KeX Manager** tab.
2. Tap **Setup KeX Password** and set a password of your choice (e.g. `kali123`).
3. Tap **Start KeX Server**.
4. Open the **NetHunter KeX App**.
5. Leave the host as `127.0.0.1` and port as `5901`. Enter your password.
6. Tap **Connect**!
7. You now have a full Kali desktop with terminal, Metasploit, Wireshark, Burp Suite, and graphical penetration testing applications right on your phone!

---

## 📡 Step 6: External Wi-Fi Card & Monitor Mode Setup

To perform wireless auditing (WPA/WPA2 handshakes, deauthentication, packet injection):

1. Connect your external USB Wi-Fi dongle (e.g. **Atheros AR9271 / TP-Link TL-WN722N v1** or **Alfa AWUS036ACH**) to your phone using a USB OTG adapter.
2. Open **NetHunter Terminal** and choose **KALI**.
3. Run the ADos wireless toolkit:
   ```bash
   sh /data/ados/tools/wireless/wireless_toolkit.sh
   ```
4. Your external adapter will be automatically detected and switched into **Monitor Mode** (`wlan1mon`).
5. Launch a live wireless network scan:
   ```bash
   airodump-ng wlan1mon
   ```

---

## 🦆 Step 7: DuckHunter (BadUSB HID Attacks)

ADos includes DuckHunter, allowing your phone to act as an automated USB Rubber Ducky keyboard:

1. Connect your phone via USB cable to a target PC or test machine.
2. In NetHunter Terminal (as root):
   ```bash
   # Initialize USB HID Gadget
   sh /data/ados/scripts/setup-usb-gadget.sh
   ```
3. Compile and execute any DuckyScript payload:
   ```bash
   python3 /data/ados/tools/duckhunter/duckhunter.py /data/ados/tools/duckhunter/payloads/recon.txt run.sh
   sh run.sh
   ```
4. Your phone instantly types out the automated payload on the target machine in milliseconds!

---

## 🎯 Step 8: Launching the Mobile Dashboard & Installing More Tools

To easily run tools on your touchscreen without typing complex commands, open **NetHunter Terminal** and type:
```bash
ados-menu
```

This opens the interactive menu allowing one-tap launching of:
- **Nmap Network Scans**
- **Wifite & Aircrack Wi-Fi Audits**
- **Bettercap & Responder MITM Attacks**
- **SQLMap Web Vulnerability Scans**
- **BadUSB Payloads**
- **Metasploit Console**

### Installing Additional Toolsets On Demand:
To install more specialized tools directly inside the Kali Chroot:
```bash
# Install wireless hacking tools (Wifite, Aircrack, Kismet, Mdk4)
bash /data/ados/scripts/install-tools.sh wireless

# Install web app hacking tools (SQLMap, Gobuster, Nikto, WPScan, FFuF)
bash /data/ados/scripts/install-tools.sh web

# Install full Red Team offensive arsenal
bash /data/ados/scripts/install-tools.sh redteam
```

---

## 🔧 Troubleshooting

- **SELinux Enforcing Issues:** If the chroot fails to execute or external modules fail to load, open terminal and run `su -c setenforce 0`.
- **Chroot Not Found:** Open NetHunter App → Kali Chroot Manager → Check status. Ensure it is located in `/data/local/nhsystem/kali-arm64`.
- **Samsung Knox Blocking:** If running a Samsung device, make sure you ran `scripts/debloat-samsung.sh` to remove Knox VaultKeeper and background telemetry daemons. Refer to [Samsung Guide](SAMSUNG_GUIDE.md).
