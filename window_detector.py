"""Détection des fenêtres DOFUS — dispatch selon la plateforme.

Windows : API Win32 (pywin32) — voir window_detector_win.py
macOS   : API Accessibility (pyobjc) — voir window_detector_mac.py
"""
import sys

if sys.platform == "darwin":
    from window_detector_mac import WindowDetector, WindowInfo
else:
    from window_detector_win import WindowDetector, WindowInfo

__all__ = ["WindowDetector", "WindowInfo"]
