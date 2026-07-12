"""Client API DofusDB pour l'assistant de chasse au trésor.

Utilise l'API publique https://api.dofusdb.fr (la même que l'outil de chasse
DofusDB et Ganymède) :
- /point-of-interest : liste des indices (noms localisés)
- /treasure-hunt?x&y&direction : maps candidates dans une direction, avec
  leurs indices et la distance en nombre de maps
"""
import json
import os
import time
import unicodedata
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

from app_paths import get_data_dir

API_BASE = "https://api.dofusdb.fr"
USER_AGENT = "DofusWindowManager-HuntHelper/1.0"
TIMEOUT = 10  # secondes

CACHE_FILE = os.path.join(get_data_dir(), "hunt_clues_cache.json")
CACHE_MAX_AGE = 7 * 24 * 3600  # 7 jours

# Enum des directions de l'API (DirectionsEnum Dofus)
DIRECTION_EAST = 0
DIRECTION_SOUTH = 2
DIRECTION_WEST = 4
DIRECTION_NORTH = 6


def _get_json(path: str, params: Dict) -> Dict:
    """Effectue un GET sur l'API et retourne le JSON décodé."""
    url = f"{API_BASE}/{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize(text: str) -> str:
    """Minuscules + sans accents, pour la recherche d'indices."""
    text = unicodedata.normalize("NFD", text.lower().strip())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def fetch_clues(lang: str = "fr") -> List[Dict]:
    """Récupère la liste complète des indices depuis l'API (paginée)."""
    clues = []
    skip = 0
    while True:
        result = _get_json("point-of-interest", {"$limit": 50, "$skip": skip})
        for poi in result.get("data", []):
            name = poi.get("name", {}).get(lang)
            if name and poi.get("id") is not None:
                clues.append({"id": poi["id"], "name": name})
        skip += len(result.get("data", []))
        if skip >= result.get("total", 0) or not result.get("data"):
            break
    clues.sort(key=lambda c: normalize(c["name"]))
    return clues


def load_clues(force_refresh: bool = False) -> List[Dict]:
    """Charge la liste des indices (cache disque 7 jours, sinon API)."""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            if time.time() - cache.get("timestamp", 0) < CACHE_MAX_AGE and cache.get("clues"):
                return cache["clues"]
        except Exception:
            pass  # Cache corrompu : on re-télécharge

    clues = fetch_clues()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "clues": clues}, f, ensure_ascii=False)
    except Exception:
        pass  # Impossible d'écrire le cache : non bloquant
    return clues


def find_clue(x: int, y: int, direction: int, poi_id: int) -> Optional[Dict]:
    """Cherche la map la plus proche contenant l'indice dans une direction.

    Retourne {"x", "y", "distance"} ou None si l'indice n'est pas trouvé
    (l'API limite la recherche à 10 maps, comme en jeu).
    """
    result = _get_json("treasure-hunt", {
        "x": x, "y": y, "direction": direction, "$limit": 50
    })

    best = None
    for map_data in result.get("data", []):
        poi_ids = {poi.get("id") for poi in map_data.get("pois", [])}
        if poi_id in poi_ids:
            candidate = {
                "x": map_data["posX"],
                "y": map_data["posY"],
                "distance": map_data.get("distance", 0),
            }
            if best is None or candidate["distance"] < best["distance"]:
                best = candidate
    return best
