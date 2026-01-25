"""Module pour gérer l'ordre des fenêtres et le switching."""
from typing import List, Optional, Dict
from window_detector import WindowDetector, WindowInfo


class CharacterWindow:
    """Représente un personnage avec sa fenêtre associée."""
    
    def __init__(self, name: str, hwnd: int, position: int):
        self.name = name
        self.hwnd = hwnd
        self.position = position  # Position dans l'ordre d'initiative (0-7)
        
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour la sérialisation."""
        return {
            "name": self.name,
            "hwnd": self.hwnd,
            "position": self.position
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CharacterWindow':
        """Crée une instance depuis un dictionnaire."""
        return CharacterWindow(
            name=data["name"],
            hwnd=data["hwnd"],
            position=data["position"]
        )


class WindowManager:
    """Gère les fenêtres DOFUS et l'ordre de switching."""
    
    def __init__(self, detector: WindowDetector):
        self.detector = detector
        self.characters: List[CharacterWindow] = []
        self.current_index: int = 0
        
    def add_character(self, name: str, hwnd: int, position: int):
        """Ajoute un personnage à la liste."""
        char = CharacterWindow(name, hwnd, position)
        self.characters.append(char)
        self._sort_by_position()
        
    def remove_character(self, position: int):
        """Retire un personnage de la liste."""
        self.characters = [c for c in self.characters if c.position != position]
        
    def update_character_name(self, position: int, new_name: str):
        """Met à jour le nom d'un personnage."""
        for char in self.characters:
            if char.position == position:
                char.name = new_name
                break
                
    def _sort_by_position(self):
        """Trie les personnages par position (ordre d'initiative)."""
        self.characters.sort(key=lambda c: c.position)
        
    def switch_to_position(self, position: int) -> bool:
        """Switch vers un personnage à une position donnée (0-7)."""
        if 0 <= position < len(self.characters):
            char = self.characters[position]
            if self.detector.is_window_valid(char.hwnd):
                success = self.detector.focus_window(char.hwnd)
                if success:
                    self.current_index = position
                return success
        return False
    
    def switch_to_character(self, name: str) -> bool:
        """Switch vers un personnage par son nom."""
        for i, char in enumerate(self.characters):
            if char.name.upper() == name.upper():
                return self.switch_to_position(i)
        return False
    
    def switch_to_next(self) -> bool:
        """Switch vers le personnage suivant dans l'ordre d'initiative."""
        if not self.characters:
            return False
            
        self.current_index = (self.current_index + 1) % len(self.characters)
        char = self.characters[self.current_index]
        
        if self.detector.is_window_valid(char.hwnd):
            return self.detector.focus_window(char.hwnd)
        else:
            # Si la fenêtre n'est plus valide, essayer la suivante
            return self.switch_to_next()
    
    def switch_to_previous(self) -> bool:
        """Switch vers le personnage précédent dans l'ordre d'initiative."""
        if not self.characters:
            return False
            
        self.current_index = (self.current_index - 1) % len(self.characters)
        char = self.characters[self.current_index]
        
        if self.detector.is_window_valid(char.hwnd):
            return self.detector.focus_window(char.hwnd)
        else:
            return self.switch_to_previous()
    
    def get_current_character(self) -> Optional[CharacterWindow]:
        """Retourne le personnage actuellement actif."""
        if 0 <= self.current_index < len(self.characters):
            return self.characters[self.current_index]
        return None
    
    def get_next_character(self) -> Optional[CharacterWindow]:
        """Retourne le prochain personnage dans l'ordre."""
        if not self.characters:
            return None
        next_index = (self.current_index + 1) % len(self.characters)
        return self.characters[next_index]
    
    def get_character_list(self) -> List[str]:
        """Retourne la liste des noms de personnages dans l'ordre."""
        return [char.name for char in self.characters]
    
    def validate_windows(self) -> List[int]:
        """Vérifie la validité des fenêtres et retourne les positions invalides."""
        invalid_positions = []
        for char in self.characters:
            if not self.detector.is_window_valid(char.hwnd):
                invalid_positions.append(char.position)
        return invalid_positions
    
    def to_dict(self) -> Dict:
        """Convertit la configuration en dictionnaire."""
        return {
            "characters": [c.to_dict() for c in self.characters],
            "current_index": self.current_index
        }
    
    def from_dict(self, data: Dict):
        """Charge la configuration depuis un dictionnaire."""
        self.characters = [CharacterWindow.from_dict(c) for c in data.get("characters", [])]
        self.current_index = data.get("current_index", 0)
        self._sort_by_position()
