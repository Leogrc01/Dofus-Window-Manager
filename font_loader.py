"""Utilitaire pour charger les polices personnalisées (Windows GDI / macOS CoreText)."""
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

    Windows : AddFontResourceExW avec FR_PRIVATE (0x10) — polices disponibles
    uniquement au processus courant, sans installation système.
    macOS   : CTFontManagerRegisterFontsForURL avec scope process (équivalent).
    """
    font_dir = _get_font_dir()
    if not os.path.isdir(font_dir):
        return

    font_paths = [
        os.path.join(font_dir, f) for f in os.listdir(font_dir)
        if f.lower().endswith(('.ttf', '.otf'))
    ]

    if sys.platform == "darwin":
        try:
            from CoreText import CTFontManagerRegisterFontsForURL, kCTFontManagerScopeProcess
            from Foundation import NSURL
            for font_path in font_paths:
                url = NSURL.fileURLWithPath_(font_path)
                CTFontManagerRegisterFontsForURL(url, kCTFontManagerScopeProcess, None)
        except Exception:
            pass  # Police de secours du système utilisée
        return

    import ctypes
    FR_PRIVATE = 0x10
    for font_path in font_paths:
        ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
