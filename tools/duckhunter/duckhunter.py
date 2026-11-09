import os
import sys
from typing import List, Tuple

# Mapping of standard ASCII to (modifier, hid_keycode)
# Modifier: 0x00=None, 0x02=Left Shift
HID_KEYMAP = {
    'a': (0x00, 0x04), 'b': (0x00, 0x05), 'c': (0x00, 0x06), 'd': (0x00, 0x07),
    'e': (0x00, 0x08), 'f': (0x00, 0x09), 'g': (0x00, 0x0a), 'h': (0x00, 0x0b),
    'i': (0x00, 0x0c), 'j': (0x00, 0x0d), 'k': (0x00, 0x0e), 'l': (0x00, 0x0f),
    'm': (0x00, 0x10), 'n': (0x00, 0x11), 'o': (0x00, 0x12), 'p': (0x00, 0x13),
    'q': (0x00, 0x14), 'r': (0x00, 0x15), 's': (0x00, 0x16), 't': (0x00, 0x17),
    'u': (0x00, 0x18), 'v': (0x00, 0x19), 'w': (0x00, 0x1a), 'x': (0x00, 0x1b),
    'y': (0x00, 0x1c), 'z': (0x00, 0x1d),
    'A': (0x02, 0x04), 'B': (0x02, 0x05), 'C': (0x02, 0x06), 'D': (0x02, 0x07),
    'E': (0x02, 0x08), 'F': (0x02, 0x09), 'G': (0x02, 0x0a), 'H': (0x02, 0x0b),
    'I': (0x02, 0x0c), 'J': (0x02, 0x0d), 'K': (0x02, 0x0e), 'L': (0x02, 0x0f),
    'M': (0x02, 0x10), 'N': (0x02, 0x11), 'O': (0x02, 0x12), 'P': (0x02, 0x13),
    'Q': (0x02, 0x14), 'R': (0x02, 0x15), 'S': (0x02, 0x16), 'T': (0x02, 0x17),
    'U': (0x02, 0x18), 'V': (0x02, 0x19), 'W': (0x02, 0x1a), 'X': (0x02, 0x1b),
    'Y': (0x02, 0x1c), 'Z': (0x02, 0x1d),
    '1': (0x00, 0x1e), '2': (0x00, 0x1f), '3': (0x00, 0x20), '4': (0x00, 0x21),
    '5': (0x00, 0x22), '6': (0x00, 0x23), '7': (0x00, 0x24), '8': (0x00, 0x25),
    '9': (0x00, 0x26), '0': (0x00, 0x27),
    '!': (0x02, 0x1e), '@': (0x02, 0x1f), '#': (0x02, 0x20), '$': (0x02, 0x21),
    '%': (0x02, 0x22), '^': (0x02, 0x23), '&': (0x02, 0x24), '*': (0x02, 0x25),
    '(': (0x02, 0x26), ')': (0x02, 0x27),
    ' ': (0x00, 0x2c), '\n': (0x00, 0x28), '\t': (0x00, 0x2b),
    '-': (0x00, 0x2d), '_': (0x02, 0x2d),
    '=': (0x00, 0x2e), '+': (0x02, 0x2e),
    '[': (0x00, 0x2f), '{': (0x02, 0x2f),
    ']': (0x00, 0x30), '}': (0x02, 0x30),
    '\\': (0x00, 0x31), '|': (0x02, 0x31),
    ';': (0x00, 0x33), ':': (0x02, 0x33),
    '\'': (0x00, 0x34), '"': (0x02, 0x34),
    '`': (0x00, 0x35), '~': (0x02, 0x35),
    ',': (0x00, 0x36), '<': (0x02, 0x36),
    '.': (0x00, 0x37), '>': (0x02, 0x37),
    '/': (0x00, 0x38), '?': (0x02, 0x38)
}

