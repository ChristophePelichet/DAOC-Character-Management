# 🔧 Configuration des cookies Herald - Dossier personnalisé

**Version :** 0.106 (Ajout complémentaire)  
**Date :** 1er novembre 2025  
**Type :** Configuration / Amélioration

---

## 📋 Résumé

Ajout d'une option de configuration dans les **Paramètres** permettant de spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Herald.

---

## ✨ Fonctionnalité

### Avant
- Les cookies étaient sauvegardés automatiquement dans le dossier `Configuration/`
- Pas de possibilité de les placer ailleurs
- Risque de partage du dossier Configuration si celui-ci est customisé

### Maintenant
- **Nouveau champ dans Paramètres** : "Dossier des cookies Herald"
- Permet de spécifier n'importe quel dossier pour les cookies
- Par défaut : même dossier que Configuration (comportement identique au précédent)
- Totalement portable et applicable au démarrage de l'application

---

## 🎯 Interface

### Emplacement
- Menu **⚙️ Paramètres** → Onglet **"Chemins des dossiers"**
- Nouvelle ligne après **"Dossier des armures"**

### Champ
```
Dossier des cookies Herald : [__________] [Parcourir]
```

### Fonctionnement
1. **Champ texte** : Affiche le chemin du dossier configuré
2. **Bouton "Parcourir"** : Ouvre un explorateur pour sélectionner le dossier
3. **Sauvegarde automatique** dans `config.json` au clic sur "Enregistrer"

---

## 🔒 Portabilité et sécurité

### ✅ Application portable
- Le chemin est **absolu** (pas de chemin relatif via `__file__`)
- Fonctionne correctement quelle que soit la position du fichier executable
- Compatible PyInstaller
- Compatible démarrage depuis n'importe quel dossier

### ⚙️ Gestion des chemins
```python
# Dans les Paramètres
config.set("cookies_folder", "/chemin/complet/vers/dossier")

# Au démarrage de CookieManager
config.get("cookies_folder")  # Récupère la valeur sauvegardée
```

### 🔄 Fallback intelligent
```python
# Si aucune configuration n'existe
cookies_folder = config.get("cookies_folder") or get_config_dir()
# Utilise le dossier Configuration/ par défaut
```

---

## 📝 Fichiers modifiés

### 1. `UI/dialogs.py` - ConfigurationDialog

#### Ajout du champ (ligne ~1127)
```python
# Cookies Path (for Herald scraping)
self.cookies_path_edit = QLineEdit()
browse_cookies_button = QPushButton(lang.get("browse_button"))
browse_cookies_button.clicked.connect(self.browse_cookies_folder)
cookies_path_layout = QHBoxLayout()
cookies_path_layout.addWidget(self.cookies_path_edit)
cookies_path_layout.addWidget(browse_cookies_button)
paths_layout.addRow(lang.get("config_cookies_path_label", default="Dossier des cookies Herald :"), cookies_path_layout)
```

#### Méthode browse (ligne ~1310)
```python
def browse_cookies_folder(self):
    """Browse for cookies folder."""
    self.browse_folder(self.cookies_path_edit, "select_folder_dialog_title")
```

#### Chargement des paramètres (ligne ~1260)
```python
cookies_folder = config.get("cookies_folder") or get_config_dir()
self.cookies_path_edit.setText(cookies_folder)
```

### 2. `main.py` - save_configuration()

#### Sauvegarde du paramètre (ligne ~600)
```python
config.set("cookies_folder", dialog.cookies_path_edit.text())
```

### 3. `Functions/cookie_manager.py` - __init__()

#### Modification de l'initialisation
```python
if config_dir is None:
    # Utiliser le dossier des cookies depuis la configuration
    from Functions.config_manager import config, get_config_dir
    config_dir = config.get("cookies_folder")
    if not config_dir:
        # Fallback sur le dossier de configuration par défaut
        config_dir = get_config_dir()
```

---

## 🔧 Utilisation

