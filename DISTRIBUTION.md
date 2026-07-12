# 🎮 DOFUS Window Switcher - Version Exécutable

## 📦 Fichier inclus

- **DOFUS-Window-Switcher.exe** - Application tout-en-un (configuration + switcher)

## 🚀 Installation

1. Téléchargez `DOFUS-Window-Switcher.exe`
2. Placez-le dans un dossier de votre choix
3. C'est tout ! Aucune installation Python requise.

## ⚙️ Utilisation

### Première utilisation

1. **Lancez DOFUS** avec tous vos personnages (jusqu'à 8 fenêtres)
2. **Double-cliquez sur `DOFUS-Window-Switcher.exe`**
3. L'interface de configuration s'ouvre et affiche toutes les fenêtres DOFUS détectées
4. Pour chaque fenêtre :
   - Choisissez la **Position** (ordre d'initiative : 1 à 8)
   - Vérifiez la **Classe** (auto-détectée, modifiable)
5. Cliquez sur **🚀 Sauvegarder & Lancer**
6. L'application se lance automatiquement avec l'overlay et les raccourcis actifs !

### Utilisation quotidienne

Double-cliquez sur `DOFUS-Window-Switcher.exe`, puis **"▶ Lancer"** : les fenêtres
sont retrouvées automatiquement par nom de personnage, même après un redémarrage
de DOFUS. La reconfiguration n'est nécessaire que pour changer l'ordre, les noms
ou les raccourcis.

## 🎮 Raccourcis

Une fois l'application lancée :

- **F1-F8** : Switch direct vers le personnage 1-8
- **`** (backtick) : Personnage suivant dans l'ordre
- **\\** (backslash) : Personnage précédent dans l'ordre
- **Ctrl+Alt+O** : Afficher/masquer l'overlay
- **Ctrl+Alt+W** : Roue de sélection radiale
- **Ctrl+Alt+H** : Assistant chasse au trésor (données DofusDB, `/travel` auto-copié)
- **Ctrl+Alt+C** : Modifier la configuration
- **Ctrl+Alt+Q** : **Quitter l'application complètement**

💡 Les touches de switch ne réagissent que si une fenêtre DOFUS est au premier
plan (désactivable via `"only_in_game": false` dans `config.json`).

### 🚪 Comment arrêter l'application

1. **Raccourci clavier** : Appuyez sur `Ctrl+Alt+Q`
2. **Icône system tray** : Faites un clic droit sur l'icône verte dans la barre des tâches (en bas à droite) → "Quitter"

L'overlay disparaîtra et tous les raccourcis seront désactivés.

## 📊 Overlay Visuel

L'overlay (coins arrondis, icônes de classe) affiche en temps réel :
```
Roublard › Sram › Pandawa › Eniripsa › Sacrieur › Iop › Sadida › Zobal
```
- **Bordeaux** : Personnage actuellement actif (suit aussi vos alt-tab et clics)
- **Doré** : Prochain personnage

Vous pouvez déplacer l'overlay en le glissant avec la souris.

## ❓ Dépannage

### L'application ne démarre pas
- **Antivirus** : Ajoutez les .exe à la liste blanche
- **Windows Defender** : Autorisez l'exécution (c'est normal pour les exe Python)

### Les fenêtres ne switchent pas
1. Vérifiez que DOFUS est bien lancé et au premier plan (les touches de switch
   sont filtrées hors du jeu par défaut)
2. Le re-matching automatique retrouve les fenêtres en ~5 secondes après un
   redémarrage de DOFUS ; si un personnage a changé de nom, refaites la
   configuration (Ctrl+Alt+C)

### L'overlay ne s'affiche pas
- Appuyez sur **Ctrl+Alt+O** pour le réafficher
- Vérifiez qu'il n'est pas caché derrière une fenêtre

## 📝 Notes

- Les fichiers `config.json` (configuration) et `hunt_clues_cache.json` (cache
  des indices de chasse, 7 jours) vivent dans `%APPDATA%\DofusWindowManager\`
  (migration automatique depuis l'ancien emplacement à côté de l'exe)
- Les fenêtres sont retrouvées automatiquement par nom de personnage après un
  redémarrage de DOFUS — pas besoin de reconfigurer
- L'assistant chasse au trésor nécessite une connexion internet (API DofusDB)
- **Démarrer avec Windows** : activable dans le menu de l'icône system tray
- L'app vérifie au lancement si une version plus récente existe sur GitHub
  et vous en informe par notification (silencieux hors ligne)

## 🔒 Sécurité

Ces executables sont créés avec PyInstaller depuis le code source Python.
Si votre antivirus bloque l'exe, c'est une fausse alerte courante avec PyInstaller.
Vous pouvez vérifier le code source sur : [votre-repo-github]

## 💡 Astuces

- **Raccourci Windows** : Créez un raccourci de `DOFUS-Window-Switcher.exe` sur votre bureau
- **Lancement rapide** : Placez l'exe dans un dossier facile d'accès
- **Personnalisation** : Éditez `config.json` pour changer les raccourcis clavier
- **Si déjà configuré** : Cliquez sur "▶ Lancer" au lieu de "Sauvegarder & Lancer" pour lancer directement

---

Bon jeu ! 🎯
