"""Fenêtre de configuration GUI pour gérer l'ordre des personnages."""
import customtkinter as ctk
from tkinter import messagebox
import ctypes
import subprocess
import sys
from typing import List, Callable, Optional, Dict
from window_detector import WindowDetector, WindowInfo


# =============================================================================
# Palette Dofus 3 — Dark Theme
# =============================================================================
COLORS = {
    "bg_primary": "#1a1a1a",       # Fond principal (noir profond)
    "bg_secondary": "#222222",     # Fond secondaire
    "bg_card": "#2d2d2d",          # Fond carte/widget
    "bg_input": "#1e1e1e",         # Fond champs de saisie
    "accent": "#8b2252",           # Accent principal (bordeaux)
    "accent_hover": "#a0325f",     # Accent hover
    "text_primary": "#e0e0e0",     # Texte principal
    "text_secondary": "#777777",   # Texte secondaire
    "border": "#3a3a3a",           # Bordures
    "success": "#4ade80",          # Vert succès
    "warning": "#fbbf24",          # Orange warning
    "btn_cancel": "#3a3a3a",       # Bouton annuler
    "btn_cancel_hover": "#4a4a4a", # Bouton annuler hover
}


class ConfigWindow:
    """Fenêtre de configuration pour assigner les personnages."""
    
    def __init__(self, detector: WindowDetector, on_save: Callable, allow_launch: bool = True, current_hotkeys: Optional[Dict] = None, previous_config: Optional[Dict] = None):
        self.detector = detector
        self.on_save = on_save
        self.allow_launch = allow_launch
        self.current_hotkeys = current_hotkeys or {}
        self.previous_config = previous_config or {}
        self.root: Optional[ctk.CTk] = None
        self.windows: List[WindowInfo] = []
        self.position_menus: List[ctk.CTkOptionMenu] = []
        self.position_vars: List[ctk.StringVar] = []
        self.name_entries: List[ctk.CTkEntry] = []
        
        # Widgets pour les raccourcis
        self.next_key_entry: Optional[ctk.CTkEntry] = None
        self.previous_key_entry: Optional[ctk.CTkEntry] = None
        self.wheel_key_entry: Optional[ctk.CTkEntry] = None
        
    def show(self):
        """Affiche la fenêtre de configuration."""
        # Détecter les fenêtres DOFUS
        self.windows = self.detector.detect_windows()
        
        if not self.windows:
            messagebox.showerror("Erreur", "Aucune fenêtre DOFUS détectée!\nLancez DOFUS d'abord.")
            return
        
        # Configuration CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = ctk.CTk()
        self.root.title("DOFUS Window Switcher — Configuration")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # Retirer la barre de titre système
        self.root.configure(fg_color=COLORS["bg_primary"])
        
        # Centrer la fenêtre à l'écran
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 750) // 2
        y = (self.root.winfo_screenheight() - 700) // 2
        self.root.geometry(f"750x700+{x}+{y}")
        
        # Réafficher dans la taskbar + forcer le focus (Win32)
        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        # Ajouter WS_EX_APPWINDOW pour apparaître dans la taskbar
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        # Forcer au premier plan (topmost temporaire)
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.after(200, lambda: self.root.attributes('-topmost', False))
        
        # =================================================================
        # Header (draggable + bouton fermer)
        # =================================================================
        header_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["accent"],
            corner_radius=0,
            height=60
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Drag pour déplacer la fenêtre
        self._offset_x = 0
        self._offset_y = 0
        header_frame.bind("<Button-1>", self._start_move)
        header_frame.bind("<B1-Motion>", self._do_move)
        
        ctk.CTkLabel(
            header_frame,
            text="🎮  Configuration des Personnages",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=20, pady=15)
        
        # Bouton fermer (✕)
        ctk.CTkButton(
            header_frame,
            text="✕",
            command=self.root.destroy,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            hover_color="#a0325f",
            text_color="#ffffff",
            width=40,
            height=40,
            corner_radius=8
        ).pack(side="right", padx=10, pady=10)
        
        # =================================================================
        # Instructions
        # =================================================================
        info_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["bg_secondary"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"]
        )
        info_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            info_frame,
            text="Assignez chaque fenêtre DOFUS à une position (ordre d'initiative) et indiquez sa classe.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            wraplength=680
        ).pack(padx=15, pady=10)
        
        # =================================================================
        # Zone scrollable — liste des personnages
        # =================================================================
        scroll_frame = ctk.CTkScrollableFrame(
            self.root,
            fg_color=COLORS["bg_primary"],
            corner_radius=0,
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["border"]
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.position_menus = []
        self.position_vars = []
        self.name_entries = []
        
        positions = [f"Position {i+1} (F{i+1})" for i in range(8)]
        
        for i, window in enumerate(self.windows[:8]):
            card = ctk.CTkFrame(
                scroll_frame,
                fg_color=COLORS["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color=COLORS["border"]
            )
            card.pack(fill="x", pady=5)
            
            # Titre de la fenêtre détectée
            ctk.CTkLabel(
                card,
                text=f"🪟  {window.title}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(fill="x", padx=15, pady=(12, 8))
            
            # Ligne position + classe
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=(0, 12))
            
            # Position
            ctk.CTkLabel(
                row_frame,
                text="Position :",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"]
            ).pack(side="left", padx=(0, 8))
            
            char_name = self._extract_character_name(window.title)
            prev_position = self._get_previous_position(char_name)
            default_pos = prev_position if prev_position is not None else i
            
            pos_var = ctk.StringVar(value=positions[min(default_pos, 7)])
            pos_menu = ctk.CTkOptionMenu(
                row_frame,
                variable=pos_var,
                values=positions,
                width=180,
                height=30,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["bg_input"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                dropdown_fg_color=COLORS["bg_card"],
                dropdown_hover_color=COLORS["accent"],
                dropdown_text_color=COLORS["text_primary"],
                text_color=COLORS["text_primary"]
            )
            pos_menu.pack(side="left", padx=(0, 20))
            self.position_menus.append(pos_menu)
            self.position_vars.append(pos_var)
            
            # Classe du personnage
            ctk.CTkLabel(
                row_frame,
                text="Classe :",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"]
            ).pack(side="left", padx=(0, 8))
            
            name_entry = ctk.CTkEntry(
                row_frame,
                width=160,
                height=30,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["bg_input"],
                border_color=COLORS["border"],
                text_color=COLORS["text_primary"],
                placeholder_text="Ex: Roublard",
                placeholder_text_color=COLORS["text_secondary"]
            )
            name_entry.insert(0, char_name)
            name_entry.pack(side="left")
            self.name_entries.append(name_entry)
        
        # =================================================================
        # Section Raccourcis
        # =================================================================
        hotkeys_card = ctk.CTkFrame(
            scroll_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        hotkeys_card.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(
            hotkeys_card,
            text="⌨️  Raccourcis de navigation",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=15, pady=(12, 10))
        
        # Touche suivant
        next_frame = ctk.CTkFrame(hotkeys_card, fg_color="transparent")
        next_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(
            next_frame,
            text="Personnage suivant :",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=180,
            anchor="w"
        ).pack(side="left")
        
        self.next_key_entry = ctk.CTkEntry(
            next_frame,
            width=120,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.next_key_entry.insert(0, self.current_hotkeys.get("next_key", "`"))
        self.next_key_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            next_frame,
            text="(ex: tab, `, é, a)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        # Touche précédent
        prev_frame = ctk.CTkFrame(hotkeys_card, fg_color="transparent")
        prev_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(
            prev_frame,
            text="Personnage précédent :",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=180,
            anchor="w"
        ).pack(side="left")
        
        self.previous_key_entry = ctk.CTkEntry(
            prev_frame,
            width=120,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.previous_key_entry.insert(0, self.current_hotkeys.get("previous_key", "\\"))
        self.previous_key_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            prev_frame,
            text="(ex: shift+tab, \\, &, z)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        # Touche roue de sélection
        wheel_frame = ctk.CTkFrame(hotkeys_card, fg_color="transparent")
        wheel_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(
            wheel_frame,
            text="Roue de sélection :",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            width=180,
            anchor="w"
        ).pack(side="left")
        
        self.wheel_key_entry = ctk.CTkEntry(
            wheel_frame,
            width=120,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.wheel_key_entry.insert(0, self.current_hotkeys.get("wheel_key", "ctrl+alt+w"))
        self.wheel_key_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            wheel_frame,
            text="(ex: ctrl+alt+w)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        # Hint
        ctk.CTkLabel(
            hotkeys_card,
            text="💡 Pour les combinaisons, utilisez '+' (ex: shift+tab, ctrl+n)",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["accent"],
            anchor="w"
        ).pack(fill="x", padx=15, pady=(8, 12))
        
        # =================================================================
        # Boutons
        # =================================================================
        button_frame = ctk.CTkFrame(
            self.root,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            height=65
        )
        button_frame.pack(fill="x", side="bottom")
        button_frame.pack_propagate(False)
        
        # Annuler
        ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=self.root.destroy,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["btn_cancel"],
            hover_color=COLORS["btn_cancel_hover"],
            text_color=COLORS["text_primary"],
            width=120,
            height=36,
            corner_radius=8
        ).pack(side="left", padx=(20, 10), pady=14)
        
        if self.allow_launch:
            # Sauvegarder & Lancer
            ctk.CTkButton(
                button_frame,
                text="🚀 Sauvegarder & Lancer",
                command=self._save_and_launch,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color="#ffffff",
                width=200,
                height=36,
                corner_radius=8
            ).pack(side="right", padx=(10, 20), pady=14)
            
            # Lancer
            ctk.CTkButton(
                button_frame,
                text="▶ Lancer",
                command=self._launch_app,
                font=ctk.CTkFont(size=11),
                fg_color="#1a6b3c",
                hover_color="#228b4a",
                text_color="#ffffff",
                width=100,
                height=36,
                corner_radius=8
            ).pack(side="right", padx=5, pady=14)
        
        # Sauvegarder (toujours présent)
        save_text = "💾 Sauvegarder & Appliquer" if not self.allow_launch else "Sauvegarder"
        save_width = 200 if not self.allow_launch else 120
        ctk.CTkButton(
            button_frame,
            text=save_text,
            command=self._save_config,
            font=ctk.CTkFont(size=12, weight="bold") if not self.allow_launch else ctk.CTkFont(size=11),
            fg_color=COLORS["success"] if not self.allow_launch else "#1a6b3c",
            hover_color="#3bcc6e" if not self.allow_launch else "#228b4a",
            text_color="#000000" if not self.allow_launch else "#ffffff",
            width=save_width,
            height=36,
            corner_radius=8
        ).pack(side="right", padx=5, pady=14)
        
        self.root.mainloop()
    
    def _start_move(self, event):
        """Début du déplacement de la fenêtre."""
        self._offset_x = event.x
        self._offset_y = event.y
    
    def _do_move(self, event):
        """Déplacement de la fenêtre par drag du header."""
        x = self.root.winfo_x() + event.x - self._offset_x
        y = self.root.winfo_y() + event.y - self._offset_y
        self.root.geometry(f"+{x}+{y}")
    
    def _extract_character_name(self, title: str) -> str:
        """Extrait le nom de la classe depuis le titre de la fenêtre."""
        # Format: "NomPerso - Classe - Version"
        parts = title.split(" - ")
        if len(parts) >= 2:
            return parts[1].strip()
        return "Perso"
    
    def _get_previous_position(self, character_name: str) -> Optional[int]:
        """Récupère la position précédente d'un personnage depuis la config."""
        if not self.previous_config:
            return None
        
        characters = self.previous_config.get("characters", [])
        for char in characters:
            if char.get("name", "").lower() == character_name.lower():
                return char.get("position")
        
        return None
    
    def _get_position_index(self, pos_var: ctk.StringVar) -> int:
        """Extrait l'index de position depuis la valeur du menu."""
        value = pos_var.get()
        # Format: "Position X (FX)"
        try:
            return int(value.split(" ")[1]) - 1
        except (IndexError, ValueError):
            return 0
    
    def _save_and_launch(self):
        """Sauvegarde la configuration et lance l'application."""
        if self._save_config_internal():
            self._launch_app()
    
    def _launch_app(self):
        """Lance l'application principale."""
        try:
            if self.root:
                self.root.destroy()
            
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
        for pos_var in self.position_vars:
            pos = self._get_position_index(pos_var)
            if pos in positions_used:
                messagebox.showerror("Erreur", "Deux fenêtres ne peuvent pas avoir la même position!")
                return False
            positions_used.append(pos)
        
        # Créer la liste des personnages
        characters = []
        for i, window in enumerate(self.windows[:8]):
            if i < len(self.position_vars):
                position = self._get_position_index(self.position_vars[i])
                name = self.name_entries[i].get().strip() or f"Perso{position+1}"
                
                characters.append({
                    "name": name,
                    "hwnd": window.hwnd,
                    "position": position
                })
        
        # Récupérer les raccourcis personnalisés
        hotkeys = {
            "next_key": self.next_key_entry.get().strip() if self.next_key_entry else "`",
            "previous_key": self.previous_key_entry.get().strip() if self.previous_key_entry else "\\",
            "wheel_key": self.wheel_key_entry.get().strip() if self.wheel_key_entry else "ctrl+alt+w"
        }
        
        self.on_save(characters, hotkeys)
        return True
    
    def _save_config(self):
        """Sauvegarde la configuration avec message de confirmation."""
        if self._save_config_internal():
            messagebox.showinfo("Succès", "Configuration sauvegardée!")
