"""Fenêtre de configuration GUI pour gérer l'ordre des personnages."""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from typing import List, Callable, Optional, Dict
from window_detector import WindowDetector, WindowInfo


class ConfigWindow:
    """Fenêtre de configuration pour assigner les personnages."""
    
    def __init__(self, detector: WindowDetector, on_save: Callable, allow_launch: bool = True, current_hotkeys: Optional[Dict] = None, previous_config: Optional[Dict] = None):
        self.detector = detector
        self.on_save = on_save
        self.allow_launch = allow_launch
        self.current_hotkeys = current_hotkeys or {}
        self.previous_config = previous_config or {}
        self.root: Optional[tk.Tk] = None
        self.windows: List[WindowInfo] = []
        self.position_combos: List[ttk.Combobox] = []
        self.name_entries: List[tk.Entry] = []
        
        # Widgets pour les raccourcis
        self.next_key_entry: Optional[tk.Entry] = None
        self.previous_key_entry: Optional[tk.Entry] = None
        
    def show(self):
        """Affiche la fenêtre de configuration."""
        # Détecter les fenêtres DOFUS
        self.windows = self.detector.detect_windows()
        
        if not self.windows:
            messagebox.showerror("Erreur", "Aucune fenêtre DOFUS détectée!\nLancez DOFUS d'abord.")
            return
        
        self.root = tk.Tk()
        self.root.title("Configuration DOFUS Window Switcher")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2a2a2a", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🎮 Configuration des Personnages",
            font=("Arial", 16, "bold"),
            fg="#00ff00",
            bg="#2a2a2a"
        )
        title.pack(pady=15)
        
        # Instructions
        info_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        info_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        info_text = tk.Label(
            info_frame,
            text="Assignez chaque fenêtre DOFUS à une position (ordre d'initiative) et indiquez sa classe.",
            font=("Arial", 10),
            bg="#f0f0f0",
            wraplength=650
        )
        info_text.pack()
        
        # Canvas avec scrollbar
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Fonction pour gérer le scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind la molette de souris au canvas
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Liste des fenêtres
        self.position_combos = []
        self.name_entries = []
        
        positions = [f"Position {i+1} (F{i+1})" for i in range(8)]
        
        for i, window in enumerate(self.windows[:8]):  # Max 8 fenêtres
            frame = tk.Frame(scrollable_frame, bg="white", pady=5)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Titre de la fenêtre (nom du perso détecté)
            window_label = tk.Label(
                frame,
                text=f"🪟 {window.title}",
                font=("Arial", 9),
                bg="white",
                anchor="w",
                width=50
            )
            window_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
            
            # Position
            pos_label = tk.Label(frame, text="Position:", font=("Arial", 9), bg="white")
            pos_label.grid(row=1, column=0, sticky="w", padx=(0, 10))
            
            pos_combo = ttk.Combobox(frame, values=positions, state="readonly", width=18)
            
            # Essayer de récupérer la position précédente pour ce personnage
            char_name = self._extract_character_name(window.title)
            prev_position = self._get_previous_position(char_name)
            
            if prev_position is not None:
                # Utiliser la position précédente
                pos_combo.current(prev_position)
            else:
                # Défaut: ordre de détection
                pos_combo.current(i)
            
            pos_combo.grid(row=1, column=1, sticky="w")
            self.position_combos.append(pos_combo)
            
            # Classe du personnage
            name_label = tk.Label(frame, text="Classe:", font=("Arial", 9), bg="white")
            name_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
            
            name_entry = tk.Entry(frame, width=20, font=("Arial", 9))
            name_entry.insert(0, self._extract_character_name(window.title))
            name_entry.grid(row=2, column=1, sticky="w", pady=(5, 0))
            self.name_entries.append(name_entry)
            
            # Séparateur
            sep = ttk.Separator(scrollable_frame, orient="horizontal")
            sep.pack(fill=tk.X, padx=10, pady=5)
        
        # Section Raccourcis
        hotkeys_frame = tk.Frame(scrollable_frame, bg="white", pady=10)
        hotkeys_frame.pack(fill=tk.X, padx=10, pady=10)
        
        hotkeys_title = tk.Label(
            hotkeys_frame,
            text="⌨️ Raccourcis de navigation",
            font=("Arial", 11, "bold"),
            bg="white",
            anchor="w"
        )
        hotkeys_title.pack(anchor="w", pady=(0, 10))
        
        # Touche "Suivant"
        next_frame = tk.Frame(hotkeys_frame, bg="white")
        next_frame.pack(fill=tk.X, pady=5)
        
        next_label = tk.Label(
            next_frame,
            text="Personnage suivant:",
            font=("Arial", 9),
            bg="white",
            width=20,
            anchor="w"
        )
        next_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_key_entry = tk.Entry(next_frame, width=15, font=("Arial", 9))
        self.next_key_entry.insert(0, self.current_hotkeys.get("next_key", "`"))
        self.next_key_entry.pack(side=tk.LEFT)
        
        next_hint = tk.Label(
            next_frame,
            text="(ex: tab, `, \u00e9, a, etc.)",
            font=("Arial", 8),
            bg="white",
            fg="#666666"
        )
        next_hint.pack(side=tk.LEFT, padx=(10, 0))
        
        # Touche "Précédent"
        prev_frame = tk.Frame(hotkeys_frame, bg="white")
        prev_frame.pack(fill=tk.X, pady=5)
        
        prev_label = tk.Label(
            prev_frame,
            text="Personnage précédent:",
            font=("Arial", 9),
            bg="white",
            width=20,
            anchor="w"
        )
        prev_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.previous_key_entry = tk.Entry(prev_frame, width=15, font=("Arial", 9))
        self.previous_key_entry.insert(0, self.current_hotkeys.get("previous_key", "\\"))
        self.previous_key_entry.pack(side=tk.LEFT)
        
        prev_hint = tk.Label(
            prev_frame,
            text="(ex: shift+tab, \\, &, z, etc.)",
            font=("Arial", 8),
            bg="white",
            fg="#666666"
        )
        prev_hint.pack(side=tk.LEFT, padx=(10, 0))
        
        # Info supplémentaire
        info_hint = tk.Label(
            hotkeys_frame,
            text="💡 Pour les combinaisons, utilisez '+' (ex: shift+tab, ctrl+n)",
            font=("Arial", 8, "italic"),
            bg="white",
            fg="#0066cc",
            anchor="w"
        )
        info_hint.pack(anchor="w", pady=(10, 0))
        
        # Boutons
        button_frame = tk.Frame(self.root, bg="#f0f0f0", pady=15)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Annuler",
            command=self.root.destroy,
            font=("Arial", 10),
            bg="#cccccc",
            width=12,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=(20, 10))
        
        # Boutons conditionnels selon le mode
        if self.allow_launch:
            # Bouton Sauvegarder & Lancer (action principale)
            save_launch_btn = tk.Button(
                button_frame,
                text="🚀 Sauvegarder & Lancer",
                command=self._save_and_launch,
                font=("Arial", 10, "bold"),
                bg="#ff6600",
                fg="white",
                width=20,
                cursor="hand2"
            )
            save_launch_btn.pack(side=tk.RIGHT, padx=(10, 20))
            
            # Bouton pour lancer l'application (si déjà config)
            launch_btn = tk.Button(
                button_frame,
                text="▶ Lancer",
                command=self._launch_app,
                font=("Arial", 9),
                bg="#0066ff",
                fg="white",
                width=10,
                cursor="hand2"
            )
            launch_btn.pack(side=tk.RIGHT, padx=(10, 5))
        
        # Bouton Sauvegarder (toujours présent)
        save_btn = tk.Button(
            button_frame,
            text="💾 Sauvegarder & Appliquer" if not self.allow_launch else "Sauvegarder",
            command=self._save_config,
            font=("Arial", 10, "bold") if not self.allow_launch else ("Arial", 9),
            bg="#00cc00",
            fg="white",
            width=20 if not self.allow_launch else 10,
            cursor="hand2"
        )
        save_btn.pack(side=tk.RIGHT, padx=(10, 20 if not self.allow_launch else 5))
        
        self.root.mainloop()
    
    def _extract_character_name(self, title: str) -> str:
        """Extrait le nom de la classe depuis le titre de la fenêtre."""
        # Format: "NomPerso - Classe - Version"
        parts = title.split(" - ")
        if len(parts) >= 2:
            # Retourner la classe (2ème élément) au lieu du nom
            return parts[1].strip()
        return "Perso"
    
    def _get_previous_position(self, character_name: str) -> Optional[int]:
        """Récupère la position précédente d'un personnage depuis la config."""
        if not self.previous_config:
            return None
        
        characters = self.previous_config.get("characters", [])
        for char in characters:
            # Comparer les noms (ignorer la casse)
            if char.get("name", "").lower() == character_name.lower():
                return char.get("position")
        
        return None
    
    def _save_and_launch(self):
        """Sauvegarde la configuration et lance l'application."""
        # D'abord sauvegarder
        if self._save_config_internal():
            # Puis lancer
            self._launch_app()
    
    def _launch_app(self):
        """Lance l'application principale."""
        try:
            # Fermer la fenêtre de config
            if self.root:
                self.root.destroy()
            
            # Importer et lancer l'application principale directement
            from main import DofusWindowSwitcher
            app = DofusWindowSwitcher()
            app.initialize()
            app.run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Impossible de lancer l'application:\n{e}")
    
    def _save_config_internal(self) -> bool:
        """Sauvegarde la configuration (version interne sans message)."""
        # Vérifier les doublons de position
        positions_used = []
        for combo in self.position_combos:
            pos = combo.current()
            if pos in positions_used:
                messagebox.showerror("Erreur", "Deux fenêtres ne peuvent pas avoir la même position!")
                return False
            positions_used.append(pos)
        
        # Créer la liste des personnages
        characters = []
        for i, window in enumerate(self.windows[:8]):
            if i < len(self.position_combos):
                position = self.position_combos[i].current()
                name = self.name_entries[i].get().strip() or f"Perso{position+1}"
                
                characters.append({
                    "name": name,
                    "hwnd": window.hwnd,
                    "position": position
                })
        
        # Récupérer les raccourcis personnalisés
        hotkeys = {
            "next_key": self.next_key_entry.get().strip() if self.next_key_entry else "`",
            "previous_key": self.previous_key_entry.get().strip() if self.previous_key_entry else "\\"
        }
        
        # Appeler le callback de sauvegarde avec les personnages ET les raccourcis
        self.on_save(characters, hotkeys)
        return True
    
    def _save_config(self):
        """Sauvegarde la configuration avec message de confirmation."""
        if self._save_config_internal():
            messagebox.showinfo("Succès", "Configuration sauvegardée!")
