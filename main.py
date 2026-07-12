"""Point d'entrée principal de l'application DOFUS Window Switcher."""
import os
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
from character_wheel import CharacterWheel
from config_manager import ConfigManager
from font_loader import load_custom_fonts


def _get_base_dir() -> str:
    """Retourne le répertoire de base (compatible PyInstaller)."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


class DofusWindowSwitcher:
    """Application principale pour le switching de fenêtres DOFUS."""
    
    def __init__(self):
        # Composants principaux
        self.detector = WindowDetector()
        self.window_manager = WindowManager(self.detector)
        self.hotkey_manager = HotkeyManager(self.window_manager)
        self.overlay = OverlayWindow()
        self.wheel = CharacterWheel()
        self.config_manager = ConfigManager()
        
        # System tray
        self.tray_icon: Optional[pystray.Icon] = None
        self.running = False
        
        # Configurer les callbacks des hotkeys
        self.hotkey_manager.on_toggle_overlay = self._toggle_overlay
        self.hotkey_manager.on_quit = self.quit
        self.hotkey_manager.on_open_config = self._open_config
        self.hotkey_manager.on_toggle_wheel = self._toggle_wheel
        
    def initialize(self):
        """Initialise l'application."""
        load_custom_fonts()
        print("DOFUS Window Switcher - Initialisation...")
        
        # Charger la configuration
        config = self.config_manager.load()
        
        if config:
            print("Configuration chargée")
            self._load_config(config)
            # Ré-associer les fenêtres par nom de personnage (les hwnd sauvegardés
            # sont périmés si DOFUS a redémarré depuis)
            rematched = self.window_manager.rematch_windows()
            if rematched:
                print(f"{rematched} fenêtre(s) ré-associée(s) automatiquement")
                self._save_config()
        else:
            print("Premier lancement - Configuration initiale")
            self._first_time_setup()
        
        # Créer l'overlay
        self.overlay.create_window()
        
        # Créer la roue de sélection (sur le même root que l'overlay)
        if self.overlay.root:
            self.wheel.create_window(self.overlay.root)
            self.wheel.on_select = self._on_wheel_select
        
        # Enregistrer les hotkeys
        self.hotkey_manager.register_all()
        print("Raccourcis clavier enregistrés")
        
        # Mettre à jour l'overlay
        self._update_overlay()
        
        print("Initialisation terminée")
        print("\nRaccourcis:")
        print("  F1-F8      : Switch vers le personnage 1-8")
        print("  `          : Personnage suivant")
        print("  \\          : Personnage précédent")
        print("  Ctrl+Alt+O : Afficher/masquer l'overlay")
        print("  Ctrl+Alt+C : Modifier la configuration")
        print("  Ctrl+Alt+W : Roue de sélection")
        print("  Ctrl+Alt+Q : Quitter")
    
    def _first_time_setup(self):
        """Configuration initiale au premier lancement."""
        print("\nDétection des fenêtres DOFUS...")
        windows = self.detector.detect_windows()
        
        if not windows:
            print("Aucune fenêtre DOFUS détectée!")
            print("  Assurez-vous que DOFUS est lancé et réessayez.")
            return
        
        print(f"{len(windows)} fenêtre(s) DOFUS détectée(s)")
        
        # Créer une configuration par défaut avec les fenêtres détectées
        for i, window in enumerate(windows[:8]):  # Max 8 fenêtres
            # Extraire le nom de classe depuis le titre de la fenêtre
            char_name = self._extract_character_class(window.title, i+1)
            character = self.detector.extract_character_from_title(window.title)
            self.window_manager.add_character(char_name, window.hwnd, i, character)
            print(f"  [{i+1}] {window.title} → {char_name}")
        
        print("\nPour personnaliser les noms, utilisez Ctrl+Alt+C ou lancez configure.py")
    
    def _extract_character_class(self, title: str, fallback_number: int) -> str:
        """Extrait le nom de la classe depuis le titre de la fenêtre DOFUS."""
        # Format attendu: "NomPerso - Classe - Version"
        parts = title.split(" - ")
        if len(parts) >= 2:
            # Retourner la classe (2ème élément)
            return parts[1].strip()
        # Fallback si le format n'est pas reconnu
        return f"PERSO{fallback_number}"
    
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
    
    def _toggle_wheel(self):
        """Affiche/masque la roue de sélection."""
        if not self.overlay.root:
            return
        char_list = self.window_manager.get_character_list()
        current_index = self.window_manager.current_index
        # Passer par root.after pour rester thread-safe (appelé depuis thread keyboard)
        self.overlay.root.after(0, lambda: self.wheel.toggle(char_list, current_index))
    
    def _on_wheel_select(self, position: int):
        """Callback quand un personnage est sélectionné via la roue."""
        self.window_manager.switch_to_position(position)
        self._update_overlay()
    
    def reload_config(self):
        """Recharge la configuration depuis le fichier sans redémarrer l'app."""
        print("Rechargement de la configuration...")
        config = self.config_manager.load()
        
        if config:
            self._load_config(config)
            self._update_overlay()
            print("✓ Configuration rechargée avec succès")
        else:
            print("Impossible de recharger la configuration")
    
    def _open_config(self):
        """Ouvre la fenêtre de configuration pour modifier l'ordre."""
        from config_gui import ConfigWindow
        
        def on_save(characters, hotkeys):
            """Callback appelé quand la config est sauvegardée."""
            # Mettre à jour le window_manager avec les nouveaux personnages
            self.window_manager.characters.clear()
            for char in characters:
                self.window_manager.add_character(
                    char["name"],
                    char["hwnd"],
                    char["position"],
                    char.get("character", "")
                )
            
            # Mettre à jour les raccourcis clavier
            if hotkeys.get("next_key"):
                self.hotkey_manager.next_key = hotkeys["next_key"]
            if hotkeys.get("previous_key"):
                self.hotkey_manager.previous_key = hotkeys["previous_key"]
            if hotkeys.get("wheel_key"):
                self.hotkey_manager.wheel_key = hotkeys["wheel_key"]
            
            # Ré-enregistrer les hotkeys avec les nouvelles touches
            self.hotkey_manager.register_all()
            
            # Sauvegarder la configuration
            self._save_config()
            
            # Recharger pour mettre à jour l'overlay
            self.reload_config()
            
            print(f"Raccourcis mis à jour: Suivant='{hotkeys.get('next_key')}', Précédent='{hotkeys.get('previous_key')}'")
        
        # Récupérer les hotkeys actuels et la config du window manager
        current_hotkeys = self.hotkey_manager.to_dict()
        previous_window_config = self.window_manager.to_dict()
        
        # Créer et afficher la fenêtre de configuration dans un thread séparé
        def show_config():
            config_window = ConfigWindow(
                self.detector, 
                on_save, 
                allow_launch=False, 
                current_hotkeys=current_hotkeys,
                previous_config=previous_window_config
            )
            config_window.show()
        
        config_thread = threading.Thread(target=show_config, daemon=False)
        config_thread.start()
    
    def _create_tray_icon(self):
        """Crée l'icône dans la barre système."""
        icon_path = os.path.join(_get_base_dir(), "DWM.ico")
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            # Fallback si l'icône n'est pas trouvée
            image = Image.new('RGB', (64, 64), color='#1a1a1a')
            draw = ImageDraw.Draw(image)
            draw.rectangle([16, 16, 48, 48], fill='#8b2252', outline='#e0e0e0')
        
        menu = pystray.Menu(
            item('DOFUS Window Switcher', lambda: None, enabled=False),
            item('---', lambda: None),
            item('Modifier la configuration', lambda: self._open_config()),
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
            tick = 0
            while self.running:
                # Suivre la fenêtre réellement active (alt-tab, clic direct)
                self.window_manager.sync_with_foreground()

                # Toutes les 5s : re-matcher les fenêtres périmées (DOFUS relancé)
                if tick % 5 == 0 and self.window_manager.has_invalid_windows():
                    rematched = self.window_manager.rematch_windows()
                    if rematched:
                        print(f"{rematched} fenêtre(s) ré-associée(s) automatiquement")
                        self._save_config()

                # Mettre à jour l'overlay toutes les secondes
                self._update_overlay()
                time.sleep(1)
                tick += 1
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        # Lancer la boucle principale de l'overlay (bloquant)
        try:
            if self.overlay.root:
                self.overlay.run()
            else:
                # Si l'overlay n'a pas pu être créé, garder l'app en vie
                print("\nOverlay non disponible - Mode sans GUI")
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
        self.running = False
        
        # Sauvegarder la configuration
        try:
            self._save_config()
        except:
            pass
        
        # Désenregistrer les hotkeys
        try:
            self.hotkey_manager.unregister_all()
        except:
            pass
        
        # Arrêter l'icône system tray
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        
        # Arrêter l'overlay (IMPORTANT: fermer le mainloop tkinter)
        if self.overlay.root:
            try:
                self.overlay.root.quit()  # Arrête le mainloop
                self.overlay.root.destroy()  # Détruit la fenêtre
            except:
                pass
        
        # Forcer la sortie
        import os
        os._exit(0)


def main():
    """Fonction principale."""
    try:
        app = DofusWindowSwitcher()
        app.initialize()
        app.run()
    except Exception as e:
        print(f"\nErreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
