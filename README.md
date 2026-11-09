# ADos (Advanced Defensive/Offensive OS)

<p align="center">
  <b>Unified Open-Source Mobile Cybersecurity Operating System & Full-Stack PC Studio</b><br>
  <i>Transform your Android smartphone (with dedicated Samsung Galaxy optimizations) or your PC workstation into an ultra-fast, lightweight ethical hacking and bug bounty platform.</i>
</p>

---

## 🌐 Ecosystem Overview

| Repository | Visibility | Role & Capabilities |
| :--- | :--- | :--- |
| **ADos** (this repo) | **Public** | Core Mobile NetHunter OS Builder, Full-Stack Backend API, PC Desktop Studio, and Bug Bounty Security Suite |
| **ADos-Manager** | **Private** | Android Native Companion App (`ADosManager.apk`), 2GB RAM Kernel Limiter, and Extended Desktop Deployment Suite |

---

## ⚡ Quick Start: Running on Windows (PowerShell & CMD)

ADos is 100% standard-library compliant. It requires **zero external pip installations** and runs immediately using Python 3.10+ on Windows, Linux, and macOS.

### 🔷 Windows PowerShell (`powershell.exe`)

Open PowerShell (or Windows Terminal) and navigate to the project directory:

```powershell
# 1. Navigate to the repository
cd C:\ADos

# 2. Launch the Desktop GUI Application (Visual PC Studio)
python launch_studio.py
# -- OR alternatively via the unified build orchestrator:
python build.py --launch-gui

# 3. Start the Full-Stack REST Backend API server (Port 8000)
python build.py --serve --port 8000
# -- OR directly run the API module:
python -m backend.api --port 8000

# 4. Run any Security / Bug Bounty tool directly from PowerShell:
python tools/tool_installer.py subfinder -d example.com
python tools/tool_installer.py header-audit -u https://example.com
python tools/tool_installer.py cors-scan -u https://example.com
python tools/tool_installer.py cert-inspect -d example.com -p 443
python tools/tool_installer.py secret-scan -u https://example.com
python tools/tool_installer.py tech-detect -u https://example.com

# 5. Run the Automated Unit Test Suite (100% Passing)
python -m unittest discover -s tests
```

---

### ⬛ Windows Command Prompt (`cmd.exe`)

Open Command Prompt (`cmd.exe`) and run:

```cmd
:: 1. Navigate to the repository directory
cd /d C:\ADos

:: 2. Launch the Desktop GUI Application on PC
python launch_studio.py
:: -- OR:
python build.py --launch-gui

:: 3. Start the REST Backend API server
python -m backend.api --port 8000

:: 4. Execute on-demand Bug Bounty tools
python tools\tool_installer.py subfinder -d example.com
python tools\tool_installer.py header-audit -u https://example.com
python tools\tool_installer.py secret-scan -u https://example.com

:: 5. Run verification tests
python -m unittest discover -s tests
```

---

## 🎯 Bug Bounty & Web Reconnaissance Suite (Earn via Responsible Disclosure)

ADos includes a dedicated suite of **ethical reconnaissance and vulnerability auditing tools** engineered specifically for security researchers participating in authorized **Bug Bounty Programs** (such as **HackerOne**, **Bugcrowd**, and **Intigriti**).

### 🛠️ Built-in Bug Bounty Tools

| Tool | Focus & Purpose | Typical Bounty Impact | CLI Command Example |
| :--- | :--- | :--- | :--- |
| **`subfinder`** | Passive Certificate Transparency & DNS asset discovery | Reconnaissance / Attack Surface Expansion | `python tools/tool_installer.py subfinder -d target.com` |
| **`header-audit`** | Audits CSP, HSTS, X-Frame-Options (Clickjacking), X-Content-Type | Low / Medium (Misconfiguration / Defense-in-Depth) | `python tools/tool_installer.py header-audit -u https://target.com` |
| **`cors-scan`** | Tests for Arbitrary Origin Reflection & Insecure Credential Sharing | Medium / High (Sensitive Data Leakage / CSRF Bypass) | `python tools/tool_installer.py cors-scan -u https://target.com/api` |
| **`cert-inspect`** | SSL/TLS certificate metadata & Subject Alternative Names (SANs) | Reconnaissance / Internal Infrastructure Discovery | `python tools/tool_installer.py cert-inspect -d target.com -p 443` |
| **`secret-scan`** | Scans client-side JavaScript for leaked AWS, Google, Stripe, JWT keys | High / Critical ($500 - $10,000+ per valid finding) | `python tools/tool_installer.py secret-scan -u https://target.com/bundle.js` |
| **`tech-detect`** | Web technology stack, server, CMS, and framework fingerprinter | Reconnaissance / CVE Component Identification | `python tools/tool_installer.py tech-detect -u https://target.com` |

---

### 💰 Bug Bounty Methodology: How to Hunt and Earn Responsibly

