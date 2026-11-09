# ADos Samsung Galaxy Setup & Optimization Guide

Samsung Galaxy devices (Galaxy S8/S9/S10/S20, Note 9/10, and A-series) make exceptional mobile cybersecurity platforms due to their powerful hardware, high-resolution screens, and USB 3.1 Type-C OTG support.

However, Samsung phones include proprietary security architectures (**Samsung Knox, VaultKeeper, Defex, and OneUI background services**) that require specific handling. This guide covers how to set up, patch, and debloat your Samsung phone for peak lightweight performance.

---

## ⚠️ Important Warnings About Samsung Devices

1. **Knox Warranty Void (0x1):** Unlocking the bootloader permanently trips the Samsung Knox hardware fuse from `0x0` to `0x1`. This permanently disables Samsung Pay and Samsung Pass (secure hardware storage).
2. **Exynos vs Snapdragon:**
   - **Exynos models (Global/International 'F', 'B', 'N' variants):** Easily bootloader unlocked and fully supported.
   - **Snapdragon models (International '0' variants, e.g. China/Hong Kong):** Unlockable bootloaders.
   - **Snapdragon North American Carrier models ('U', 'U1', 'W'):** Bootloaders are factory locked by US carriers and cannot be unlocked. Ensure you have an unlockable variant before proceeding.

---

## 🔓 Step 1: Unlocking the Samsung Bootloader

1. On your Samsung phone, go to **Settings** → **About phone** → **Software information**.
2. Tap **Build number** 7 times until Developer options are enabled.
3. Go back to **Settings** → **Developer options**.
4. Enable **OEM unlocking** and **USB debugging**.
5. Power off your phone.
6. Connect your phone to your PC with a USB cable while holding **Volume Down + Bixby** (or **Volume Down + Volume Up** on newer devices like S20/A52) to enter **Download Mode**.
7. Long press **Volume Up** to enter "Device Unlock Mode", then confirm bootloader unlock.
   *(Note: This will perform a factory reset. Backup your data first.)*

---

## ⚡ Step 2: Flashing Custom Recovery (TWRP) via Odin / Heimdall

1. Download the official TWRP `.tar` or `.img` build for your specific Galaxy model.
2. Download a patched `vbmeta.tar` (or `vbmeta.img`) to disable AVB (Android Verified Boot).
3. Put the phone into **Download Mode** again.
4. On Windows, launch **Odin v3.14.x**:
   - In the **AP** slot, select your `TWRP.tar`.
   - In the **USERDATA** or **CP** slot (depending on device), select `vbmeta_disabled.tar`.
   - In Odin Options, **uncheck Auto-Reboot**.
   - Click **Start**.
5. When Odin shows **PASS**, immediately press and hold **Volume Down + Power** to exit Download mode, and instantly switch to **Volume Up + Bixby + Power** to boot directly into TWRP Recovery.

---

## 🧹 Step 3: Making Samsung Lightweight (Debloating OneUI & Knox)

Stock Samsung OneUI runs over 100 background services (Knox telemetry, Bixby daemons, AR emoji engines, Facebook analytics, and Game Optimizing Service) that consume up to 2.5 GB of RAM and cause thermal throttling.

ADos includes an automated debloater that safely strips non-essential Samsung bloatware without breaking phone calls, Wi-Fi, camera, or audio.

### Running the Debloater:

#### Option A: Direct on Device (Root Terminal)
Open **NetHunter Terminal** or Termux as root and run:
```bash
su -c sh /data/ados/scripts/debloat-samsung.sh
```

#### Option B: Via ADB from your Computer
Connect the phone with USB debugging enabled:
```bash
adb shell sh /data/ados/scripts/debloat-samsung.sh
```

### What Gets Removed:
- **Bixby Suite:** `bixby.agent`, `bixby.service`, `bixby.wakeup`, `bixbyvision`
- **Knox Enterprise Daemons:** `knox.attestation`, `knox.cloudmdm`, `knox.containercore`
- **Game Throttlers:** `game.gos` (Game Optimizing Service that throttles CPU frequency), `game.gamehome`
- **Third-Party Bloat:** Facebook background app managers, telemetry agents, Netflix partners
- **Result:** ~40% background RAM reduction, faster tool compilation, longer battery life.

*(If you ever need to restore Samsung apps, run `sh debloat-samsung.sh --restore`)*

---

## 🛡️ Step 4: Neutralizing Samsung Defex Security Daemon

Samsung kernels contain a security daemon called **Defex** that monitors process execution and aggressively terminates unsigned binaries (such as custom chroot binaries, packet sniffing tools, and raw sockets).

ADos provides `devices/samsung/anykernel_samsung.sh` which automatically patches the ramdisk during the installation of ADos:
- Disables `service defex` in `init.rc`.
- Sets SELinux to permissive mode for the chroot subsystem.
- Disables `VaultKeeper` to prevent Knox from relocking the boot partition.

---

## 🎯 Device-Specific Notes

| Galaxy Model | Chipset | Key Recommendation |
| :--- | :--- | :--- |
| **Galaxy S9 / Note 9** | Exynos 9810 | Very stable NetHunter support. S-Pen functionality on Note 9 remains intact after debloating. |
| **Galaxy S10 / Note 10** | Exynos 9820 / 9825 | System-As-Root (SAR). Always boot using Magisk recovery key combo if using Magisk root. |
| **Galaxy S20 Series** | Exynos 990 | Dynamic partitions layout. Must flash `vbmeta.img` with `--disable-verity --disable-verification`. |
| **Galaxy A50 / A52** | Exynos 9610 / Snapdragon 720G | Excellent budget pentesting hardware. High battery capacity and USB OTG work out of the box. |