SPECIAL_KEYS = {
    "ENTER": (0x00, 0x28),
    "ESCAPE": (0x00, 0x29),
    "BACKSPACE": (0x00, 0x2a),
    "TAB": (0x00, 0x2b),
    "SPACE": (0x00, 0x2c),
    "CAPSLOCK": (0x00, 0x39),
    "F1": (0x00, 0x3a), "F2": (0x00, 0x3b), "F3": (0x00, 0x3c), "F4": (0x00, 0x3d),
    "F5": (0x00, 0x3e), "F6": (0x00, 0x3f), "F7": (0x00, 0x40), "F8": (0x00, 0x41),
    "F9": (0x00, 0x42), "F10": (0x00, 0x43), "F11": (0x00, 0x44), "F12": (0x00, 0x45),
    "UP": (0x00, 0x52), "DOWN": (0x00, 0x51), "LEFT": (0x00, 0x50), "RIGHT": (0x00, 0x4f)
}

class DuckHunterCompiler:
    """Translates Rubber Ducky scripts into shell commands for /dev/hidg0."""

    def __init__(self, hid_dev: str = "/dev/hidg0"):
        self.hid_dev = hid_dev

    def _make_hid_press(self, mod: int, key: int) -> str:
        # 8 bytes: mod, reserved(0), key, 0, 0, 0, 0, 0
        press = f"printf '\\x{mod:02x}\\x00\\x{key:02x}\\x00\\x00\\x00\\x00\\x00' > {self.hid_dev}"
        release = f"printf '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00' > {self.hid_dev}"
        return f"{press}; {release}"

    def compile(self, script_text: str) -> List[str]:
        commands = []
        lines = script_text.strip().splitlines()

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("REM"):
                continue

            parts = line.split(" ", 1)
            cmd = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "DELAY":
                try:
                    ms = int(arg)
                    commands.append(f"sleep {ms / 1000.0:.3f}")
                except ValueError:
                    commands.append("sleep 0.1")

            elif cmd == "STRING":
                for char in arg:
                    mod, code = HID_KEYMAP.get(char, (0x00, 0x00))
                    if code:
                        commands.append(self._make_hid_press(mod, code))

            elif cmd == "GUI" or cmd == "WINDOWS":
                # E.g. GUI r
                mod = 0x08  # Left GUI
                code = 0x00
                if arg:
                    char = arg[0].lower()
                    _, code = HID_KEYMAP.get(char, (0x00, 0x00))
                commands.append(self._make_hid_press(mod, code))

            elif cmd == "CTRL" or cmd == "CONTROL":
                mod = 0x01
                char = arg[0].lower() if arg else ""
                _, code = HID_KEYMAP.get(char, (0x00, 0x00))
                commands.append(self._make_hid_press(mod, code))

            elif cmd == "ALT":
                mod = 0x04
                char = arg[0].lower() if arg else ""
                _, code = HID_KEYMAP.get(char, (0x00, 0x00))
                commands.append(self._make_hid_press(mod, code))

            elif cmd in SPECIAL_KEYS:
                mod, code = SPECIAL_KEYS[cmd]
                commands.append(self._make_hid_press(mod, code))

        return commands

    def to_executable_script(self, script_text: str) -> str:
        commands = self.compile(script_text)
        header = [
            "#!/system/bin/sh",
            "# ADos DuckHunter HID Payload Execution",
            "if [ ! -e /dev/hidg0 ]; then",
            "    echo '[-] Error: /dev/hidg0 not found. Run setup-usb-gadget.sh first.'",
            "    exit 1",
            "fi",
            "echo '[+] Executing BadUSB payload...'"
        ]
        return "\n".join(header + commands + ["echo '[+] Payload execution finished!'\n"])

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 duckhunter.py <payload.txt> [output.sh]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "run_payload.sh"

    with open(in_file, "r", encoding="utf-8") as f:
        script_text = f.read()

    compiler = DuckHunterCompiler()
    sh_content = compiler.to_executable_script(script_text)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(sh_content)

    print(f"[+] Compiled '{in_file}' to '{out_file}' successfully!")

if __name__ == "__main__":
    main()
