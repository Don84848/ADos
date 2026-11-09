#!/usr/bin/env python3
"""
ADos Studio Desktop Launcher
Ensures window renders on the user's active interactive desktop (WinSta0\\Default).
"""
import ctypes
import os
import sys

if sys.platform == "win32":
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception as e:
        pass

# Ensure repo root is on path
repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from desktop.ados_studio import main

if __name__ == "__main__":
    main()
