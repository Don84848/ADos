#!/bin/bash
# ADos Hacking Tools Installer & Updater
# Installs curated pentesting arsenals inside Kali NetHunter Chroot or individual tools on-demand

echo "=========================================================="
echo "    ADos Mobile Cybersecurity Tools Installer"
echo "=========================================================="

# Check for single tool flag
if [ "$1" = "--tool" ] || [ "$1" = "-t" ]; then
    TOOL_NAME="$2"
    if [ -z "$TOOL_NAME" ]; then
        echo "[!] Error: No tool specified for --tool flag"
        exit 1
    fi
    echo "[*] Installing single tool on-demand: $TOOL_NAME"
    if [ "$(id -u)" -ne 0 ]; then
        echo "[!] Warning: Not running as root. Attempting user/python fallback..."
        python3 tools/tool_installer.py "$TOOL_NAME"
        exit $?
    fi
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y && apt-get install -y --no-install-recommends "$TOOL_NAME" || python3 tools/tool_installer.py "$TOOL_NAME"
    exit $?
fi

PROFILE="${1:-essential}"

echo "[*] Selected Arsenal Profile or Tool: $PROFILE"

# Ensure running as root for system package management
if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Not running as root. Attempting on-demand tool installation via Python resolver..."
    python3 tools/tool_installer.py "$PROFILE"
    exit $?
fi

export DEBIAN_FRONTEND=noninteractive

echo "[*] Updating Kali Linux package repositories..."
apt-get update -y

install_pkgs() {
    echo -e "\n[+] Installing: $*"
    apt-get install -y --no-install-recommends "$@"
}

case "$PROFILE" in
    wireless)
        install_pkgs aircrack-ng wifite hcxdumptool hcxtools mdk4 pixiewps reaver bully macchanger kismet iw wireless-tools
        ;;
    web)
        install_pkgs sqlmap gobuster ffuf nikto wpscan dirb commix whatweb curl nmap
        ;;
    network)
        install_pkgs nmap masscan zmap netdiscover arp-scan hping3 traceroute fping tcpdump
        ;;
    mitm)
        install_pkgs bettercap responder mitmproxy ettercap-text-only tcpdump dsniff tshark
        ;;
    passwords)
        install_pkgs john hydra medusa hashcat crowbar wordlists crunch
        # Decompress rockyou wordlist if present
        if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
            echo "[-] Decompressing rockyou.txt wordlist..."
            gzip -d /usr/share/wordlists/rockyou.txt.gz
        fi
        ;;
    redteam|full)
        echo "[*] Installing Complete Red Team Arsenal..."
        install_pkgs nmap masscan netdiscover arp-scan \
                     aircrack-ng wifite hcxdumptool hcxtools mdk4 pixiewps reaver macchanger \
                     bettercap responder mitmproxy tcpdump \
                     sqlmap gobuster ffuf nikto wpscan dirb \
                     metasploit-framework exploitdb msfpc netcat-traditional socat \
                     john hydra hashcat wordlists
        
        if [ "$PROFILE" = "full" ]; then
            install_pkgs bluez btscanner rtl-sdr hackrf
        fi

        if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
            gzip -d /usr/share/wordlists/rockyou.txt.gz
        fi
        ;;
    john|sqlmap|nmap|hydra|hashcat|aircrack-ng|bettercap|gobuster|nikto|wfuzz|netcat|adb|masscan)
        echo "[*] Installing specific tool on-demand: $PROFILE"
        install_pkgs "$PROFILE" || python3 tools/tool_installer.py "$PROFILE"
        ;;
    essential|*)
        echo "[*] Installing Essential Mobile Arsenal..."
        install_pkgs nmap masscan aircrack-ng wifite hcxdumptool macchanger metasploit-framework netcat-traditional sqlmap
        ;;
esac

# Initialize Metasploit Database if installed
if command -v msfdb >/dev/null 2>&1; then
    echo "[-] Initializing Metasploit database..."
    msfdb init >/dev/null 2>&1 || true
fi

echo -e "\n=========================================================="
echo "[+] Tools installation complete!"
echo "[+] Launch the mobile menu anytime by typing: ados-menu"
echo "=========================================================="
exit 0
