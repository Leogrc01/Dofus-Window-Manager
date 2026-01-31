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
- ⌨️ Personnaliser les touches de navigation (suivant/précédent)
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
- **`** (backtick) : Passer au personnage suivant dans l'ordre d'initiative **(personnalisable)**
- **\\** (backslash) : Passer au personnage précédent dans l'ordre d'initiative **(personnalisable)**
- **Ctrl+Alt+O** : Afficher/masquer l'overlay
- **Ctrl+Alt+C** : Modifier la configuration en temps réel
- **Ctrl+Alt+Q** : Quitter l'application complètement

💡 **Clavier 60% ?** Les touches **Suivant** et **Précédent** sont personnalisables dans la fenêtre de configuration !

### Comment quitter

- **Raccourci** : `Ctrl+Alt+Q`
- **System Tray** : Clic droit sur l'icône dans la barre des tâches → Quitter
- L'overlay et tous les raccourcis seront désactivés automatiquement

### Overlay

L'overlay affiche :
```
[PANDA] → ENU → ENI → IOP → CRA → SRAM → FEC → OSAMODAS
  ^^^
  Perso actif (surligné)
```

### Modification de la configuration en temps réel

Vous pouvez modifier l'ordre d'initiative **pendant que l'application fonctionne** sans avoir à la redémarrer :

1. **Appuyez sur Ctrl+Alt+C** (ou clic droit sur l'icône system tray → "Modifier la configuration")
2. La fenêtre de configuration s'ouvre avec les fenêtres DOFUS actuelles
3. Modifiez l'ordre, les noms, **et les raccourcis de navigation**
4. Cliquez sur **"Sauvegarder & Appliquer"**
5. La configuration est immédiatement appliquée et l'overlay se met à jour

⚡ Aucun besoin de redémarrer l'application ou l'overlay !

#### Personnaliser les raccourcis de navigation

Dans la section **⌨️ Raccourcis de navigation** de la fenêtre de configuration :
- **Personnage suivant** : Par défaut `` ` `` - changez-le pour `tab`, `é`, `a`, etc.
- **Personnage précédent** : Par défaut `\` - changez-le pour `shift+tab`, `&`, `z`, etc.

Exemples pour claviers 60% :
- `tab` et `shift+tab`
- `é` et `&` (touches numériques azerty)
- `q` et `w`

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
