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

## ⚡ Step 3: Flashing the ADos Package

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

## 🔧 Troubleshooting

- **SELinux Enforcing Issues:** If the chroot fails to execute or external modules fail to load, open terminal and run `su -c setenforce 0`.
- **Chroot Not Found:** Open NetHunter App → Kali Chroot Manager → Check status. Ensure it is located in `/data/local/nhsystem/kali-arm64`.
- **Samsung Knox Blocking:** If running a Samsung device, make sure you ran `scripts/debloat-samsung.sh` to remove Knox VaultKeeper and background telemetry daemons. Refer to [Samsung Guide](SAMSUNG_GUIDE.md).