### Cas 1 : Utiliser le dossier par défaut
1. Ouvrir **Paramètres**
2. Le champ affiche : `C:\Users\User\AppData\Roaming\DAOC-Character-Manager\Configuration`
3. Laisser tel quel → Les cookies seront dans Configuration/

### Cas 2 : Utiliser un dossier personnalisé
1. Ouvrir **Paramètres**
2. Cliquer sur **"Parcourir"** à côté du champ "Dossier des cookies Herald"
3. Sélectionner un dossier (ex: `D:\AppData\Cookies\`)
4. Cliquer **"Enregistrer"**
5. Les cookies seront dorénavant sauvegardés dans ce dossier

### Cas 3 : Réappliquer le défaut
1. Ouvrir **Paramètres**
2. Effacer le contenu du champ "Dossier des cookies Herald"
3. Cliquer **"Enregistrer"**
4. Les cookies retourneront au dossier Configuration/

---

## 💾 Configuration JSON

### Format sauvegardé
```json
{
  "cookies_folder": "C:\\Users\\User\\Documents\\MesCookies",
  "config_folder": "C:\\Users\\User\\AppData\\Roaming\\DAOC\\Configuration",
  "character_folder": "C:\\Users\\User\\AppData\\Roaming\\DAOC\\Characters",
  "log_folder": "C:\\Users\\User\\AppData\\Roaming\\DAOC\\Logs",
  "armor_folder": "C:\\Users\\User\\AppData\\Roaming\\DAOC\\Armors"
}
```

### Valeur par défaut
Si `cookies_folder` n'est pas défini → Utilise `config_folder`

---

## 🎨 Comportement

### Création du dossier
- Le dossier est **créé automatiquement** au démarrage de CookieManager
- Aucune action manuelle requise
- Pas d'erreur si le dossier existe déjà

### Permission et accès
- Application doit avoir les droits en **lecture/écriture** sur le dossier
- Si pas de droits → Erreur lors du scraping Herald
- Les cookies sont stockés en binaire (pickle) chiffré

### Fichier généré
```
MonDossierCookies/
├── eden_cookies.pkl  (fichier des cookies chiffré)
└── (autres fichiers si nécessaire)
```

---

## 🧪 Tests

- [x] Charger la configuration par défaut
- [x] Modifier le dossier des cookies
- [x] Sauvegarder la nouvelle configuration
- [x] Redémarrer l'application → Dossier conservé
- [x] CookieManager démarre avec le bon chemin
- [x] Scraping Herald crée les cookies au bon endroit
- [x] Portabilité : Déplacement de l'application → Fonctionne toujours
- [x] Aucune erreur de syntaxe ou imports

---

## ✅ Validation

- ✅ Champ visible dans Paramètres
- ✅ Bouton Parcourir fonctionnel
- ✅ Sauvegarde en JSON
- ✅ Rechargement au démarrage
- ✅ Fallback intelligent si vide
- ✅ CookieManager utilise la config
- ✅ Pas de chemin relatif via `__file__`
- ✅ Application portable

---

## 📝 Cohérence avec autres dossiers

Cette nouvelle option suit le même modèle que les autres chemins configurables :

| Dossier | Clé Config | Défaut | Interface |
|---------|-----------|--------|-----------|
| Personnages | `character_folder` | `Characters/` | ✅ Oui |
| Configuration | `config_folder` | `Configuration/` | ✅ Oui |
| Logs | `log_folder` | `Logs/` | ✅ Oui |
| Armures | `armor_folder` | `Armor/` | ✅ Oui |
| **Cookies** | **`cookies_folder`** | **Configuration/** | **✅ OUI** |

Tous les chemins sont **centralisés et gérables** depuis Paramètres !

---

## 🔄 Évolution future

- [ ] Afficher le statut du dossier (disque, chemin, permissions)
- [ ] Nettoyer les anciens cookies lors du changement de dossier
- [ ] Validation du dossier avant sauvegarde
- [ ] Statistiques d'utilisation des cookies (taille, ancienneté)

