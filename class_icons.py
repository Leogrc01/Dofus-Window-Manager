"""Chargement des icônes de classe, partagé entre l'overlay et la roue."""
import os
import sys
from typing import Dict, Optional, Tuple
from PIL import Image, ImageTk


def _get_classes_dir() -> str:
    """Retourne le chemin du dossier classes/ (compatible .exe et .py)."""
    if getattr(sys, 'frozen', False):
        # Exécuté depuis un .exe PyInstaller
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "classes")


CLASSES_DIR = _get_classes_dir()

# Cache global : garde aussi les références pour éviter le garbage collection
_cache: Dict[Tuple[str, int], Optional[ImageTk.PhotoImage]] = {}


def get_class_icon(class_name: str, size: int) -> Optional[ImageTk.PhotoImage]:
    """Retourne l'icône d'une classe redimensionnée, ou None si introuvable."""
    key = (class_name.lower().strip(), size)
    if key in _cache:
        return _cache[key]

    icon_path = os.path.join(CLASSES_DIR, f"{key[0]}.png")
    if not os.path.exists(icon_path):
        _cache[key] = None
        return None

    try:
        img = Image.open(icon_path)
        img = img.resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
    except Exception:
        photo = None
    _cache[key] = photo
    return photo
