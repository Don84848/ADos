import os
import json
import zipfile
import hashlib
from typing import Dict, Any, Tuple

class PackageGenerator:
    """Generates standard flashable Android recovery zips and Magisk modules."""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    def create_package(
        self,
        manifest: Dict[str, Any],
        staging_files: Dict[str, str] = None
    ) -> Tuple[str, str]:
        """Creates the flashable ZIP package and returns (file_path, sha256_hash)."""
        pkg_type = manifest.get("type", "twrp")
        
        with zipfile.ZipFile(self.output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. Manifest
            manifest_str = json.dumps(manifest, indent=2)
            zf.writestr("ados_manifest.json", manifest_str)
            
            # 2. Recovery / TWRP binary scripts
            if pkg_type == "twrp":
                updater_script = (
                    'ui_print("***********************************************");\n'
                    'ui_print("*       ADos - NetHunter Mobile Security      *");\n'
                    'ui_print("*       Lightweight Cybersecurity Platform    *");\n'
                    'ui_print("***********************************************");\n'
                    f'ui_print("Target Device: {manifest.get("device", "generic")}");\n'
                    f'ui_print("Android Release: {manifest.get("release", "auto")}");\n'
                    'ui_print("Flashing ADos core system & NetHunter chroot...");\n'
                    'package_extract_dir("system", "/system");\n'
                    'package_extract_dir("data", "/data");\n'
                    'set_perm_recursive(0, 0, 0755, 0644, "/system/etc/ados");\n'
                    'ui_print("ADos Mobile OS installed successfully!");\n'
                )
                zf.writestr("META-INF/com/google/android/updater-script", updater_script)
                
                update_binary = (
                    "#!/sbin/sh\n"
                    "# ADos Recovery Installer Stub\n"
                    "OUTFD=$2\n"
                    'ui_print() { echo -e "ui_print $1\\nui_print" > /proc/self/fd/$OUTFD; }\n'
                    'ui_print "Starting ADos NetHunter Installation..."\n'
                    "exit 0\n"
                )
                zf.writestr("META-INF/com/google/android/update-binary", update_binary)
                
            elif pkg_type == "magisk":
                module_prop = (
                    f"id=ados_nethunter\n"
                    f"name=ADos NetHunter Core\n"
                    f"version={manifest.get('version', '1.0.0')}\n"
                    f"versionCode=100\n"
                    f"author=ADos Security Team\n"
                    f"description=Lightweight Kali NetHunter cybersecurity suite and rootfs integration for {manifest.get('device', 'generic')}\n"
                )
                zf.writestr("module.prop", module_prop)
                
                service_sh = (
                    "#!/system/bin/sh\n"
                    "MODDIR=${0%/*}\n"
                    "# Launch ADos boot triggers and USB gadget\n"
                    "if [ -f /data/ados/scripts/setup-usb-gadget.sh ]; then\n"
                    "    sh /data/ados/scripts/setup-usb-gadget.sh &\n"
                    "fi\n"
                )
                zf.writestr("service.sh", service_sh)
            
            # 3. Add any staging files
            if staging_files:
                for zip_rel_path, content in staging_files.items():
                    if isinstance(content, str):
                        zf.writestr(zip_rel_path, content)
                    elif isinstance(content, bytes):
                        zf.writestr(zip_rel_path, content)

        # 4. Compute SHA256 checksum
        sha256 = hashlib.sha256()
        with open(self.output_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        
        sha256_hash = sha256.hexdigest()
        checksum_path = f"{self.output_path}.sha256"
        with open(checksum_path, "w", encoding="utf-8") as f:
            f.write(f"{sha256_hash}  {os.path.basename(self.output_path)}\n")
            
        return self.output_path, sha256_hash
