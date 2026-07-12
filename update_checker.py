"""Vérification de mise à jour via les releases GitHub."""
import json
import re
import urllib.request
from typing import Optional, Tuple

RELEASES_API = "https://api.github.com/repos/Leogrc01/Dofus-Window-Manager/releases/latest"
RELEASES_PAGE = "https://github.com/Leogrc01/Dofus-Window-Manager/releases/latest"
TIMEOUT = 10


def _parse_version(version: str) -> Tuple[int, ...]:
    """'v1.2.0' → (1, 2, 0). Tolérant aux formats approximatifs."""
    numbers = re.findall(r"\d+", version)
    return tuple(int(n) for n in numbers[:3]) or (0,)


def check_for_update(current_version: str) -> Optional[Tuple[str, str]]:
    """Retourne (nouvelle_version, url) si une version plus récente existe, sinon None.

    Silencieux en cas d'erreur réseau (retourne None) : la vérification
    ne doit jamais gêner le lancement.
    """
    try:
        request = urllib.request.Request(
            RELEASES_API,
            headers={"User-Agent": "DofusWindowManager-UpdateCheck",
                     "Accept": "application/vnd.github+json"}
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
        latest_tag = data.get("tag_name", "")
        if _parse_version(latest_tag) > _parse_version(current_version):
            return latest_tag, data.get("html_url", RELEASES_PAGE)
    except Exception:
        pass
    return None
