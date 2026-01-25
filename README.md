# 🎮 DOFUS Window Switcher

Utilitaire Windows pour gérer et switcher entre 8 fenêtres DOFUS selon l'ordre d'initiative de combat.

## 💡 Concept

- **Détection automatique** de vos fenêtres DOFUS
- **Ordre fixe personnalisable** pour vos personnages
- **Switch rapide** avec une seule touche par personnage
- **Mode "tour suivant"** : passe automatiquement au prochain perso dans l'ordre
- **Overlay visuel** : bandeau discret montrant l'ordre et le perso actif

## 🚀 Installation

```bash
# Cloner le projet
git clone <repo-url>
cd dofus-window-switcher

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

Au premier lancement, l'application détecte vos fenêtres DOFUS et vous permet de :
- Assigner un nom à chaque fenêtre (ex: PANDA, ENU, ENI, etc.)
- Définir l'ordre d'initiative
- Configurer les raccourcis clavier

La configuration est sauvegardée dans `config.json`.

## 🎯 Utilisation

```bash
python main.py
```

### Raccourcis par défaut

- **F1-F8** : Switch vers le personnage 1-8
- **Tab** : Passer au personnage suivant dans l'ordre d'initiative
- **Ctrl+Alt+O** : Afficher/masquer l'overlay
- **Ctrl+Alt+Q** : Quitter l'application

### Overlay

L'overlay affiche :
```
[PANDA] → ENU → ENI → IOP → CRA → SRAM → FEC → OSAMODAS
  ^^^
  Perso actif (surligné)
```

## 📁 Structure du projet

```
dofus-window-switcher/
├── main.py                 # Point d'entrée
├── window_detector.py      # Détection des fenêtres DOFUS
├── window_manager.py       # Gestion de l'ordre et du switching
├── hotkey_manager.py       # Gestion des raccourcis clavier
├── overlay.py              # Interface overlay
├── config_manager.py       # Gestion de la configuration
└── requirements.txt
```

## 🔧 Technologies

- **pywin32** : API Windows pour la détection et manipulation de fenêtres
- **keyboard** : Gestion des hotkeys globaux
- **tkinter** : Interface graphique overlay
- **pystray** : Icône system tray

## 📝 Licence

MIT
