"""Script pour lancer la fenêtre de configuration GUI."""
from window_detector import WindowDetector
from config_gui import ConfigWindow
from config_manager import ConfigManager


def save_configuration(characters, hotkeys=None):
    """Callback pour sauvegarder la configuration."""
    config_manager = ConfigManager()
    
    # Trier par position
    characters.sort(key=lambda c: c["position"])
    
    # Utiliser les hotkeys fournis ou les valeurs par défaut
    if hotkeys is None:
        hotkeys = {}
    
    # Créer la config complète
    config = {
        "version": "0.1.0",
        "window_manager": {
            "characters": characters,
            "current_index": 0
        },
        "hotkeys": {
            "position_keys": ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"],
            "next_key": hotkeys.get("next_key", "`"),
            "previous_key": hotkeys.get("previous_key", "\\"),
            "toggle_overlay_key": "ctrl+alt+o",
            "open_config_key": "ctrl+alt+c",
            "quit_key": "ctrl+alt+q"
        },
        "overlay": {
            "enabled": True,
            "position_x": 100,
            "position_y": 100,
            "width": 855,
            "height": 50,
            "opacity": 0.9,
            "font_size": 14
        }
    }
    
    config_manager.save(config)
    print("✓ Configuration sauvegardée dans config.json")


def main():
    """Point d'entrée principal."""
    print("🎮 DOFUS Window Switcher - Configuration\n")
    
    detector = WindowDetector()
    config_manager = ConfigManager()
    
    # Charger la config existante pour récupérer les hotkeys ET l'ordre précédent
    existing_config = config_manager.load()
    current_hotkeys = existing_config.get("hotkeys", {}) if existing_config else {}
    previous_window_config = existing_config.get("window_manager", {}) if existing_config else {}
    
    if previous_window_config:
        print("💾 Configuration précédente détectée - les positions seront pré-remplies\n")
    
    config_window = ConfigWindow(
        detector, 
        save_configuration, 
        current_hotkeys=current_hotkeys,
        previous_config=previous_window_config
    )
    config_window.show()


if __name__ == "__main__":
    main()
