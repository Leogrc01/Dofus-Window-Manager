"""Chemins des données de l'application (%APPDATA%/DofusWindowManager)."""
import os


APP_DIR_NAME = "DofusWindowManager"


def get_data_dir() -> str:
    """Retourne le dossier de données de l'app (créé si besoin).

    %APPDATA%/DofusWindowManager — évite d'écrire à côté de l'exe,
    qui peut être dans un dossier protégé (Program Files, etc.).
    """
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    data_dir = os.path.join(base, APP_DIR_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
