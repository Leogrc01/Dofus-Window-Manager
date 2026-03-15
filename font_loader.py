"""Utilitaire pour charger les polices personnalisées via l'API Windows."""
import ctypes
import os
import sys


def _get_font_dir() -> str:
    """Retourne le chemin du dossier font/ (compatible .exe et .py)."""
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "font")


def load_custom_fonts():
    """Charge toutes les polices .ttf/.otf du dossier font/ pour la session.

    Utilise AddFontResourceExW avec FR_PRIVATE (0x10) pour rendre les polices
    disponibles uniquement au processus courant, sans installation système.
    """
    font_dir = _get_font_dir()
    if not os.path.isdir(font_dir):
        return

    FR_PRIVATE = 0x10
    for filename in os.listdir(font_dir):
        if filename.lower().endswith(('.ttf', '.otf')):
            font_path = os.path.join(font_dir, filename)
            ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
