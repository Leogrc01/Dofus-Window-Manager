"""Roue de sélection radiale des personnages."""
import tkinter as tk
import math
import os
import sys
from typing import List, Optional, Callable, Dict
from PIL import Image, ImageTk


# Palette Dofus 3
WHEEL_COLORS = {
    "bg_transparent": "#010101",   # Couleur clé de transparence
    "sector_normal": "#2d2d2d",    # Fond secteur
    "sector_hover": "#8b2252",     # Fond secteur surligné
    "sector_border": "#3a3a3a",    # Bordure secteurs
    "text_normal": "#e0e0e0",      # Texte normal
    "text_hover": "#ffffff",       # Texte surligné
    "center_bg": "#1a1a1a",        # Fond cercle central
    "center_border": "#8b2252",    # Bordure cercle central
    "center_text": "#e0e0e0",      # Texte central
}

# Dimensions
OUTER_RADIUS = 200
INNER_RADIUS = 60
WHEEL_SIZE = (OUTER_RADIUS + 40) * 2  # Marge pour le texte
ICON_SIZE = 36  # Taille des icônes de classe (pixels)

# Chemin vers le dossier des icônes de classe
def _get_classes_dir() -> str:
    """Retourne le chemin du dossier classes/ (compatible .exe et .py)."""
    if getattr(sys, 'frozen', False):
        # Exécuté depuis un .exe PyInstaller
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "classes")

CLASSES_DIR = _get_classes_dir()


