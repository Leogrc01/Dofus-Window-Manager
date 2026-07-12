"""Module pour l'overlay visuel affichant l'ordre des personnages."""
import tkinter as tk
from typing import Callable, List, Optional

from class_icons import get_class_icon

ICON_SIZE = 20  # Taille des icônes de classe dans l'overlay
BG_COLOR = "#1a1a1a"          # Fond du bandeau (palette Dofus 3)
TRANSPARENT_KEY = "#010101"   # Couleur-clé de transparence (comme la roue)
CORNER_RADIUS = 14            # Rayon des coins arrondis
CLICK_THRESHOLD = 5           # Déplacement max (px) pour qu'un relâchement compte comme un clic


class OverlayWindow:
    """Fenêtre overlay transparente affichant l'ordre des personnages."""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self._bg_rect: Optional[int] = None
        self.visible = True
        
        # Configuration par défaut
        self.position_x = 100
        self.position_y = 100
        self.width = 855  # Augmenté de 800 à 1100 pour voir tous les noms
        self.height = 50
        self.opacity = 0.9
        self.font_size = 16
        
        # Données d'affichage
        self.characters: List[str] = []
        self.current_index = 0
        self.next_index = 0
        self.skipped: List[bool] = []
        self._last_state = None  # Dernier état affiché (évite les rebuilds inutiles)

        # Callbacks (clic gauche = switch, clic droit = mort/vivant)
        self.on_character_click: Optional[Callable[[int], None]] = None
        self.on_character_toggle: Optional[Callable[[int], None]] = None
        
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
            
            # Coins arrondis : le fond de la fenêtre est transparent (couleur-clé),
            # un rectangle arrondi est dessiné sur le canvas sous les widgets
            self.root.configure(bg=TRANSPARENT_KEY)
            self.root.wm_attributes('-transparentcolor', TRANSPARENT_KEY)

            self.canvas = tk.Canvas(
                self.root,
                bg=TRANSPARENT_KEY,
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self._bg_rect: Optional[int] = None

            # Frame principal, posé sur le canvas
            self.main_frame = tk.Frame(self.canvas, bg=BG_COLOR)
            self.canvas.create_window(10, 10, window=self.main_frame, anchor='nw')

            # Frame pour les personnages
            self.char_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
            self.char_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Binding pour déplacer la fenêtre + détecter les clics
            self.root.bind('<Button-1>', self._start_move)
            self.root.bind('<B1-Motion>', self._do_move)
            self.root.bind('<ButtonRelease-1>', self._on_release)

            # Variables pour le déplacement
            self._offset_x = 0
            self._offset_y = 0
            self._press_x_root = 0
            self._press_y_root = 0
            self._drag_moved = False
            self._label_index = {}  # widget label → index du personnage
            
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
        self._press_x_root = event.x_root
        self._press_y_root = event.y_root
        self._drag_moved = False

    def _do_move(self, event):
        """Déplace la fenêtre."""
        if (abs(event.x_root - self._press_x_root) > CLICK_THRESHOLD
                or abs(event.y_root - self._press_y_root) > CLICK_THRESHOLD):
            self._drag_moved = True
        x = self.root.winfo_x() + event.x - self._offset_x
        y = self.root.winfo_y() + event.y - self._offset_y
        self.root.geometry(f'+{x}+{y}')
        self.position_x = x
        self.position_y = y

    def _on_release(self, event):
        """Relâchement sans déplacement sur un nom = switch vers ce personnage."""
        if self._drag_moved:
            return
        index = self._label_index.get(event.widget)
        if index is not None and self.on_character_click:
            self.on_character_click(index)

    def update_display(self, characters: List[str], current_index: int,
                       next_index: int, skipped: Optional[List[bool]] = None):
        """Met à jour l'affichage des personnages."""
        self.characters = characters
        self.current_index = current_index
        self.next_index = next_index
        self.skipped = skipped or [False] * len(characters)

        if self.root:
            self.root.after(0, self._refresh_display)
    
    def _refresh_display(self):
        """Rafraîchit l'affichage (doit être appelé depuis le thread GUI)."""
        # Ne reconstruire que si l'état affiché a changé (évite flicker, CPU
        # et la destruction des labels entre un appui et un relâchement de clic)
        state = (tuple(self.characters), self.current_index, self.next_index,
                 tuple(self.skipped), self.font_size)
        if state == self._last_state:
            return
        self._last_state = state

        # Supprimer les anciens widgets
        for widget in self.char_frame.winfo_children():
            widget.destroy()

        self.labels.clear()
        self.arrows.clear()
        self._label_index.clear()

        if not self.characters:
            return

        # Créer les labels pour chaque personnage
        for i, char_name in enumerate(self.characters):
            # Chevron discret entre les personnages
            if i > 0:
                arrow = tk.Label(
                    self.char_frame,
                    text="›",
                    font=("Fjalla One", max(self.font_size - 2, 8)),
                    fg="#4a4a4a",
                    bg="#1a1a1a"
                )
                arrow.pack(side=tk.LEFT, padx=2)
                self.arrows.append(arrow)

            is_skipped = i < len(self.skipped) and self.skipped[i]

            # Déterminer le style du label (palette Dofus 3)
            font_style = "overstrike" if is_skipped else ""
            if i == self.current_index:
                # Personnage actif : chip bordeaux (le fond suffit, pas de crochets)
                fg_color = "#ffffff"
                bg_color = "#8b2252"
                font_weight = "bold"
            elif i == self.next_index and not is_skipped:
                # Prochain personnage (doré)
                fg_color = "#fbbf24"
                bg_color = "#1a1a1a"
                font_weight = "bold"
            elif is_skipped:
                # Personnage mort/absent : barré, très discret
                fg_color = "#4a4a4a"
                bg_color = "#1a1a1a"
                font_weight = "normal"
            else:
                # Autres personnages (gris discret)
                fg_color = "#777777"
                bg_color = "#1a1a1a"
                font_weight = "normal"

            icon = get_class_icon(char_name, ICON_SIZE)
            font_spec = " ".join(s for s in (font_weight, font_style) if s and s != "normal")
            label = tk.Label(
                self.char_frame,
                text=f" {char_name}" if icon else char_name,  # petit espace icône/texte
                image=icon,
                compound=tk.LEFT if icon else tk.NONE,
                font=("Fjalla One", self.font_size, font_spec) if font_spec
                     else ("Fjalla One", self.font_size),
                fg=fg_color,
                bg=bg_color,
                padx=8,
                pady=4,
                cursor="hand2"
            )
            if icon:
                label.image = icon  # Garder la référence (anti garbage collection)
            label.pack(side=tk.LEFT)
            self.labels.append(label)

            # Clic gauche = switch (géré au relâchement), clic droit = mort/vivant
            self._label_index[label] = i
            label.bind("<Button-3>", lambda e, idx=i: self._on_toggle(idx))

        # Ajuster la fenêtre à la taille réellement requise par les widgets
        self.root.update_idletasks()
        required_width = self.main_frame.winfo_reqwidth() + 20   # marge autour du frame
        required_height = self.main_frame.winfo_reqheight() + 20
        if required_width != self.width or required_height != self.height:
            self.width = required_width
            self.height = required_height
            self.root.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
        self._draw_background(self.width, self.height)

    def _draw_background(self, width: int, height: int):
        """Dessine le fond arrondi du bandeau sous les widgets."""
        if not self.canvas:
            return
        if self._bg_rect is not None:
            self.canvas.delete(self._bg_rect)
        r = CORNER_RADIUS
        # Polygone lissé : les sommets doublés autour des coins donnent l'arrondi
        points = [
            r, 0, width - r, 0, width, 0,
            width, r, width, height - r, width, height,
            width - r, height, r, height, 0, height,
            0, height - r, 0, r, 0, 0,
        ]
        self._bg_rect = self.canvas.create_polygon(
            points, smooth=True, fill=BG_COLOR, outline=""
        )
        self.canvas.tag_lower(self._bg_rect)
    
    def _on_toggle(self, index: int):
        """Clic droit sur un nom : marquer/démarquer mort ou absent."""
        if self.on_character_toggle:
            self.on_character_toggle(index)

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
