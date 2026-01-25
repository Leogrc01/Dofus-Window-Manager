"""Script de debug pour afficher les fenêtres DOFUS détectées."""
from window_detector import WindowDetector

detector = WindowDetector()
windows = detector.detect_windows()

print(f"\n🔍 {len(windows)} fenêtre(s) DOFUS détectée(s):\n")

for i, window in enumerate(windows):
    print(f"[{i}] HWND: {window.hwnd:8d} | Titre: {window.title}")

print("\n💡 Ces fenêtres sont dans l'ordre de détection de Windows.")
print("   Pas forcément ton ordre d'initiative souhaité.\n")
