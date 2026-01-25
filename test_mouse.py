"""Script de test pour détecter les boutons de souris."""
from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Bouton détecté: {button}")
        print(f"  - Type: {type(button)}")
        print(f"  - Nom: {button.name if hasattr(button, 'name') else 'N/A'}")
        print(f"  - Valeur: {button.value if hasattr(button, 'value') else 'N/A'}")
        print()

print("🖱️ Test des boutons de souris")
print("Appuyez sur vos boutons latéraux (avant et arrière)...")
print("Appuyez sur Ctrl+C pour arrêter\n")

listener = mouse.Listener(on_click=on_click)
listener.start()

try:
    listener.join()
except KeyboardInterrupt:
    print("\n✓ Test terminé")
    listener.stop()
