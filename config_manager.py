"""Module pour gérer la configuration de l'application."""
import json
import os
import shutil
from typing import Dict, Optional
from pathlib import Path

from app_paths import get_data_dir


class ConfigManager:
    """Gère la sauvegarde et le chargement de la configuration."""

    DEFAULT_CONFIG_FILE = "config.json"

    def __init__(self, config_file: Optional[str] = None):
        if config_file:
            self.config_file = config_file
            self.config_path = Path(config_file)
        else:
            # Config dans %APPDATA% : survit aux déplacements de l'exe et
            # fonctionne même si l'exe est dans un dossier protégé
            self.config_path = Path(get_data_dir()) / self.DEFAULT_CONFIG_FILE
            self.config_file = str(self.config_path)
            self._migrate_legacy_file(Path(self.DEFAULT_CONFIG_FILE))

    def _migrate_legacy_file(self, legacy_path: Path):
        """Déplace l'ancienne config (à côté de l'exe) vers %APPDATA%."""
        if legacy_path.exists() and not self.config_path.exists():
            try:
                shutil.move(str(legacy_path), str(self.config_path))
                print(f"Configuration migrée vers {self.config_path}")
            except Exception as e:
                print(f"Impossible de migrer l'ancienne configuration: {e}")
        
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