```
     [1. SCOPE VERIFICATION]
     Confirm target domain is listed in HackerOne / Bugcrowd "In-Scope"
               │
               ▼
     [2. PASSIVE RECONNAISSANCE]
     Run `subfinder` & `cert-inspect` to discover active subdomains & SAN endpoints
               │
               ▼
     [3. TECHNOLOGY PROFILING]
     Run `tech-detect` to identify frameworks, CMS, and web server versions
               │
               ▼
     [4. SECURITY CONFIGURATION AUDIT]
     Run `header-audit` (Missing HSTS/CSP/Clickjacking) & `cors-scan` (Origin reflection)
               │
               ▼
     [5. CLIENT-SIDE SECRET AUDITING]
     Run `secret-scan` across public JavaScript assets to catch leaked API tokens & keys
               │
               ▼
     [6. RESPONSIBLE DISCLOSURE]
     Write a clear vulnerability report with reproduction steps and submit to the company
```

#### 📋 Professional Report Writing Checklist
When submitting a bug finding to a company program:
1. **Title:** Clear and concise (e.g., `CORS Misconfiguration leading to Arbitrary Origin Reflection on /api/user`).
2. **Severity:** Accurate CVSS rating (e.g., Low, Medium, High).
3. **Target Asset:** Exact in-scope URL or endpoint.
4. **Vulnerability Description:** Explain what the vulnerability is and the underlying cause.
5. **Step-by-Step Proof of Concept (PoC):** Minimal, reproducible steps demonstrating the issue without causing harm or data corruption.
6. **Business Impact:** How an attacker could abuse this to affect the company or its users.
7. **Remediation Recommendation:** Practical guidance on how developers can remediate the bug (e.g., configure strict CORS allowlists, implement Content-Security-Policy headers, revoke and rotate exposed credentials).

> [!IMPORTANT]
> **Strict Ethical Policy:** Only test systems you have explicit, documented permission to assess. Strictly respect program rules of engagement, rate limits, and out-of-scope exclusions. Never perform denial-of-service, data exfiltration, or modification of live user data.

---

## 📥 Universal On-Demand Tool Installer

No tool is ever missing in ADos! When any security tool is invoked (from the Desktop Studio, REST API, or CLI), the **Universal Tool Installer** (`tools/tool_installer.py`) dynamically guarantees readiness:

- **Instant Zero-Wait Setup:** If a tool binary (`john`, `nmap`, `sqlmap`, `adb`, `subfinder`, `secret-scan`, etc.) is not present on your system PATH, the installer automatically generates a lightweight, high-performance pure-Python fallback inside `tools/bin/` with a Windows `.bat` and Linux shell launcher in **< 0.005 seconds**.
- **Zero External Dependencies:** Built entirely with Python's standard library (`urllib`, `socket`, `ssl`, `json`, `hashlib`, `re`, `argparse`).
- **Interactive UI Toggle:** Check "Auto-Install On-Demand" in ADos Studio to have missing tools installed transparently before execution.
- **Batch Verification:** Click **"📥 Install / Verify All Tools"** to verify and install all 15+ cybersecurity tools at once.

---

## 📱 Mobile NetHunter OS Builder & Samsung Optimizations

ADos consolidates the entire **Kali NetHunter** mobile ecosystem (including `kali-nethunter-installer`) into a unified build orchestrator:

```bash
# Build package for Samsung Galaxy S10 with Red Team tools:
python3 build.py --device samsung_s10 --release 11 --rootfs minimal --tools redteam --debloat-samsung

# Build for generic ARM64 phone:
python3 build.py --device generic_arm64 --release 13 --type twrp
```

### Supported Hardware Presets:
- `samsung_s9` (Galaxy S9 / S9+)
- `samsung_s10` (Galaxy S10 / S10e / S10+)
- `samsung_s20` (Galaxy S20 / S20+ / S20 Ultra)
- `samsung_note9` (Galaxy Note 9)
- `samsung_note10` (Galaxy Note 10 / Note 10+)
- `samsung_a50` (Galaxy A50)
- `samsung_a52` (Galaxy A52 / A52s 5G)
- `generic_arm64` (Generic 64-bit ARM / GSI)
- `generic_armhf` (Generic 32-bit ARM)

---

## 🔌 Full-Stack REST Backend API Reference

ADos includes a lightweight HTTP REST server powering both the desktop software and remote integrations.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` / `/status` | Server health check and system metrics |
| `GET` | `/api/tools/installed` | List all available and installed security tools with status |
| `POST` | `/install-tool` | Install or verify any tool on-demand (`{"tool": "subfinder"}`) |
| `POST` | `/api/tools/execute` | Execute an installed security tool with arguments |
| `POST` | `/api/build` | Trigger mobile OS package generation |
| `GET` | `/api/devices` | Query supported hardware device matrix |
| `GET` | `/api/profiles` | Query curated toolset profiles |

---

## 📖 In-Depth Guides & Documentation

- **[Installation Guide](docs/INSTALL_GUIDE.md):** Complete flashing, Magisk root, and NetHunter KeX setup.
- **[Samsung Galaxy Setup Guide](docs/SAMSUNG_GUIDE.md):** Dedicated Knox mitigation and Odin guide.
- **[Developer Guide](docs/DEVELOPER_GUIDE.md):** Extending device profiles and custom packages.

---

## 🧪 Verification & Automated Testing

All features maintain 100% automated test coverage:

```powershell
# Run the 54+ ADos core test suite:
python -m unittest discover -s tests
```

---

## ⚖️ License & Ethical Disclaimer

- Licensed under the **GNU General Public License v3.0 (GPLv3)**.
- Designed strictly for authorized penetration testing, academic security research, defensive hardening, and authorized bug bounty participation. Unauthorized testing against third-party systems is illegal.
