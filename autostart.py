"""Démarrage automatique avec Windows (clé Run du registre, utilisateur courant)."""
import os
import sys
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "DofusWindowManager"


def _launch_command() -> str:
    """Commande à enregistrer : l'exe, ou pythonw + main.py en mode dev."""
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return f'"{pythonw}" "{script}"'


def is_enabled() -> bool:
    """Indique si le démarrage automatique est activé."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


def enable():
    """Active le démarrage automatique avec Windows."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _launch_command())


def disable():
    """Désactive le démarrage automatique."""
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
