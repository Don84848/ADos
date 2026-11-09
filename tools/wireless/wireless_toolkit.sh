#!/bin/sh
# ADos External Wi-Fi Manager & Wireless Toolkit
# Easily enables monitor mode, tests packet injection, and launches airodump

echo "=========================================================="
echo "    ADos Wireless Toolkit (OTG External Wi-Fi)"
echo "=========================================================="

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Error: Root privileges required."
    exit 1
fi

echo "[*] Detecting available wireless interfaces..."
INTERFACES=$(iwconfig 2>&1 | grep -o '^[a-zA-Z0-9]*' | grep -v 'lo')

if [ -z "$INTERFACES" ]; then
    echo "[!] No wireless interfaces found."
    echo "[Tip] Connect your USB Wi-Fi adapter (e.g. TP-Link TL-WN722N or Alfa AWUS036ACH) via OTG cable."
    exit 1
fi

echo "[+] Found wireless interfaces:"
echo "$INTERFACES"

# Prefer wlan1 (external OTG) over wlan0 (internal phone Wi-Fi)
TARGET_IFACE="wlan1"
if ! echo "$INTERFACES" | grep -q "wlan1"; then
    TARGET_IFACE=$(echo "$INTERFACES" | head -n 1)
fi

echo "\n[*] Selected interface: $TARGET_IFACE"
echo "[*] Stopping conflicting processes..."
airmon-ng check kill >/dev/null 2>&1

echo "[*] Putting $TARGET_IFACE into Monitor Mode..."
if command -v airmon-ng >/dev/null 2>&1; then
    airmon-ng start "$TARGET_IFACE"
    MON_IFACE="${TARGET_IFACE}mon"
else
    ip link set "$TARGET_IFACE" down
    iw dev "$TARGET_IFACE" set type monitor
    ip link set "$TARGET_IFACE" up
    MON_IFACE="$TARGET_IFACE"
fi

echo "[+] Interface $MON_IFACE is in Monitor Mode!"
echo "\n[*] Testing packet injection..."
if command -v aireplay-ng >/dev/null 2>&1; then
    aireplay-ng --test "$MON_IFACE"
else
    echo "[*] aireplay-ng not in current path (run inside ADos/NetHunter chroot for full suite)."
fi

echo "\n[+] Ready for security auditing. Launch airodump with:"
echo "    airodump-ng $MON_IFACE"
exit 0
