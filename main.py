"""Point d'entrée principal de l'application DOFUS Window Switcher."""
import sys
import threading
import time
from typing import Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from window_detector import WindowDetector
from window_manager import WindowManager
from hotkey_manager import HotkeyManager
from overlay import OverlayWindow
from config_manager import ConfigManager


class DofusWindowSwitcher:
    """Application principale pour le switching de fenêtres DOFUS."""
    
    def __init__(self):
        # Composants principaux
        self.detector = WindowDetector()
        self.window_manager = WindowManager(self.detector)
        self.hotkey_manager = HotkeyManager(self.window_manager)
        self.overlay = OverlayWindow()
        self.config_manager = ConfigManager()
        
        # System tray
        self.tray_icon: Optional[pystray.Icon] = None
        self.running = False
        
        # Configurer les callbacks des hotkeys
        self.hotkey_manager.on_toggle_overlay = self._toggle_overlay
        self.hotkey_manager.on_quit = self.quit
        
    def initialize(self):
        """Initialise l'application."""
        print("🎮 DOFUS Window Switcher - Initialisation...")
        
        # Charger la configuration
        config = self.config_manager.load()
        
        if config:
            print("✓ Configuration chargée")
            self._load_config(config)
        else:
            print("ℹ Premier lancement - Configuration initiale")
            self._first_time_setup()
        
        # Créer l'overlay
        self.overlay.create_window()
        
        # Enregistrer les hotkeys
        self.hotkey_manager.register_all()
        print("✓ Raccourcis clavier enregistrés")
        
        # Mettre à jour l'overlay
        self._update_overlay()
        
        print("✓ Initialisation terminée")
        print("\nRaccourcis:")
        print("  F1-F8      : Switch vers le personnage 1-8")
        print("  `          : Personnage suivant")
        print("  \\          : Personnage précédent")
        print("  Ctrl+Alt+O : Afficher/masquer l'overlay")
        print("  Ctrl+Alt+Q : Quitter")
    
    def _first_time_setup(self):
        """Configuration initiale au premier lancement."""
        print("\n🔍 Détection des fenêtres DOFUS...")
        windows = self.detector.detect_windows()
        
        if not windows:
            print("⚠ Aucune fenêtre DOFUS détectée!")
            print("  Assurez-vous que DOFUS est lancé et réessayez.")
            return
        
        print(f"✓ {len(windows)} fenêtre(s) DOFUS détectée(s)")
        
        # Créer une configuration par défaut avec les fenêtres détectées
        for i, window in enumerate(windows[:8]):  # Max 8 fenêtres
            char_name = f"PERSO{i+1}"
            self.window_manager.add_character(char_name, window.hwnd, i)
            print(f"  [{i+1}] {window.title} → {char_name}")
        
        print("\n💡 Pour personnaliser les noms, éditez le fichier config.json")
    
    def _load_config(self, config: dict):
        """Charge la configuration depuis un dictionnaire."""
        # Charger la configuration du window manager
        if "window_manager" in config:
            self.window_manager.from_dict(config["window_manager"])
        
        # Charger la configuration des hotkeys
        if "hotkeys" in config:
            self.hotkey_manager.from_dict(config["hotkeys"])
        
        # Charger la configuration de l'overlay
        if "overlay" in config:
            self.overlay.from_dict(config["overlay"])
    
    def _save_config(self):
        """Sauvegarde la configuration actuelle."""
        config = self.config_manager.get_full_config(
            self.window_manager.to_dict(),
            self.hotkey_manager.to_dict(),
            self.overlay.to_dict()
        )
        self.config_manager.save(config)
    
    def _update_overlay(self):
        """Met à jour l'affichage de l'overlay."""
        if not self.overlay.root:
            return
        
        char_list = self.window_manager.get_character_list()
        current_char = self.window_manager.get_current_character()
        next_char = self.window_manager.get_next_character()
        
        current_index = self.window_manager.current_index
        next_index = (current_index + 1) % len(char_list) if char_list else 0
        
        self.overlay.update_display(char_list, current_index, next_index)
    
    def _toggle_overlay(self):
        """Affiche/masque l'overlay."""
        self.overlay.toggle()
        self._save_config()
    
    def _create_tray_icon(self):
        """Crée l'icône dans la barre système."""
        # Créer une icône simple
        image = Image.new('RGB', (64, 64), color='#1a1a1a')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='#00ff00', outline='#ffffff')
        
        menu = pystray.Menu(
            item('DOFUS Window Switcher', lambda: None, enabled=False),
            item('---', lambda: None),
            item('Afficher overlay', lambda: self.overlay.show()),
            item('Masquer overlay', lambda: self.overlay.hide()),
            item('---', lambda: None),
            item('Quitter', lambda: self.quit())
        )
        
        self.tray_icon = pystray.Icon("dofus_switcher", image, "DOFUS Window Switcher", menu)
    
    def _run_tray_icon(self):
        """Lance l'icône system tray dans un thread séparé."""
        if self.tray_icon:
            self.tray_icon.run()
    
    def run(self):
        """Lance l'application."""
        self.running = True
        
        # Créer et lancer l'icône system tray dans un thread
        self._create_tray_icon()
        tray_thread = threading.Thread(target=self._run_tray_icon, daemon=True)
        tray_thread.start()
        
        # Boucle de mise à jour périodique
        def update_loop():
            while self.running:
                # Mettre à jour l'overlay toutes les secondes
                self._update_overlay()
                time.sleep(1)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        # Lancer la boucle principale de l'overlay (bloquant)
        try:
            if self.overlay.root:
                self.overlay.run()
            else:
                # Si l'overlay n'a pas pu être créé, garder l'app en vie
                print("\n⚠ Overlay non disponible - Mode sans GUI")
                print("Les raccourcis clavier fonctionnent toujours.")
                print("Appuyez sur Ctrl+Alt+Q pour quitter\n")
                while self.running:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.quit()
        except Exception as e:
            print(f"Erreur overlay: {e}")
            self.quit()
    
    def quit(self):
        """Quitte l'application proprement."""
        print("\n👋 Arrêt de l'application...")
        self.running = False
        
        # Sauvegarder la configuration
        self._save_config()
        print("✓ Configuration sauvegardée")
        
        # Désenregistrer les hotkeys
        self.hotkey_manager.unregister_all()
        print("✓ Raccourcis désactivés")
        
        # Arrêter l'overlay
        self.overlay.destroy()
        
        # Arrêter l'icône system tray
        if self.tray_icon:
            self.tray_icon.stop()
        
        print("✓ Au revoir!")
        sys.exit(0)


def main():
    """Fonction principale."""
    try:
        app = DofusWindowSwitcher()
        app.initialize()
        app.run()
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
