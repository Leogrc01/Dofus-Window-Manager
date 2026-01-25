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

À chaque fois que vous relancez DOFUS :
1. Double-cliquez sur `DOFUS-Window-Switcher.exe`
2. Vérifiez/ajustez l'ordre si nécessaire (les handles de fenêtre changent)
3. Cliquez sur **🚀 Sauvegarder & Lancer**

## 🎮 Raccourcis

Une fois l'application lancée :

- **F1-F8** : Switch direct vers le personnage 1-8
- **`** (backtick) : Personnage suivant dans l'ordre
- **\\** (backslash) : Personnage précédent dans l'ordre
- **Ctrl+Alt+O** : Afficher/masquer l'overlay
- **Ctrl+Alt+Q** : **Quitter l'application complètement**

### 🚪 Comment arrêter l'application

1. **Raccourci clavier** : Appuyez sur `Ctrl+Alt+Q`
2. **Icône system tray** : Faites un clic droit sur l'icône verte dans la barre des tâches (en bas à droite) → "Quitter"

L'overlay disparaîtra et tous les raccourcis seront désactivés.

## 📊 Overlay Visuel

L'overlay affiche en temps réel :
```
[Roublard] → Sram → Pandawa → Eniripsa → Sacrieur → Iop → Sadida → Zobal
```
- **[Vert]** : Personnage actuellement actif
- **Orange** : Prochain personnage

Vous pouvez déplacer l'overlay en le glissant avec la souris.

## ❓ Dépannage

### L'application ne démarre pas
- **Antivirus** : Ajoutez les .exe à la liste blanche
- **Windows Defender** : Autorisez l'exécution (c'est normal pour les exe Python)

### Les fenêtres ne switchent pas
1. Relancez `DOFUS-Window-Switcher.exe` et refaites la configuration
2. Vérifiez que DOFUS est bien lancé
3. Les handles de fenêtre changent à chaque lancement de DOFUS

### L'overlay ne s'affiche pas
- Appuyez sur **Ctrl+Alt+O** pour le réafficher
- Vérifiez qu'il n'est pas caché derrière une fenêtre

## 📝 Notes

- Le fichier `config.json` est créé automatiquement dans le même dossier que les .exe
- Ce fichier contient votre configuration (ordre, noms, raccourcis)
- **Important** : Les handles de fenêtre Windows changent à chaque redémarrage de DOFUS, donc relancez la config après chaque restart !

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
