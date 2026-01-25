"""Module pour détecter les fenêtres DOFUS."""
import win32gui
import win32con
import win32process
import psutil
from typing import List, Dict, Optional


class WindowInfo:
    """Informations sur une fenêtre DOFUS."""
    
    def __init__(self, hwnd: int, title: str, pid: int):
        self.hwnd = hwnd
        self.title = title
        self.pid = pid
        self.character_name: Optional[str] = None
        
    def __repr__(self):
        return f"WindowInfo(hwnd={self.hwnd}, title='{self.title}', char='{self.character_name}')"


class WindowDetector:
    """Détecte et gère les fenêtres DOFUS."""
    
    DOFUS_WINDOW_CLASS = "GLFW30"  # Classe de fenêtre typique pour DOFUS
    DOFUS_PROCESS_NAMES = ["Dofus.exe", "dofus.exe"]
    
    def __init__(self):
        self.windows: List[WindowInfo] = []
        
    def detect_windows(self) -> List[WindowInfo]:
        """Détecte toutes les fenêtres DOFUS actives."""
        self.windows = []
        win32gui.EnumWindows(self._enum_callback, None)
        return self.windows
    
    def _enum_callback(self, hwnd: int, _) -> bool:
        """Callback pour l'énumération des fenêtres."""
        if not win32gui.IsWindowVisible(hwnd):
            return True
            
        title = win32gui.GetWindowText(hwnd)
        
        # Vérifier si c'est une fenêtre DOFUS via le processus
        if self._is_dofus_process(hwnd):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                window_info = WindowInfo(hwnd, title, pid)
                self.windows.append(window_info)
            except Exception:
                pass
                
        return True
    
    def _is_dofus_process(self, hwnd: int) -> bool:
        """Vérifie si la fenêtre appartient à un processus DOFUS."""
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name() in self.DOFUS_PROCESS_NAMES
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_window_count(self) -> int:
        """Retourne le nombre de fenêtres DOFUS détectées."""
        return len(self.windows)
    
    def refresh(self) -> List[WindowInfo]:
        """Rafraîchit la liste des fenêtres."""
        return self.detect_windows()
    
    @staticmethod
    def focus_window(hwnd: int) -> bool:
        """Met le focus sur une fenêtre."""
        try:
            # Restaurer la fenêtre si elle est minimisée
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # Workaround pour Windows: simuler un Alt press pour contourner les restrictions
            import win32api
            import win32con as wcon
            
            # Simuler Alt key pour autoriser SetForegroundWindow
            win32api.keybd_event(wcon.VK_MENU, 0, 0, 0)
            
            # Essayer plusieurs méthodes
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                # Méthode alternative: BringWindowToTop + SetFocus
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetFocus(hwnd)
            
            # Relâcher Alt
            win32api.keybd_event(wcon.VK_MENU, 0, wcon.KEYEVENTF_KEYUP, 0)
            
            return True
        except Exception as e:
            # Ne plus afficher l'erreur pour éviter le spam
            return False
    
    @staticmethod
    def is_window_valid(hwnd: int) -> bool:
        """Vérifie si une fenêtre est toujours valide."""
        try:
            return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)
        except Exception:
            return False
