#!/bin/bash
# ADos Mobile Interactive Pentest Dashboard
# Mobile-optimized terminal menu for touchscreen smartphones

clear
show_banner() {
cat << "EOF"
    ___    ____            
   /   |  / __ \____  _____
  / /| | / / / / __ \/ ___/
 / ___ |/ /_/ / /_/ (__  ) 
/_/  |_/_____/\____/____/  
======================================================
  ADos - Mobile Cybersecurity Operating System
  Interactive Offensive Security Dashboard
======================================================
EOF
}

while true; do
    show_banner
    echo " [1] Network Recon (Nmap & Host Discovery)"
    echo " [2] Wi-Fi Auditing & Monitor Mode (Wifite & Aircrack)"
    echo " [3] Man-in-the-Middle (Bettercap & Responder)"
    echo " [4] Web Vulnerability Scanner (SQLMap & Gobuster)"
    echo " [5] BadUSB & DuckHunter Payloads (/dev/hidg0)"
    echo " [6] Metasploit Framework Console (msfconsole)"
    echo " [7] NetHunter KeX (Graphical Desktop)"
    echo " [8] Install / Update Hacking Toolsets"
    echo " [0] Exit to Shell"
    echo "------------------------------------------------------"
    read -rp "Select an option [0-8]: " OPTION

    case "$OPTION" in
        1)
            echo "\n--- Network Recon ---"
            read -rp "Enter target IP or Subnet (e.g. 192.168.1.0/24): " TARGET
            if [ -n "$TARGET" ]; then
                nmap -sS -T4 -F "$TARGET"
            fi
            read -rp "Press Enter to return..." _
            ;;
        2)
            echo "\n--- Wi-Fi Auditing ---"
            if [ -f /data/ados/tools/wireless/wireless_toolkit.sh ]; then
                sh /data/ados/tools/wireless/wireless_toolkit.sh
            elif command -v wifite >/dev/null 2>&1; then
                wifite
            else
                echo "[!] Please run Option 8 to install wireless toolset."
            fi
            read -rp "Press Enter to return..." _
            ;;
        3)
            echo "\n--- Man-in-the-Middle ---"
            if command -v bettercap >/dev/null 2>&1; then
                bettercap
            else
                echo "[!] Bettercap not installed. Install via Option 8."
            fi
            read -rp "Press Enter to return..." _
            ;;
        4)
            echo "\n--- Web Vulnerability Scan ---"
            read -rp "Enter Target URL (e.g. http://example.com/item.php?id=1): " URL
            if [ -n "$URL" ]; then
                sqlmap -u "$URL" --batch --dbs
            fi
            read -rp "Press Enter to return..." _
            ;;
        5)
            echo "\n--- BadUSB & DuckHunter Execution ---"
            if [ -f /data/ados/scripts/setup-usb-gadget.sh ]; then
                sh /data/ados/scripts/setup-usb-gadget.sh
            fi
            echo "Available payloads:"
            ls -1 /data/ados/tools/duckhunter/payloads/ 2>/dev/null || ls -1 tools/duckhunter/payloads/
            read -rp "Enter payload name (e.g. recon.txt): " PNAME
            PAYLOAD_PATH="/data/ados/tools/duckhunter/payloads/$PNAME"
            if [ ! -f "$PAYLOAD_PATH" ]; then
                PAYLOAD_PATH="tools/duckhunter/payloads/$PNAME"
            fi
            if [ -f "$PAYLOAD_PATH" ]; then
                python3 tools/duckhunter/duckhunter.py "$PAYLOAD_PATH" run_payload.sh
                sh run_payload.sh
            fi
            read -rp "Press Enter to return..." _
            ;;
        6)
            echo "\n[*] Starting Metasploit Framework Console..."
            msfconsole
            ;;
        7)
            echo "\n--- NetHunter KeX Desktop Manager ---"
            echo "1) Start KeX Server"
            echo "2) Stop KeX Server"
            read -rp "Choose [1/2]: " KEX_OPT
            if [ "$KEX_OPT" = "1" ]; then
                kex start
            elif [ "$KEX_OPT" = "2" ]; then
                kex stop
            fi
            read -rp "Press Enter to return..." _
            ;;
        8)
            echo "\n--- Install / Update Hacking Toolsets ---"
            echo "Profiles: essential, wireless, web, mitm, passwords, redteam, full"
            read -rp "Enter profile name [default: essential]: " TPROFILE
            TPROFILE=${TPROFILE:-essential}
            if [ -f /data/ados/scripts/install-tools.sh ]; then
                bash /data/ados/scripts/install-tools.sh "$TPROFILE"
            elif [ -f scripts/install-tools.sh ]; then
                bash scripts/install-tools.sh "$TPROFILE"
            fi
            read -rp "Press Enter to return..." _
            ;;
        0)
            echo "[*] Exiting ADos Dashboard."
            exit 0
            ;;
        *)
            echo "[!] Invalid selection."
            sleep 1
            ;;
    esac
done
