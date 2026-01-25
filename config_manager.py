"""Module pour gérer la configuration de l'application."""
import json
import os
from typing import Dict, Optional
from pathlib import Path


class ConfigManager:
    """Gère la sauvegarde et le chargement de la configuration."""
    
    DEFAULT_CONFIG_FILE = "config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config_path = Path(self.config_file)
        
    def save(self, config: Dict) -> bool:
        """Sauvegarde la configuration dans un fichier JSON."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def load(self) -> Optional[Dict]:
        """Charge la configuration depuis un fichier JSON."""
        if not self.config_path.exists():
            return None
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return None
    
    def exists(self) -> bool:
        """Vérifie si un fichier de configuration existe."""
        return self.config_path.exists()
    
    def delete(self) -> bool:
        """Supprime le fichier de configuration."""
        try:
            if self.config_path.exists():
                self.config_path.unlink()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la configuration: {e}")
            return False
    
    def create_default_config(self) -> Dict:
        """Crée une configuration par défaut."""
        return {
            "version": "0.1.0",
            "window_manager": {
                "characters": [],
                "current_index": 0
            },
            "hotkeys": {
                "position_keys": ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"],
                "next_key": "tab",
                "previous_key": "shift+tab",
                "toggle_overlay_key": "ctrl+alt+o",
                "quit_key": "ctrl+alt+q"
            },
            "overlay": {
                "enabled": True,
                "position_x": 100,
                "position_y": 100,
                "width": 800,
                "height": 60,
                "opacity": 0.9,
                "font_size": 14
            }
        }
    
    def get_full_config(self, window_manager_dict: Dict, hotkeys_dict: Dict, overlay_dict: Dict) -> Dict:
        """Crée un dictionnaire de configuration complet."""
        return {
            "version": "0.1.0",
            "window_manager": window_manager_dict,
            "hotkeys": hotkeys_dict,
            "overlay": overlay_dict
        }
