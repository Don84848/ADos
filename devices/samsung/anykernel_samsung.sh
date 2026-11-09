#!/sbin/sh
# AnyKernel3 Ramdisk Patcher for Samsung Galaxy Devices (ADos NetHunter)
# Disables Samsung Defex, TIMA, and Knox guard daemons; enables USB OTG & NetHunter chroot

OUTFD=$2
ui_print() { echo -e "ui_print $1\nui_print" > /proc/self/fd/$OUTFD; }

ui_print "=========================================="
ui_print " ADos Samsung Kernel Ramdisk Patcher"
ui_print " Disabling Samsung Defex & Security Daemons"
ui_print "=========================================="

RAMDISK_DIR="/tmp/anykernel/ramdisk"

if [ -d "$RAMDISK_DIR" ]; then
    cd "$RAMDISK_DIR" || exit 1
    
    # 1. Disable Samsung Defex daemon in init.rc
    if [ -f "init.rc" ]; then
        ui_print "[-] Patching init.rc to neutralize Samsung Defex..."
        sed -i 's/service defex /service defex_disabled /g' init.rc
        sed -i 's/start defex/stop defex/g' init.rc
        # Disable TIMA trustzone
        sed -i 's/service tima /service tima_disabled /g' init.rc
    fi

    # 2. Patch Samsung specific init scripts if present
    for init_script in init.samsung.rc init.samsung.bcmdhd.rc init.baseband.rc; do
        if [ -f "$init_script" ]; then
            ui_print "[-] Patching $init_script for permissive chroot operation..."
            sed -i 's/setenforce 1/setenforce 0/g' "$init_script"
            sed -i 's/start vaultkeeper/stop vaultkeeper/g' "$init_script"
            sed -i 's/start wvkprov/stop wvkprov/g' "$init_script"
        fi
    done

    # 3. Enable USB ConfigFS HID and Networking endpoints
    ui_print "[-] Enabling ConfigFS USB gadget support in ramdisk..."
    if [ -f "init.usb.configfs.rc" ]; then
        sed -i 's/write \/config\/usb_gadget\/g1\/UDC none/write \/config\/usb_gadget\/g1\/UDC none\n    chmod 0666 \/dev\/hidg0/g' init.usb.configfs.rc
    fi

    ui_print "[+] Samsung ramdisk patches applied successfully!"
else
    ui_print "[!] Ramdisk directory not found, skipping standalone ramdisk patch."
fi

exit 0
