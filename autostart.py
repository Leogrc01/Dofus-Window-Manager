"""Démarrage automatique avec la session utilisateur.

Windows : clé Run du registre (utilisateur courant).
macOS   : LaunchAgent (~/Library/LaunchAgents).
"""
import os
import sys

IS_MAC = sys.platform == "darwin"
if not IS_MAC:
    import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "DofusWindowManager"
LAUNCH_AGENT_LABEL = "com.dofuswindowmanager.autostart"
LAUNCH_AGENT_PATH = os.path.expanduser(
    f"~/Library/LaunchAgents/{LAUNCH_AGENT_LABEL}.plist"
)


def _launch_args() -> list:
    """Arguments de lancement : l'exe, ou python + main.py en mode dev."""
    if getattr(sys, 'frozen', False):
        return [sys.executable]
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return [sys.executable, script]


def _launch_command() -> str:
    """Commande à enregistrer dans le registre Windows."""
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return f'"{pythonw}" "{script}"'


def is_enabled() -> bool:
    """Indique si le démarrage automatique est activé."""
    if IS_MAC:
        return os.path.exists(LAUNCH_AGENT_PATH)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


def enable():
    """Active le démarrage automatique avec la session."""
    if IS_MAC:
        import plistlib
        os.makedirs(os.path.dirname(LAUNCH_AGENT_PATH), exist_ok=True)
        plist = {
            "Label": LAUNCH_AGENT_LABEL,
            "ProgramArguments": _launch_args(),
            "RunAtLoad": True,
        }
        with open(LAUNCH_AGENT_PATH, "wb") as f:
            plistlib.dump(plist, f)
        return
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())


def disable():
    """Désactive le démarrage automatique."""
    if IS_MAC:
        try:
            os.remove(LAUNCH_AGENT_PATH)
        except OSError:
            pass
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except OSError:
        pass


def toggle() -> bool:
    """Inverse l'état et retourne le nouvel état."""
    if is_enabled():
        disable()
        return False
    enable()
    return True
