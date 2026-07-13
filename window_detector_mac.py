"""Détection des fenêtres DOFUS sous macOS (API Accessibility via pyobjc).

Même API publique que window_detector_win.py. Les "hwnd" sont ici des
identifiants synthétiques (entiers) attribués par ce module : macOS ne
fournit pas de handle entier stable pour une fenêtre, on maintient donc
un registre id → (pid, titre, occurrence) résolu à la demande.

Nécessite l'autorisation Accessibilité :
Réglages Système → Confidentialité et sécurité → Accessibilité.
"""
import psutil
from typing import Dict, List, Optional, Tuple

from AppKit import NSWorkspace, NSRunningApplication, NSApplicationActivateIgnoringOtherApps
from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXUIElementSetAttributeValue,
    AXUIElementPerformAction,
    AXIsProcessTrustedWithOptions,
    kAXTrustedCheckOptionPrompt,
    kAXWindowsAttribute,
    kAXTitleAttribute,
    kAXFocusedWindowAttribute,
    kAXMainAttribute,
    kAXRaiseAction,
)


class WindowInfo:
    """Informations sur une fenêtre DOFUS."""

    def __init__(self, hwnd: int, title: str, pid: int):
        self.hwnd = hwnd
        self.title = title
        self.pid = pid
        self.character_name: Optional[str] = None

    def __repr__(self):
        return f"WindowInfo(hwnd={self.hwnd}, title='{self.title}', char='{self.character_name}')"


def _ensure_accessibility():
    """Vérifie l'autorisation Accessibilité (affiche le prompt système si absent)."""
    try:
        options = {kAXTrustedCheckOptionPrompt: True}
        if not AXIsProcessTrustedWithOptions(options):
            print("⚠ Autorisation Accessibilité requise :")
            print("  Réglages Système → Confidentialité et sécurité → Accessibilité")
            print("  puis relancez l'application.")
    except Exception:
        pass


class WindowDetector:
    """Détecte et gère les fenêtres DOFUS (backend macOS)."""

    DOFUS_PROCESS_PREFIX = "dofus"

    # Registre partagé id synthétique ↔ (pid, titre, occurrence)
    _next_id: int = 1
    _id_by_key: Dict[Tuple[int, str, int], int] = {}
    _key_by_id: Dict[int, Tuple[int, str, int]] = {}

    def __init__(self):
        self.windows: List[WindowInfo] = []
        _ensure_accessibility()

    # ------------------------------------------------------------------
    # Helpers internes
    # ------------------------------------------------------------------

    @classmethod
    def _dofus_pids(cls) -> List[int]:
        """PIDs des processus DOFUS en cours."""
        pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = (proc.info.get('name') or '').lower()
                if name.startswith(cls.DOFUS_PROCESS_PREFIX):
                    pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return pids

    @staticmethod
    def _ax_windows(pid: int) -> List[Tuple[object, str]]:
        """Liste (élément AX, titre) des fenêtres d'un processus."""
        try:
            app_ref = AXUIElementCreateApplication(pid)
            err, windows = AXUIElementCopyAttributeValue(app_ref, kAXWindowsAttribute, None)
            if err != 0 or not windows:
                return []
            result = []
            for win in windows:
                err, title = AXUIElementCopyAttributeValue(win, kAXTitleAttribute, None)
                result.append((win, str(title) if err == 0 and title else ""))
            return result
        except Exception:
            return []

    @classmethod
    def _get_or_assign_id(cls, pid: int, title: str, occurrence: int) -> int:
        """Retourne l'id synthétique stable pour (pid, titre, occurrence)."""
        key = (pid, title, occurrence)
        if key not in cls._id_by_key:
            cls._id_by_key[key] = cls._next_id
            cls._key_by_id[cls._next_id] = key
            cls._next_id += 1
        return cls._id_by_key[key]

    @classmethod
    def _resolve(cls, hwnd: int):
        """Résout un id synthétique vers son élément AX actuel (None si périmé)."""
        key = cls._key_by_id.get(hwnd)
        if not key:
            return None
        pid, title, occurrence = key
        try:
            if not psutil.pid_exists(pid):
                return None
        except Exception:
            return None
        matches = [win for win, t in cls._ax_windows(pid) if t == title]
        if occurrence < len(matches):
            return matches[occurrence]
        return None

    # ------------------------------------------------------------------
    # API publique (identique au backend Windows)
    # ------------------------------------------------------------------

    def detect_windows(self) -> List[WindowInfo]:
        """Détecte toutes les fenêtres DOFUS actives."""
        self.windows = []
        for pid in self._dofus_pids():
            seen: Dict[str, int] = {}
            for _, title in self._ax_windows(pid):
                occurrence = seen.get(title, 0)
                seen[title] = occurrence + 1
                win_id = self._get_or_assign_id(pid, title, occurrence)
                self.windows.append(WindowInfo(win_id, title, pid))
        return self.windows

    def is_dofus_window(self, hwnd: int) -> bool:
        """Vérifie si un id correspond à une fenêtre DOFUS connue."""
        return self._resolve(hwnd) is not None

    @classmethod
    def get_foreground_window(cls) -> int:
        """Retourne l'id de la fenêtre DOFUS au premier plan (0 sinon)."""
        try:
            front_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if front_app is None:
                return 0
            name = (front_app.localizedName() or "").lower()
            if not name.startswith(cls.DOFUS_PROCESS_PREFIX):
                return 0
            pid = front_app.processIdentifier()

            app_ref = AXUIElementCreateApplication(pid)
            err, focused = AXUIElementCopyAttributeValue(app_ref, kAXFocusedWindowAttribute, None)
            if err != 0 or focused is None:
                return 0
            err, title = AXUIElementCopyAttributeValue(focused, kAXTitleAttribute, None)
            title = str(title) if err == 0 and title else ""

            # Retrouver l'occurrence parmi les fenêtres du même titre
            occurrence = 0
            same_title = [win for win, t in cls._ax_windows(pid) if t == title]
            for i, win in enumerate(same_title):
                try:
                    if win == focused:
                        occurrence = i
                        break
                except Exception:
                    break
            return cls._get_or_assign_id(pid, title, occurrence)
        except Exception:
            return 0

    @staticmethod
    def extract_character_from_title(title: str) -> str:
        """Extrait le nom du personnage depuis un titre 'NomPerso - Classe - Version'."""
        parts = title.split(" - ")
        if len(parts) >= 2:
            return parts[0].strip()
        # Titre sans personnage (ex: écran de connexion)
        return ""

    def get_window_count(self) -> int:
        """Retourne le nombre de fenêtres DOFUS détectées."""
        return len(self.windows)

    def refresh(self) -> List[WindowInfo]:
        """Rafraîchit la liste des fenêtres."""
        return self.detect_windows()

    @classmethod
    def focus_window(cls, hwnd: int) -> bool:
        """Met le focus sur une fenêtre (active l'app + raise la fenêtre)."""
        window = cls._resolve(hwnd)
        if window is None:
            return False
        try:
            pid = cls._key_by_id[hwnd][0]
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
            if app is not None:
                app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
            AXUIElementSetAttributeValue(window, kAXMainAttribute, True)
            AXUIElementPerformAction(window, kAXRaiseAction)
            return True
        except Exception:
            return False

    @classmethod
    def is_window_valid(cls, hwnd: int) -> bool:
        """Vérifie si une fenêtre est toujours valide."""
        return cls._resolve(hwnd) is not None
