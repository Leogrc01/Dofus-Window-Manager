"""Script pour lancer la fenêtre de configuration GUI."""
from window_detector import WindowDetector
from config_gui import ConfigWindow
from config_manager import ConfigManager


def save_configuration(characters):
    """Callback pour sauvegarder la configuration."""
    config_manager = ConfigManager()
    
    # Trier par position
    characters.sort(key=lambda c: c["position"])
    
    # Créer la config complète
    config = {
        "version": "0.1.0",
        "window_manager": {
            "characters": characters,
            "current_index": 0
        },
        "hotkeys": {
            "position_keys": ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"],
            "next_key": "`",
            "previous_key": "\\",
            "toggle_overlay_key": "ctrl+alt+o",
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
    config_window = ConfigWindow(detector, save_configuration)
    config_window.show()


if __name__ == "__main__":
    main()
