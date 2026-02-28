"""Module pour l'overlay visuel affichant l'ordre des personnages."""
import tkinter as tk
from typing import List, Optional
import threading


class OverlayWindow:
    """Fenêtre overlay transparente affichant l'ordre des personnages."""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.visible = True
        
        # Configuration par défaut
        self.position_x = 100
        self.position_y = 100
        self.width = 855  # Augmenté de 800 à 1100 pour voir tous les noms
        self.height = 50
        self.opacity = 0.9
        self.font_size = 14
        
        # Données d'affichage
        self.characters: List[str] = []
        self.current_index = 0
        self.next_index = 0
        
        # Widgets
        self.labels: List[tk.Label] = []
        self.arrows: List[tk.Label] = []
        
        # Thread-safe update flag
        self._update_pending = False
        
    def create_window(self):
        """Crée la fenêtre overlay."""
        try:
            self.root = tk.Tk()
            self.root.title("DOFUS Window Switcher")
            
            # Configuration de la fenêtre
            self.root.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', self.opacity)
            self.root.overrideredirect(True)  # Pas de bordure de fenêtre
            
            # Fond semi-transparent
            self.root.configure(bg='#1a1a1a')
            
            # Frame principal
            self.main_frame = tk.Frame(self.root, bg='#1a1a1a')
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Frame pour les personnages
            self.char_frame = tk.Frame(self.main_frame, bg='#1a1a1a')
            self.char_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Binding pour déplacer la fenêtre
            self.root.bind('<Button-1>', self._start_move)
            self.root.bind('<B1-Motion>', self._do_move)
            
            # Variables pour le déplacement
            self._offset_x = 0
            self._offset_y = 0
            
            # Empêcher la fermeture par défaut
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)
            
            if not self.visible:
                self.root.withdraw()
        except Exception as e:
            print(f"Erreur lors de la création de l'overlay: {e}")
            self.root = None
    
    def _start_move(self, event):
        """Commence le déplacement de la fenêtre."""
        self._offset_x = event.x
        self._offset_y = event.y
    
    def _do_move(self, event):
        """Déplace la fenêtre."""
        x = self.root.winfo_x() + event.x - self._offset_x
        y = self.root.winfo_y() + event.y - self._offset_y
        self.root.geometry(f'+{x}+{y}')
        self.position_x = x
        self.position_y = y
    
    def update_display(self, characters: List[str], current_index: int, next_index: int):
        """Met à jour l'affichage des personnages."""
        self.characters = characters
        self.current_index = current_index
        self.next_index = next_index
        
        if self.root:
            self.root.after(0, self._refresh_display)
    
    def _calculate_optimal_width(self) -> int:
        """Calcule la largeur optimale en fonction du nombre de personnages."""
        if not self.characters:
            return 200  # Largeur minimale
        
        # Estimer la largeur nécessaire
        # Chaque caractère = ~8-10px selon la police
        # Padding = 8px de chaque côté = 16px
        # Crochets pour le perso actif = ~2 caractères supplémentaires
        # Flèche = ~20px
        
        char_width_estimate = 9  # pixels par caractère
        padding_per_label = 16  # padx=8 de chaque côté
        arrow_width = 20  # largeur de la flèche + espacement
        bracket_chars = 2  # crochets autour du perso actif
        
        total_width = 20  # padding du main_frame (10px de chaque côté)
        
        for i, char_name in enumerate(self.characters):
            # Longueur du nom + crochets si c'est le perso actif
            name_length = len(char_name)
            if i == self.current_index:
                name_length += bracket_chars
            
            # Largeur pour ce label
            total_width += (name_length * char_width_estimate) + padding_per_label
            
            # Ajouter la flèche sauf pour le premier
            if i > 0:
                total_width += arrow_width
        
        # Ajouter une marge de sécurité de 10%
        total_width = int(total_width * 1.1)
        
        # Limites min/max
        min_width = 200
        max_width = 1200
        
        return max(min_width, min(total_width, max_width))
    
    def _refresh_display(self):
        """Rafraîchit l'affichage (doit être appelé depuis le thread GUI)."""
        # Supprimer les anciens widgets
        for widget in self.char_frame.winfo_children():
            widget.destroy()
        
        self.labels.clear()
        self.arrows.clear()
        
        if not self.characters:
            return
        
        # Calculer et appliquer la largeur optimale
        optimal_width = self._calculate_optimal_width()
        if self.root and optimal_width != self.width:
            self.width = optimal_width
            self.root.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
        
        # Créer les labels pour chaque personnage
        for i, char_name in enumerate(self.characters):
            # Flèche entre les personnages
            if i > 0:
                arrow = tk.Label(
                    self.char_frame,
                    text="→",
                    font=("Arial", self.font_size),
                    fg="#666666",
                    bg="#1a1a1a"
                )
                arrow.pack(side=tk.LEFT, padx=2)
                self.arrows.append(arrow)
            
            # Déterminer le style du label
            if i == self.current_index:
                # Personnage actif (surligné en vert)
                fg_color = "#00ff00"
                bg_color = "#2a2a2a"
                text = f"[{char_name}]"
                font_weight = "bold"
            elif i == self.next_index:
                # Prochain personnage (orange)
                fg_color = "#ffaa00"
                bg_color = "#1a1a1a"
                text = char_name
                font_weight = "bold"
            else:
                # Autres personnages (gris)
                fg_color = "#aaaaaa"
                bg_color = "#1a1a1a"
                text = char_name
                font_weight = "normal"
            
            label = tk.Label(
                self.char_frame,
                text=text,
                font=("Arial", self.font_size, font_weight),
                fg=fg_color,
                bg=bg_color,
                padx=8,
                pady=4
            )
            label.pack(side=tk.LEFT)
            self.labels.append(label)
    
    def show(self):
        """Affiche l'overlay."""
        if self.root:
            self.root.deiconify()
            self.visible = True
    
    def hide(self):
        """Masque l'overlay."""
        if self.root:
            self.root.withdraw()
            self.visible = False
    
    def toggle(self):
        """Affiche/masque l'overlay."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def set_position(self, x: int, y: int):
        """Définit la position de l'overlay."""
        self.position_x = x
        self.position_y = y
        if self.root:
            self.root.geometry(f'+{x}+{y}')
    
    def set_opacity(self, opacity: float):
        """Définit l'opacité de l'overlay (0.0 - 1.0)."""
        self.opacity = max(0.0, min(1.0, opacity))
        if self.root:
            self.root.attributes('-alpha', self.opacity)
    
    def set_font_size(self, size: int):
        """Définit la taille de la police."""
        self.font_size = size
        self._refresh_display()
    
    def run(self):
        """Lance la boucle principale de l'interface."""
        if self.root:
            self.root.mainloop()
    
    def destroy(self):
        """Détruit la fenêtre overlay."""
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def to_dict(self):
        """Convertit la configuration en dictionnaire."""
        return {
            "enabled": self.visible,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "width": self.width,
            "height": self.height,
            "opacity": self.opacity,
            "font_size": self.font_size
        }
    
    def from_dict(self, data: dict):
        """Charge la configuration depuis un dictionnaire."""
        self.visible = data.get("enabled", True)
        self.position_x = data.get("position_x", 100)
        self.position_y = data.get("position_y", 100)
        self.width = data.get("width", 800)
        self.height = data.get("height", 60)
        self.opacity = data.get("opacity", 0.9)
        self.font_size = data.get("font_size", 14)
        
        if self.root:
            self.root.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
            self.root.attributes('-alpha', self.opacity)
