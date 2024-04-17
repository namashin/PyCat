import os
from typing import Optional


def find_windows_abspath(exe_name: str) -> Optional[str]:
    for root, dirs, files in os.walk(os.environ["ProgramFiles"]):
        if exe_name in files:
            return os.path.join(root, exe_name)

    for root, dirs, files in os.walk(os.environ["ProgramFiles(x86)"]):
        if exe_name in files:
            return os.path.join(root, exe_name)


def find_mac_abspath(app_name):
    for root, dirs, _ in os.walk('/Applications'):
        if app_name in dirs:
            return os.path.join(root, app_name)
