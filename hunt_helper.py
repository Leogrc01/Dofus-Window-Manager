"""Fenêtre d'assistant de chasse au trésor (données DofusDB)."""
import threading
import tkinter as tk
from typing import Dict, List, Optional

import hunt_api

# Palette Dofus 3
COLORS = {
    "bg": "#1a1a1a",
    "bg_card": "#2d2d2d",
    "bg_input": "#1e1e1e",
    "accent": "#8b2252",
    "accent_hover": "#a0325f",
    "text": "#e0e0e0",
    "text_dim": "#777777",
    "border": "#3a3a3a",
    "gold": "#fbbf24",
    "success": "#4ade80",
    "error": "#f87171",
}

WINDOW_WIDTH = 340

# (texte, direction API, position dans la croix)
DIRECTION_BUTTONS = [
    ("▲", hunt_api.DIRECTION_NORTH, (0, 1)),
    ("◄", hunt_api.DIRECTION_WEST, (1, 0)),
    ("►", hunt_api.DIRECTION_EAST, (1, 2)),
    ("▼", hunt_api.DIRECTION_SOUTH, (2, 1)),
]


class HuntHelper:
    """Assistant de chasse : position + direction + indice → map cible."""

    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.window: Optional[tk.Toplevel] = None
        self.visible = False

        # Données
        self.clues: List[Dict] = []
        self.selected_clue: Optional[Dict] = None
        self.direction: Optional[int] = None
        self._suggestions: List[Dict] = []
        self._loading = False

        # Widgets
        self.x_entry: Optional[tk.Entry] = None
        self.y_entry: Optional[tk.Entry] = None
        self.clue_entry: Optional[tk.Entry] = None
        self.suggestion_list: Optional[tk.Listbox] = None
        self.result_label: Optional[tk.Label] = None
        self.status_label: Optional[tk.Label] = None
        self.direction_buttons: Dict[int, tk.Button] = {}
        self.autocopy_var: Optional[tk.BooleanVar] = None

    # ------------------------------------------------------------------
    # Création de la fenêtre
    # ------------------------------------------------------------------
    def create_window(self, root: tk.Tk):
        """Crée la fenêtre Toplevel (cachée par défaut)."""
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Chasse au trésor")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.97)
        self.window.configure(bg=COLORS["bg"], highlightthickness=1,
                              highlightbackground=COLORS["border"])

        # --- Header draggable ---
        header = tk.Frame(self.window, bg=COLORS["accent"])
        header.pack(fill=tk.X)
        title = tk.Label(header, text="Chasse au trésor", bg=COLORS["accent"],
                         fg="#ffffff", font=("Fjalla One", 12, "bold"), pady=6)
        title.pack(side=tk.LEFT, padx=10)
        close_btn = tk.Label(header, text="✕", bg=COLORS["accent"], fg="#ffffff",
                             font=("Fjalla One", 11, "bold"), padx=10, cursor="hand2")
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.hide())
        for widget in (header, title):
            widget.bind("<Button-1>", self._start_move)
            widget.bind("<B1-Motion>", self._do_move)

        body = tk.Frame(self.window, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # --- Position ---
        pos_frame = tk.Frame(body, bg=COLORS["bg"])
        pos_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(pos_frame, text="Position", bg=COLORS["bg"], fg=COLORS["text_dim"],
                 font=("Fjalla One", 10)).pack(side=tk.LEFT, padx=(0, 8))
        self.x_entry = self._make_entry(pos_frame, width=5)
        self.x_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.y_entry = self._make_entry(pos_frame, width=5)
        self.y_entry.pack(side=tk.LEFT)

        # --- Croix de direction ---
        cross = tk.Frame(body, bg=COLORS["bg"])
        cross.pack(pady=(0, 8))
        for text, direction, (row, col) in DIRECTION_BUTTONS:
            btn = tk.Button(
                cross, text=text, width=3,
                font=("Fjalla One", 11),
                bg=COLORS["bg_card"], fg=COLORS["text"],
                activebackground=COLORS["accent_hover"], activeforeground="#ffffff",
                relief=tk.FLAT, cursor="hand2",
                command=lambda d=direction: self._on_direction(d)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.direction_buttons[direction] = btn

        # --- Recherche d'indice ---
        tk.Label(body, text="Indice", bg=COLORS["bg"], fg=COLORS["text_dim"],
                 font=("Fjalla One", 10), anchor="w").pack(fill=tk.X)
        self.clue_entry = self._make_entry(body)
        self.clue_entry.pack(fill=tk.X, pady=(2, 0))
        self.clue_entry.bind("<KeyRelease>", self._on_clue_typed)
        self.clue_entry.bind("<Return>", self._on_clue_enter)
        self.clue_entry.bind("<Down>", self._focus_suggestions)

        self.suggestion_list = tk.Listbox(
            body, height=6,
            bg=COLORS["bg_card"], fg=COLORS["text"],
            selectbackground=COLORS["accent"], selectforeground="#ffffff",
            font=("Fjalla One", 10),
            relief=tk.FLAT, highlightthickness=0, activestyle="none"
        )
        self.suggestion_list.bind("<<ListboxSelect>>", self._on_suggestion_selected)
        self.suggestion_list.bind("<Return>", self._on_suggestion_selected)
        # (pack/unpack dynamique selon les suggestions)

        # --- Résultat ---
        self.result_label = tk.Label(
            body, text="", bg=COLORS["bg"], fg=COLORS["gold"],
            font=("Fjalla One", 13, "bold"), pady=4
        )
        self.result_label.pack(fill=tk.X)

        # --- Options + statut ---
        self.autocopy_var = tk.BooleanVar(value=True)
        autocopy = tk.Checkbutton(
            body, text="Copier /travel automatiquement",
            variable=self.autocopy_var,
            bg=COLORS["bg"], fg=COLORS["text_dim"],
            activebackground=COLORS["bg"], activeforeground=COLORS["text"],
            selectcolor=COLORS["bg_input"], font=("Fjalla One", 9),
            highlightthickness=0
        )
        autocopy.pack(anchor="w")

        self.status_label = tk.Label(
            body, text="", bg=COLORS["bg"], fg=COLORS["text_dim"],
            font=("Fjalla One", 9), anchor="w"
        )
        self.status_label.pack(fill=tk.X)

        self.window.bind("<Escape>", lambda e: self.hide())
        # La hauteur s'adapte au contenu (suggestions dynamiques)
        self.window.withdraw()

    def _make_entry(self, parent, width: Optional[int] = None) -> tk.Entry:
        """Crée un champ de saisie au style de la palette."""
        entry = tk.Entry(
            parent, width=width or 20,
            bg=COLORS["bg_input"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT, font=("Fjalla One", 11),
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        return entry

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------
    def show(self):
        """Affiche la fenêtre près du curseur et charge les indices."""
        if not self.window:
            return
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        self.window.geometry(f"+{mouse_x - WINDOW_WIDTH // 2}+{mouse_y - 40}")
        self.window.deiconify()
        self.window.lift()
        self.visible = True
        self.clue_entry.focus_set()

        if not self.clues and not self._loading:
            self._load_clues_async()

    def hide(self):
        """Cache la fenêtre."""
        if self.window:
            self.window.withdraw()
        self.visible = False

    def toggle(self):
        """Affiche ou cache la fenêtre."""
        if self.visible:
            self.hide()
        else:
            self.show()

    def _start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _do_move(self, event):
        x = self.window.winfo_x() + event.x - self._offset_x
        y = self.window.winfo_y() + event.y - self._offset_y
        self.window.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------
    # Chargement des indices
    # ------------------------------------------------------------------
    def _load_clues_async(self):
        """Charge la liste des indices en arrière-plan."""
        self._loading = True
        self._set_status("Chargement des indices…")

        def worker():
            try:
                clues = hunt_api.load_clues()
                self.root.after(0, lambda: self._on_clues_loaded(clues))
            except Exception:
                self.root.after(0, lambda: self._on_clues_failed())

        threading.Thread(target=worker, daemon=True).start()

    def _on_clues_loaded(self, clues: List[Dict]):
        self._loading = False
        self.clues = clues
        self._set_status(f"{len(clues)} indices disponibles")

    def _on_clues_failed(self):
        self._loading = False
        self._set_status("Erreur réseau (indices non chargés)", error=True)

    # ------------------------------------------------------------------
    # Autocomplétion
    # ------------------------------------------------------------------
    def _on_clue_typed(self, event):
        """Met à jour les suggestions pendant la frappe."""
        if event.keysym in ("Return", "Down", "Up", "Escape"):
            return
        query = hunt_api.normalize(self.clue_entry.get())
        self.selected_clue = None

        if len(query) < 2:
            self._show_suggestions([])
            return
        matches = [c for c in self.clues if query in hunt_api.normalize(c["name"])]
        self._show_suggestions(matches[:8])

    def _show_suggestions(self, suggestions: List[Dict]):
        self._suggestions = suggestions
        self.suggestion_list.delete(0, tk.END)
        if not suggestions:
            self.suggestion_list.pack_forget()
            return
        for clue in suggestions:
            self.suggestion_list.insert(tk.END, f" {clue['name']}")
        self.suggestion_list.configure(height=min(len(suggestions), 8))
        self.suggestion_list.pack(fill=tk.X, pady=(2, 0),
                                  after=self.clue_entry)

    def _focus_suggestions(self, event):
        """Flèche bas depuis le champ : naviguer dans les suggestions."""
        if self._suggestions:
            self.suggestion_list.focus_set()
            self.suggestion_list.selection_clear(0, tk.END)
            self.suggestion_list.selection_set(0)
        return "break"

    def _on_clue_enter(self, event):
        """Entrée dans le champ : prendre la première suggestion."""
        if self._suggestions:
            self._select_clue(self._suggestions[0])
        return "break"

    def _on_suggestion_selected(self, event):
        selection = self.suggestion_list.curselection()
        if selection and selection[0] < len(self._suggestions):
            self._select_clue(self._suggestions[selection[0]])

    def _select_clue(self, clue: Dict):
        """Sélectionne un indice et lance la recherche si une direction est choisie."""
        self.selected_clue = clue
        self.clue_entry.delete(0, tk.END)
        self.clue_entry.insert(0, clue["name"])
        self._show_suggestions([])
        self.clue_entry.focus_set()
        self.clue_entry.icursor(tk.END)
        if self.direction is not None:
            self._search()

    # ------------------------------------------------------------------
    # Direction + recherche
    # ------------------------------------------------------------------
    def _on_direction(self, direction: int):
        """Choix d'une direction : surligner et chercher si un indice est choisi."""
        self.direction = direction
        for d, btn in self.direction_buttons.items():
            active = (d == direction)
            btn.configure(bg=COLORS["accent"] if active else COLORS["bg_card"],
                          fg="#ffffff" if active else COLORS["text"])
        if self.selected_clue:
            self._search()

    def _get_position(self) -> Optional[tuple]:
        try:
            return int(self.x_entry.get().strip()), int(self.y_entry.get().strip())
        except ValueError:
            return None

    def _search(self):
        """Lance la recherche de l'indice (réseau, en arrière-plan)."""
        position = self._get_position()
        if position is None:
            self._set_status("Position invalide", error=True)
            return
        if self.selected_clue is None or self.direction is None:
            return

        x, y = position
        clue = self.selected_clue
        direction = self.direction
        self._set_status("Recherche…")

        def worker():
            try:
                result = hunt_api.find_clue(x, y, direction, clue["id"])
                self.root.after(0, lambda: self._on_result(result))
            except Exception:
                self.root.after(0, lambda: self._set_status("Erreur réseau", error=True))

        threading.Thread(target=worker, daemon=True).start()

    def _on_result(self, result: Optional[Dict]):
        """Affiche le résultat et prépare l'étape suivante."""
        if result is None:
            self.result_label.configure(text="Introuvable (≤ 10 maps)",
                                        fg=COLORS["error"])
            self._set_status("Essayez une autre direction ou un autre indice")
            return

        x, y, distance = result["x"], result["y"], result["distance"]
        self.result_label.configure(text=f"→  [{x} ; {y}]   ({distance} maps)",
                                    fg=COLORS["gold"])

        copied = ""
        if self.autocopy_var.get():
            travel = f"/travel {x},{y}"
            self.window.clipboard_clear()
            self.window.clipboard_append(travel)
            copied = " · /travel copié"
        self._set_status(f"Trouvé à {distance} map(s){copied}", success=True)

        # Enchaîner : la map trouvée devient la position de départ suivante
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))

        # Préparer l'indice suivant
        self.selected_clue = None
        self.clue_entry.delete(0, tk.END)
        self.clue_entry.focus_set()

    def _set_status(self, text: str, error: bool = False, success: bool = False):
        color = COLORS["error"] if error else COLORS["success"] if success else COLORS["text_dim"]
        self.status_label.configure(text=text, fg=color)
