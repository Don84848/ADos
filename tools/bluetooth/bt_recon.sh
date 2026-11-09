#!/bin/sh
# ADos Bluetooth & BLE Reconnaissance Utility

echo "=========================================================="
echo "    ADos Bluetooth & BLE Security Recon"
echo "=========================================================="

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Error: Root privileges required."
    exit 1
fi

echo "[*] Checking Bluetooth controller..."
if ! command -v hciconfig >/dev/null 2>&1; then
    echo "[!] hciconfig not found. Please run within ADos NetHunter chroot."
    exit 1
fi

BT_DEV=$(hciconfig | grep -o '^hci[0-9]*' | head -n 1)

if [ -z "$BT_DEV" ]; then
    echo "[!] No Bluetooth adapters detected. Bring hci0 up:"
    echo "    rfkill unblock bluetooth && hciconfig hci0 up"
    exit 1
fi

echo "[+] Using Bluetooth adapter: $BT_DEV"
hciconfig "$BT_DEV" up
hciconfig "$BT_DEV" piscan

echo "\n[*] Scanning for nearby Classic Bluetooth devices (10s)..."
hcitool scan

echo "\n[*] Scanning for nearby BLE (Bluetooth Low Energy) devices..."
echo "[Tip] Press Ctrl+C to stop BLE scan."
hcitool lescan

exit 0
