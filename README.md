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

✨ **Re-matching automatique** : la configuration mémorise le *nom du personnage* de chaque fenêtre. Au démarrage (et périodiquement pendant l'exécution), l'application retrouve automatiquement les fenêtres DOFUS par leur titre, même après un redémarrage du jeu. Plus besoin de reconfigurer à chaque relance — l'interface de configuration ne sert plus qu'à changer l'ordre, les noms ou les raccourcis.

### Configuration manuelle

Vous pouvez aussi éditer `config.json` directement. Le champ `character` (nom du personnage en jeu) sert au re-matching automatique des fenêtres ; les `hwnd` sont mis à jour automatiquement.

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
- **Ctrl+Alt+W** : Roue de sélection radiale
- **Ctrl+Alt+H** : Assistant chasse au trésor
- **Ctrl+Alt+Q** : Quitter l'application complètement

💡 **Clavier 60% ?** Les touches **Suivant** et **Précédent** sont personnalisables dans la fenêtre de configuration !

🎯 **Filtre en jeu** : par défaut, les touches de switch (F1-F8, suivant, précédent) ne réagissent que si une fenêtre DOFUS est au premier plan — elles ne perturbent plus votre navigateur ou Discord. Désactivable avec `"only_in_game": false` dans la section `hotkeys` de `config.json`. Les raccourcis `Ctrl+Alt+*` restent globaux.

🔄 **Overlay synchronisé** : si vous changez de fenêtre par alt-tab ou clic direct, l'overlay et l'ordre de la roue suivent automatiquement la fenêtre réellement active.

🖱️ **Overlay interactif** :
- **Clic gauche** sur un nom → switch direct vers ce personnage
- **Clic droit** sur un nom → le marquer **mort/absent** (barré et grisé) : la rotation suivant/précédent le saute, re-clic droit pour le réactiver. Les touches F1-F8 continuent de fonctionner même sur un perso marqué.
- **Glisser** le bandeau pour le déplacer (un déplacement n'est jamais interprété comme un clic)

### Démarrage & mises à jour

- **Démarrer avec Windows** : activable d'un clic dans le menu de l'icône system tray (clé Run du registre utilisateur, réversible au même endroit).
- **Vérification de mise à jour** : au lancement, l'app compare sa version à la dernière release GitHub et affiche une notification si une plus récente existe (silencieux hors ligne).
- **Données** : `config.json` et le cache de chasse vivent dans `%APPDATA%\DofusWindowManager\` (migration automatique depuis l'ancien emplacement à côté de l'exe).

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

### Assistant chasse au trésor

Plus besoin de Ganymède ou d'un site externe : **Ctrl+Alt+H** ouvre un petit panneau intégré (données DofusDB) :

1. Entrez votre **position** de départ `[x ; y]`
2. Tapez le début de l'**indice** (ex: « fer à ch... ») et validez avec **Entrée** — autocomplétion sans accents
3. Cliquez la **direction** de l'indice (▲ ◄ ► ▼)
4. Le panneau affiche la map cible et copie automatiquement **`/travel x,y`** dans le presse-papier → collez dans le chat du jeu
5. La map trouvée devient votre nouvelle position de départ : enchaînez directement l'indice suivant

- L'ordre indice/direction est libre : la recherche part dès que les deux sont choisis
- « Introuvable (≤ 10 maps) » : l'indice n'existe pas dans cette direction, comme en jeu
- La liste des indices est mise en cache 7 jours (`hunt_clues_cache.json`) — première ouverture avec connexion requise
- **Échap** ferme le panneau

**Historique & retour arrière** : chaque étape résolue s'ajoute à la liste « Étapes » ; le bouton **↩ Retour** annule la dernière étape et restaure la position de départ (pratique quand on s'est trompé de direction).

**Étapes phorreur** : les phorreurs sont invisibles pour les bases de données (objets propres à chaque joueur) — aucun outil ne peut les localiser. Le bouton **Étape phorreur** trace l'étape dans l'historique ; cherchez le phorreur en jeu puis mettez la position à jour (la **molette** sur les champs X/Y fait ±1, pratique en marchant map par map).

**Auto-pilote (optionnel)** : cochez « Écrire /travel dans le jeu » pour que la commande soit tapée directement dans le chat de la fenêtre active (focus + frappe + Entrée) au lieu d'être copiée. Équivalent de l'auto-pilote de Ganymède — désactivé par défaut. Les options sont mémorisées.

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
├── character_wheel.py      # Roue de sélection radiale
├── class_icons.py          # Chargement des icônes de classe
├── config_manager.py       # Gestion de la configuration
└── requirements.txt
```

## 🔧 Technologies

- **pywin32** : API Windows pour la détection et manipulation de fenêtres
- **keyboard** : Gestion des hotkeys globaux
- **tkinter** : Interface graphique overlay
- **pystray** : Icône system tray

## 📦 Release

L'exe est construit et publié automatiquement par GitHub Actions à chaque tag de version :

```bash
git tag v1.2.0
git push origin v1.2.0
```

→ La release apparaît sur GitHub avec `DOFUS-Window-Switcher.exe` attaché et des notes générées depuis les commits. Le workflow peut aussi être lancé manuellement (onglet Actions → Release → Run workflow) pour un build de test sans release.

## 📝 Licence

MIT