class CharacterWheel:
    """Roue radiale de sélection de personnage."""

    def __init__(self):
        self.root: Optional[tk.Tk] = None  # Référence au root principal (overlay)
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.visible = False

        # Données
        self.characters: List[str] = []
        self.current_index: int = 0
        self.hovered_index: int = -1

        # Callback pour switcher
        self.on_select: Optional[Callable[[int], None]] = None

        # Cache des icônes (garder les références pour éviter le garbage collection)
        self._icon_cache: Dict[str, ImageTk.PhotoImage] = {}
        self._active_icons: List[ImageTk.PhotoImage] = []

        # IDs des éléments canvas pour le rafraîchissement
        self._sector_ids: List[int] = []
        self._text_ids: List[int] = []
        self._center_ids: List[int] = []

    def create_window(self, root: tk.Tk):
        """Crée la fenêtre Toplevel de la roue (cachée par défaut)."""
        self.root = root

        self.window = tk.Toplevel(root)
        self.window.title("Character Wheel")
        self.window.geometry(f"{WHEEL_SIZE}x{WHEEL_SIZE}")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.95)

        # Transparence du fond
        self.window.configure(bg=WHEEL_COLORS["bg_transparent"])
        self.window.wm_attributes('-transparentcolor', WHEEL_COLORS["bg_transparent"])

        # Canvas
        self.canvas = tk.Canvas(
            self.window,
            width=WHEEL_SIZE,
            height=WHEEL_SIZE,
            bg=WHEEL_COLORS["bg_transparent"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Événements
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.window.bind("<Escape>", lambda e: self.hide())

        # Cacher par défaut
        self.window.withdraw()

    def show(self, characters: List[str], current_index: int):
        """Affiche la roue centrée sur le curseur."""
        if not self.window or not characters:
            return

        self.characters = characters
        self.current_index = current_index
        self.hovered_index = -1

        # Centrer sur le curseur
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        x = mouse_x - WHEEL_SIZE // 2
        y = mouse_y - WHEEL_SIZE // 2
        self.window.geometry(f"{WHEEL_SIZE}x{WHEEL_SIZE}+{x}+{y}")

        self._draw_wheel()
        self.window.deiconify()
        self.window.lift()
        self.visible = True

    def hide(self):
        """Cache la roue."""
        if self.window:
            self.window.withdraw()
        self.visible = False

    def toggle(self, characters: List[str], current_index: int):
        """Affiche ou cache la roue."""
        if self.visible:
            self.hide()
        else:
            self.show(characters, current_index)

    def _sector_to_tkinter_angle(self, sector_index: int, n: int) -> float:
        """Convertit un index de secteur en angle de départ tkinter.
        
        Convention :
        - Secteur 0 en haut, puis sens horaire
        - tkinter : 0° = Est (droite), sens anti-horaire
        - Donc "haut" = 90° en tkinter
        """
        angle_step = 360 / n
        # Angle logique du centre du secteur (sens horaire depuis le haut)
        logical_center = sector_index * angle_step
        # Conversion en tkinter : haut=90°, sens horaire = négatif en tkinter
        tkinter_start = 90 - logical_center + angle_step / 2
        return tkinter_start

    def _sector_center_xy(self, sector_index: int, n: int, radius: float) -> tuple:
        """Calcule les coordonnées (x, y) du centre d'un secteur."""
        cx = WHEEL_SIZE // 2
        cy = WHEEL_SIZE // 2
        angle_step = 360 / n
        # Angle logique du centre (sens horaire depuis le haut)
        logical_center_deg = sector_index * angle_step
        logical_center_rad = math.radians(logical_center_deg)
        # En coordonnées écran : sin pour x (droite), cos pour y (bas)
        x = cx + radius * math.sin(logical_center_rad)
        y = cy - radius * math.cos(logical_center_rad)
        return x, y

    def _load_class_icon(self, class_name: str) -> Optional[ImageTk.PhotoImage]:
        """Charge l'icône d'une classe depuis le dossier classes/."""
        # Normaliser le nom (minuscule, sans accents)
        key = class_name.lower().strip()
        
        if key in self._icon_cache:
            return self._icon_cache[key]
        
        icon_path = os.path.join(CLASSES_DIR, f"{key}.png")
        if not os.path.exists(icon_path):
            return None
        
        try:
            img = Image.open(icon_path)
            img = img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._icon_cache[key] = photo
            return photo
        except Exception:
            return None

    def _draw_wheel(self):
        """Dessine la roue complète."""
        if not self.canvas:
            return

        self.canvas.delete("all")
        self._sector_ids.clear()
        self._text_ids.clear()
        self._center_ids.clear()
        self._active_icons.clear()

        cx = WHEEL_SIZE // 2
        cy = WHEEL_SIZE // 2
        n = len(self.characters)

        if n == 0:
            return

        angle_step = 360 / n

        # Dessiner les secteurs
        for i in range(n):
            is_hovered = (i == self.hovered_index)
            is_current = (i == self.current_index)

            if is_hovered:
                fill = WHEEL_COLORS["sector_hover"]
            elif is_current:
                fill = "#3d1a2e"  # Fond légèrement teinté bordeaux pour le perso actif
            else:
                fill = WHEEL_COLORS["sector_normal"]
            outline = WHEEL_COLORS["center_border"] if is_current else WHEEL_COLORS["sector_border"]
            outline_width = 3 if is_current else 1

            # Arc (tkinter : extent négatif = sens horaire)
            tk_start = self._sector_to_tkinter_angle(i, n)
            sector_id = self.canvas.create_arc(
                cx - OUTER_RADIUS, cy - OUTER_RADIUS,
                cx + OUTER_RADIUS, cy + OUTER_RADIUS,
                start=tk_start, extent=-angle_step,
                fill=fill, outline=outline, width=outline_width,
                style=tk.PIESLICE
            )
            self._sector_ids.append(sector_id)

            # Position du contenu (icône + texte)
            content_radius = (OUTER_RADIUS + INNER_RADIUS) / 2 + 15
            content_x, content_y = self._sector_center_xy(i, n, content_radius)

            # Icône de classe (au-dessus du nom)
            icon = self._load_class_icon(self.characters[i])
            if icon:
                self._active_icons.append(icon)  # Garder la référence
                self.canvas.create_image(
                    content_x, content_y - 12,
                    image=icon,
                    anchor=tk.CENTER
                )
                # Texte en dessous de l'icône
                text_y_offset = content_y + ICON_SIZE // 2 + 4
            else:
                # Pas d'icône : texte centré normalement
                text_y_offset = content_y

            text_color = WHEEL_COLORS["text_hover"] if is_hovered else WHEEL_COLORS["text_normal"]
            font_weight = "bold" if (is_hovered or is_current) else "normal"
            font_size = 11 if is_hovered else 10

            text_id = self.canvas.create_text(
                content_x, text_y_offset,
                text=self.characters[i],
                fill=text_color,
                font=("Arial", font_size, font_weight),
                anchor=tk.CENTER
            )
            self._text_ids.append(text_id)

        # Cercle central (masquer le centre des arcs pie)
        padding = 4
        center_bg = self.canvas.create_oval(
            cx - INNER_RADIUS - padding, cy - INNER_RADIUS - padding,
            cx + INNER_RADIUS + padding, cy + INNER_RADIUS + padding,
            fill=WHEEL_COLORS["bg_transparent"], outline=""
        )
        self._center_ids.append(center_bg)

        center_circle = self.canvas.create_oval(
            cx - INNER_RADIUS, cy - INNER_RADIUS,
            cx + INNER_RADIUS, cy + INNER_RADIUS,
            fill=WHEEL_COLORS["center_bg"],
            outline=WHEEL_COLORS["center_border"],
            width=2
        )
        self._center_ids.append(center_circle)

        # Contenu central (icône + nom du personnage actuel)
        current_name = self.characters[self.current_index] if 0 <= self.current_index < n else ""
        
        # Icône de classe au centre
        center_icon = self._load_class_icon(current_name)
        if center_icon:
            self._active_icons.append(center_icon)
            self.canvas.create_image(
                cx, cy - 14,
                image=center_icon,
                anchor=tk.CENTER
            )
            # Nom sous l'icône
            center_text = self.canvas.create_text(
                cx, cy + ICON_SIZE // 2,
                text=current_name,
                fill=WHEEL_COLORS["center_text"],
                font=("Arial", 10, "bold"),
                anchor=tk.CENTER
            )
        else:
            # Pas d'icône : label + nom
            self.canvas.create_text(
                cx, cy - 10,
                text="Actuel",
                fill=WHEEL_COLORS["center_border"],
                font=("Arial", 8),
                anchor=tk.CENTER
            )
            center_text = self.canvas.create_text(
                cx, cy + 10,
                text=current_name,
                fill=WHEEL_COLORS["center_text"],
                font=("Arial", 12, "bold"),
                anchor=tk.CENTER
            )
        self._center_ids.append(center_text)

    def _get_hovered_sector(self, event_x: int, event_y: int) -> int:
        """Calcule quel secteur est sous le curseur."""
        cx = WHEEL_SIZE // 2
        cy = WHEEL_SIZE // 2
        dx = event_x - cx
        dy = event_y - cy
        distance = math.sqrt(dx * dx + dy * dy)

        # En dehors du cercle ou dans le centre
        if distance > OUTER_RADIUS or distance < INNER_RADIUS:
            return -1

        n = len(self.characters)
        if n == 0:
            return -1

        # Angle en degrés, sens horaire depuis le haut (même convention que le dessin)
        # atan2(dx, -dy) : dx=droite, -dy=haut → 0°=haut, sens horaire
        angle = math.degrees(math.atan2(dx, -dy))
        angle_step = 360 / n
        # Décaler d'un demi-secteur pour aligner détection et dessin
        # (les secteurs sont dessinés centrés, pas alignés sur 0°)
        angle = (angle + angle_step / 2 + 360) % 360

        index = int(angle / angle_step)
        return min(index, n - 1)

    def _on_mouse_move(self, event):
        """Gère le mouvement de la souris pour surligner le secteur."""
        new_hover = self._get_hovered_sector(event.x, event.y)
        if new_hover != self.hovered_index:
            self.hovered_index = new_hover
            self._draw_wheel()

    def _on_click(self, event):
        """Gère le clic gauche pour sélectionner un personnage."""
        sector = self._get_hovered_sector(event.x, event.y)
        if sector >= 0 and self.on_select:
            self.hide()
            self.on_select(sector)
        elif sector < 0:
            # Clic en dehors / au centre = fermer
            self.hide()

    def _on_right_click(self, event):
        """Clic droit = annuler."""
        self.hide()
