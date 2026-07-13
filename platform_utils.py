"""Helpers multi-plateformes (Windows / macOS)."""
import sys
import time

IS_MAC = sys.platform == "darwin"
IS_WINDOWS = sys.platform == "win32"


def apply_color_key_transparency(window, color_key: str) -> bool:
    """Active la transparence par couleur-clé (Windows uniquement).

    Sous macOS, Tk ne supporte pas '-transparentcolor' : la fenêtre reste
    opaque (la couleur-clé sombre sert alors de fond). Retourne True si la
    transparence a pu être activée.
    """
    try:
        window.wm_attributes('-transparentcolor', color_key)
        return True
    except Exception:
        return False


def press_enter():
    """Simule un appui sur Entrée (frappe globale)."""
    if IS_MAC:
        from pynput.keyboard import Controller, Key
        Controller().tap(Key.enter)
    else:
        import keyboard
        keyboard.send('enter')


def write_text(text: str, delay: float = 0.01):
    """Tape du texte dans la fenêtre active, caractère par caractère."""
    if IS_MAC:
        from pynput.keyboard import Controller
        kb = Controller()
        for char in text:
            kb.type(char)
            time.sleep(delay)
    else:
        import keyboard
        keyboard.write(text, delay=delay)
