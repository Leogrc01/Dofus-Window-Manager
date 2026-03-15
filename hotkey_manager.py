"""Module pour gérer les raccourcis clavier et souris globaux."""
import keyboard
from pynput import mouse as pynput_mouse
from typing import Callable, Dict, List, Optional
from window_manager import WindowManager


# Mapping des noms de boutons souris vers pynput
MOUSE_BUTTON_MAP = {
    "mouse3": pynput_mouse.Button.middle,
    "mouse4": pynput_mouse.Button.x1,
    "mouse5": pynput_mouse.Button.x2,
}


def _is_mouse_button(key: str) -> bool:
    """Vérifie si la touche est un bouton souris."""
    return key.lower().strip() in MOUSE_BUTTON_MAP


class HotkeyManager:
    """Gère les raccourcis clavier et souris pour le switching de fenêtres."""
    
    DEFAULT_POSITION_KEYS = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8']
    DEFAULT_NEXT_KEY = '`'  # Backtick/accent grave
    DEFAULT_PREVIOUS_KEY = '\\'  # Backslash
    DEFAULT_TOGGLE_OVERLAY_KEY = 'ctrl+alt+o'
    DEFAULT_OPEN_CONFIG_KEY = 'ctrl+alt+c'
    DEFAULT_QUIT_KEY = 'ctrl+alt+q'
    DEFAULT_WHEEL_KEY = 'ctrl+alt+w'
    
    def __init__(self, window_manager: WindowManager):
        self.window_manager = window_manager
        self.registered_hotkeys: List[str] = []
        
        # Callbacks personnalisables
        self.on_toggle_overlay: Callable = lambda: None
        self.on_open_config: Callable = lambda: None
        self.on_quit: Callable = lambda: None
        self.on_toggle_wheel: Callable = lambda: None
        
        # Configuration des touches
        self.position_keys = self.DEFAULT_POSITION_KEYS.copy()
        self.next_key = self.DEFAULT_NEXT_KEY
        self.previous_key = self.DEFAULT_PREVIOUS_KEY
        self.toggle_overlay_key = self.DEFAULT_TOGGLE_OVERLAY_KEY
        self.open_config_key = self.DEFAULT_OPEN_CONFIG_KEY
        self.quit_key = self.DEFAULT_QUIT_KEY
        self.wheel_key = self.DEFAULT_WHEEL_KEY
        
        # Listener souris (pynput)
        self._mouse_listener: Optional[pynput_mouse.Listener] = None
        self._mouse_callbacks: Dict[pynput_mouse.Button, Callable] = {}
        
    def register_all(self):
        """Enregistre tous les raccourcis clavier et souris."""
        self.unregister_all()
        
        # Raccourcis pour chaque position (F1-F8)
        for i, key in enumerate(self.position_keys):
            try:
                keyboard.add_hotkey(key, lambda pos=i: self._switch_to_position(pos))
                self.registered_hotkeys.append(key)
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de {key}: {e}")
        
        # Raccourci pour passer au suivant (clavier ou souris)
        if _is_mouse_button(self.next_key):
            btn = MOUSE_BUTTON_MAP[self.next_key.lower().strip()]
            self._mouse_callbacks[btn] = self._switch_to_next
        else:
            try:
                keyboard.add_hotkey(self.next_key, self._switch_to_next)
                self.registered_hotkeys.append(self.next_key)
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de {self.next_key}: {e}")
        
        # Raccourci pour passer au précédent (clavier ou souris)
        if _is_mouse_button(self.previous_key):
            btn = MOUSE_BUTTON_MAP[self.previous_key.lower().strip()]
            self._mouse_callbacks[btn] = self._switch_to_previous
        else:
            try:
                keyboard.add_hotkey(self.previous_key, self._switch_to_previous)
                self.registered_hotkeys.append(self.previous_key)
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de {self.previous_key}: {e}")
        
        # Raccourci pour afficher/masquer l'overlay
        try:
            keyboard.add_hotkey(self.toggle_overlay_key, self._toggle_overlay)
            self.registered_hotkeys.append(self.toggle_overlay_key)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de {self.toggle_overlay_key}: {e}")
        
        # Raccourci pour ouvrir la configuration
        try:
            keyboard.add_hotkey(self.open_config_key, self._open_config)
            self.registered_hotkeys.append(self.open_config_key)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de {self.open_config_key}: {e}")
        
        # Raccourci pour quitter
        try:
            keyboard.add_hotkey(self.quit_key, self._quit)
            self.registered_hotkeys.append(self.quit_key)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de {self.quit_key}: {e}")
        
        # Raccourci pour la roue de sélection
        try:
            keyboard.add_hotkey(self.wheel_key, self._toggle_wheel)
            self.registered_hotkeys.append(self.wheel_key)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de {self.wheel_key}: {e}")
        
        # Démarrer le listener souris si des boutons sont configurés
        self._start_mouse_listener()
    
    def _start_mouse_listener(self):
        """Démarre le listener pynput pour les boutons souris configurés."""
        if not self._mouse_callbacks:
            return
        
        def on_click(x, y, button, pressed):
            if pressed and button in self._mouse_callbacks:
                self._mouse_callbacks[button]()
        
        self._mouse_listener = pynput_mouse.Listener(on_click=on_click)
        self._mouse_listener.start()
    
    def unregister_all(self):
        """Désenregistre tous les raccourcis clavier et souris."""
        # Arrêter le listener souris
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        self._mouse_callbacks.clear()
        
        # Raccourcis clavier
        for hotkey in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except Exception:
                pass
        self.registered_hotkeys.clear()
    
    def _switch_to_position(self, position: int):
        """Callback pour switcher vers une position."""
        self.window_manager.switch_to_position(position)
    
    def _switch_to_next(self):
        """Callback pour switcher vers le suivant."""
        self.window_manager.switch_to_next()
    
    def _switch_to_previous(self):
        """Callback pour switcher vers le précédent."""
        self.window_manager.switch_to_previous()
    
    def _toggle_overlay(self):
        """Callback pour afficher/masquer l'overlay."""
        self.on_toggle_overlay()
    
    def _open_config(self):
        """Callback pour ouvrir la configuration."""
        self.on_open_config()
    
    def _quit(self):
        """Callback pour quitter l'application."""
        self.on_quit()
    
    def _toggle_wheel(self):
        """Callback pour afficher/masquer la roue de sélection."""
        self.on_toggle_wheel()
    
    def set_position_keys(self, keys: List[str]):
        """Configure les touches pour les positions."""
        if len(keys) >= 8:
            self.position_keys = keys[:8]
            self.register_all()
    
    def set_next_key(self, key: str):
        """Configure la touche pour passer au suivant."""
        self.next_key = key
        self.register_all()
    
    def set_previous_key(self, key: str):
        """Configure la touche pour passer au précédent."""
        self.previous_key = key
        self.register_all()
    
    def set_toggle_overlay_key(self, key: str):
        """Configure la touche pour afficher/masquer l'overlay."""
        self.toggle_overlay_key = key
        self.register_all()
    
    def set_open_config_key(self, key: str):
        """Configure la touche pour ouvrir la configuration."""
        self.open_config_key = key
        self.register_all()
    
    def set_quit_key(self, key: str):
        """Configure la touche pour quitter."""
        self.quit_key = key
        self.register_all()
    
    def to_dict(self) -> Dict:
        """Convertit la configuration en dictionnaire."""
        return {
            "position_keys": self.position_keys,
            "next_key": self.next_key,
            "previous_key": self.previous_key,
            "toggle_overlay_key": self.toggle_overlay_key,
            "open_config_key": self.open_config_key,
            "quit_key": self.quit_key,
            "wheel_key": self.wheel_key
        }
    
    def from_dict(self, data: Dict):
        """Charge la configuration depuis un dictionnaire."""
        self.position_keys = data.get("position_keys", self.DEFAULT_POSITION_KEYS)
        self.next_key = data.get("next_key", self.DEFAULT_NEXT_KEY)
        self.previous_key = data.get("previous_key", self.DEFAULT_PREVIOUS_KEY)
        self.toggle_overlay_key = data.get("toggle_overlay_key", self.DEFAULT_TOGGLE_OVERLAY_KEY)
        self.open_config_key = data.get("open_config_key", self.DEFAULT_OPEN_CONFIG_KEY)
        self.quit_key = data.get("quit_key", self.DEFAULT_QUIT_KEY)
        self.wheel_key = data.get("wheel_key", self.DEFAULT_WHEEL_KEY)
