#!/system/bin/sh
# ADos USB Gadget ConfigFS Controller for Android / Samsung Kernels
# Configures USB Keyboard/Mouse HID (/dev/hidg0) and Network interfaces for BadUSB & DuckHunter

GADGET_DIR="/config/usb_gadget/g1"

echo "=========================================================="
echo "    ADos USB Gadget & BadUSB HID Controller"
echo "=========================================================="

# Check root permissions
if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Error: Root permissions required."
    exit 1
fi

# 1. Mount configfs if not already mounted
if [ ! -d "/config/usb_gadget" ]; then
    echo "[-] Mounting /config filesystem..."
    mount -t configfs none /config || exit 1
fi

if [ ! -d "$GADGET_DIR" ]; then
    mkdir -p "$GADGET_DIR"
    cd "$GADGET_DIR" || exit 1
    
    # Generic USB Identifiers
    echo 0x1d6b > idVendor   # Linux Foundation
    echo 0x0104 > idProduct  # Multifunction Composite Gadget
    echo 0x0100 > bcdDevice
    echo 0x0200 > bcdUSB
    
    mkdir -p strings/0x409
    echo "0123456789" > strings/0x409/serialnumber
    echo "ADos Security" > strings/0x409/manufacturer
    echo "ADos HID Interface" > strings/0x409/product
fi

# 2. Setup HID Keyboard Descriptor
HID_FUNCTION="$GADGET_DIR/functions/hid.usb0"
if [ ! -d "$HID_FUNCTION" ]; then
    echo "[-] Initializing HID Keyboard endpoint..."
    mkdir -p "$HID_FUNCTION"
    echo 1 > "$HID_FUNCTION/subclass"  # Boot Interface
    echo 1 > "$HID_FUNCTION/protocol"  # Keyboard
    echo 8 > "$HID_FUNCTION/report_length"
    
    # Standard 8-byte HID keyboard report descriptor
    printf '\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x01\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0' > "$HID_FUNCTION/report_desc"
fi

# Link configuration
CONFIG_DIR="$GADGET_DIR/configs/c.1"
mkdir -p "$CONFIG_DIR/strings/0x409"
echo "Config 1: ADos HID" > "$CONFIG_DIR/strings/0x409/configuration"
echo 250 > "$CONFIG_DIR/MaxPower"

if [ ! -L "$CONFIG_DIR/hid.usb0" ]; then
    ln -s "$HID_FUNCTION" "$CONFIG_DIR/hid.usb0"
fi

# Bind to UDC driver if available
UDC_DEVICE=$(ls /sys/class/udc | head -n 1)
if [ -n "$UDC_DEVICE" ]; then
    echo "[-] Binding USB Gadget to UDC: $UDC_DEVICE"
    echo "$UDC_DEVICE" > "$GADGET_DIR/UDC"
fi

# Set permissions for hidg0 device node
if [ -e "/dev/hidg0" ]; then
    chmod 0666 /dev/hidg0
    echo "[+] /dev/hidg0 created successfully! BadUSB and DuckHunter are ready."
else
    echo "[!] Note: /dev/hidg0 will become active when connected to a host computer."
fi

exit 0
