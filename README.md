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

### Configuration graphique (recommandé)

Lancez l'interface de configuration GUI :
```bash
python configure.py
```

Cette interface vous permet de :
- 🔍 Détecter automatiquement vos fenêtres DOFUS
- 🎯 Assigner chaque fenêtre à une position (F1-F8)
- ✏️ Renommer vos personnages (ex: Roublard, Sram, Pandawa...)
- 💾 Sauvegarder la configuration facilement

**Utilisez cette interface à chaque fois que vous relancez DOFUS** pour mettre à jour les handles de fenêtres.

### Configuration manuelle

Vous pouvez aussi éditer `config.json` directement, mais les `hwnd` changent à chaque redémarrage de DOFUS.

## 🎯 Utilisation

```bash
python main.py
```

### Raccourcis par défaut

- **F1-F8** : Switch vers le personnage 1-8
- **`** (backtick) : Passer au personnage suivant dans l'ordre d'initiative
- **\** (backslash) : Passer au personnage précédent dans l'ordre d'initiative
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
