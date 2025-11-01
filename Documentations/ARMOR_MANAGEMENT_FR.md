# Armor Management System Documentation

## Vue d'ensemble

Le système de gestion des armures permet aux utilisateurs d'uploader et de gérer des fichiers d'armure créés avec des logiciels tiers (par exemple, des captures d'écran, des configurations PDF, des fichiers texte, etc.) pour chaque personnage.

## Fonctionnalités

### 1. Upload de fichiers d'armure
- Support de tous les formats de fichiers (PNG, JPG, PDF, TXT, etc.)
- Gestion automatique des doublons (ajout de suffixes _1, _2, etc.)
- Organisation par ID de personnage dans des sous-dossiers dédiés

### 2. Liste et visualisation
- Affichage en tableau avec :
  - Nom du fichier
  - Taille (KB/MB)
  - Date de modification
  - Actions (Ouvrir, Supprimer)
- Ouverture automatique avec l'application par défaut du système

### 3. Configuration flexible
- Chemin du dossier d'armures configurable dans Paramètres > Chemins des dossiers
- Chemin par défaut : `Armures/` dans le répertoire de l'application
- Création automatique des répertoires nécessaires

## Architecture

### Structure des dossiers
```
Armures/
  ├── character_id_1/
  │   ├── armor_setup_1.png
  │   ├── armor_setup_2.png
  │   └── notes.txt
  ├── character_id_2/
  │   └── armor_template.pdf
  └── ...
```

### Composants

#### 1. `Functions/armor_manager.py`
**Classe `ArmorManager`**
- `__init__(character_id)` : Initialise le manager pour un personnage spécifique
- `upload_armor(source_file_path)` : Upload un fichier et gère les doublons
- `list_armors()` : Retourne la liste des fichiers avec métadonnées
- `delete_armor(filename)` : Supprime un fichier d'armure
- `open_armor(filename)` : Ouvre un fichier avec l'application par défaut
- `get_armor_count()` : Retourne le nombre d'armures

#### 2. `Functions/path_manager.py`
Nouvelles fonctions :
- `get_armor_dir()` : Retourne le chemin du dossier d'armures depuis la config
- `ensure_armor_dir()` : Crée le dossier d'armures s'il n'existe pas

#### 3. `UI/dialogs.py`
**Classe `ArmorManagementDialog`**
- Interface de gestion avec tableau et boutons
- Rafraîchissement automatique après chaque opération
- Confirmations de suppression
- Messages de succès/erreur

**Modifications `CharacterSheetWindow`**
- Ajout du bouton "📁 Gérer les armures" dans la section Armure
- Méthode `open_armor_manager()` pour ouvrir le dialog

**Modifications `ConfigurationDialog`**
- Ajout du champ "Dossier des armures" avec bouton de navigation
- Mise à jour automatique depuis la configuration
- Sauvegarde dans `config.json`

## Utilisation

### Pour l'utilisateur

1. **Ouvrir la gestion des armures**
   - Ouvrir la fiche d'un personnage
   - Cliquer sur "📁 Gérer les armures" dans la section Armure

2. **Uploader un fichier**
   - Cliquer sur "📤 Uploader un fichier"
   - Sélectionner le fichier depuis l'explorateur
   - Le fichier est copié dans le dossier du personnage

3. **Visualiser une armure**
   - Cliquer sur "🔍 Ouvrir" pour le fichier souhaité
   - Le fichier s'ouvre avec l'application par défaut

4. **Supprimer une armure**
   - Cliquer sur "🗑️ Supprimer"
   - Confirmer la suppression

5. **Configurer le chemin**
   - Menu "Paramètres" > "Configuration"
   - Section "Chemins des dossiers"
   - Modifier "Dossier des armures"

### Pour le développeur

#### Créer un ArmorManager pour un personnage
```python
from Functions.armor_manager import ArmorManager

# Initialisation
armor_mgr = ArmorManager(character_id="char_001")

# Upload d'un fichier
result_path = armor_mgr.upload_armor("/path/to/armor_setup.png")

# Lister les armures
armors = armor_mgr.list_armors()
for armor in armors:
    print(f"{armor['filename']}: {armor['size']} bytes, modified {armor['modified']}")

# Supprimer une armure
armor_mgr.delete_armor("armor_setup.png")

# Ouvrir une armure
armor_mgr.open_armor("armor_setup.png")
```

#### Structure des données retournées par `list_armors()`
```python
[
    {
        'filename': 'armor_setup.png',
        'path': '/full/path/to/armor_setup.png',
        'size': 102400,  # en bytes
        'modified': 1234567890.0  # timestamp Unix
    },
    ...
]
```

## Tests

Un script de test complet est disponible : `Scripts/test_armor_manager.py`

Pour exécuter les tests :
```powershell
python Scripts/test_armor_manager.py
```

Les tests couvrent :
- Création et vérification des chemins
- Upload de fichiers
- Gestion des doublons
- Suppression de fichiers
- Liste et métadonnées

## Gestion des erreurs

Toutes les opérations incluent :
- Logging détaillé (INFO, ERROR)
- Messages d'erreur utilisateur via QMessageBox
- Gestion des exceptions (fichiers manquants, permissions, etc.)

## Évolutions futures possibles

1. **Filtrage par type de fichier** : Ajouter des filtres dans la liste (Images, PDF, Texte)
2. **Prévisualisation** : Afficher une miniature pour les images
3. **Métadonnées** : Ajouter des champs personnalisés (description, tags)
4. **Export/Import** : Partager des configurations d'armure entre personnages
5. **Versioning** : Gérer plusieurs versions d'une même armure
6. **Templates** : Bibliothèque de templates d'armure par classe/race

## Configuration JSON

Nouvelle clé dans `Configuration/config.json` :
```json
{
  "armor_folder": "C:/Path/To/Armures",
  ...
}
```

Si non définie, utilise le chemin par défaut : `<app_dir>/Armures`

## Compatibilité

- ✅ Windows (testé avec `os.startfile`)
- ⚠️ macOS/Linux : Nécessite adaptation de `open_armor()` (utiliser `xdg-open` ou `open`)

## Notes techniques

- **Sécurité** : Les fichiers sont copiés (pas déplacés) pour préserver les originaux
- **Performance** : Utilisation de `shutil.copy2` pour préserver les métadonnées
- **Portabilité** : Chemins absolus stockés dans la configuration, relatifs dans le code
- **Architecture drive-in** : Toutes les opérations utilisent des chemins configurables

---

**Version** : 0.105  
**Date** : Décembre 2024  
**Auteur** : Système de gestion des personnages DAOC
