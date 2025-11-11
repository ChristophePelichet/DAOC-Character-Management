# Bannières de Classe - Documentation Technique

## 📋 Vue d'ensemble

Cette fonctionnalité ajoute des **bannières visuelles de classe** sur le côté gauche de la fiche personnage, permettant une identification visuelle rapide de la classe du personnage.

## ✨ Fonctionnalités

### Affichage Automatique
- ✅ La bannière s'affiche automatiquement lors de l'ouverture d'une fiche personnage
- ✅ La bannière se met à jour dynamiquement lors du changement de classe ou de royaume
- ✅ Support des 3 royaumes : Albion, Hibernia, Midgard
- ✅ Support de toutes les classes DAOC (44 classes au total)

### Interface Utilisateur
- **Position** : Côté gauche de la fenêtre
- **Largeur fixe** : 150px
- **Hauteur** : Variable selon l'image (ratio conservé)
- **Mise à l'échelle** : Automatique avec transformation lisse

## 🏗️ Architecture

### Structure des Fichiers

```
Img/Banner/
├── README.md                  # Documentation utilisateur
├── Alb/                       # Bannières Albion (15 classes)
│   ├── armsman.jpg
│   ├── paladin.jpg
│   └── ...
├── Hib/                       # Bannières Hibernia (15 classes)
│   ├── druid.jpg
│   ├── warden.jpg
│   └── ...
└── Mid/                       # Bannières Midgard (14 classes)
    ├── berserker.jpg
    ├── healer.jpg
    └── ...
```

### Conventions de Nommage

- **Dossier** : Abréviation du royaume (`Alb`, `Hib`, `Mid`)
- **Fichier** : Nom de classe anglais en minuscules + extension (`.jpg` ou `.png`)
- **Exemple** : `Img/Banner/Hib/druid.jpg`

## 🔧 Implémentation Technique

### Fichiers Modifiés

**UI/dialogs.py** :
- `CharacterSheetWindow.__init__()` : Layout horizontal avec bannière à gauche
- `_update_class_banner()` : Mise à jour de la bannière
- `_set_banner_placeholder()` : Affichage placeholder si bannière manquante
- `_on_realm_changed_sheet()` : Hook pour mise à jour lors du changement de royaume
- `_on_class_changed_sheet()` : Hook pour mise à jour lors du changement de classe

### Code Principal

```python
# Layout horizontal principal
main_horizontal = QHBoxLayout(self)

# Bannière à gauche (150px fixe)
self.banner_label = QLabel()
self.banner_label.setFixedWidth(150)
self.banner_label.setAlignment(Qt.AlignmentFlag.AlignTop)
self._update_class_banner()
main_horizontal.addWidget(self.banner_label)

# Contenu à droite (extensible)
layout = QVBoxLayout()
# ... contenu de la fenêtre ...
main_horizontal.addLayout(layout, 1)
```

### Logique de Chargement

```python
def _update_class_banner(self):
    """Mise à jour de la bannière selon classe/royaume"""
    realm = self.character_data.get('realm', 'Albion')
    class_name = self.character_data.get('class', '')
    
    if not class_name:
        # Placeholder si pas de classe
        self._set_banner_placeholder("No\nClass\nSelected")
        return
    
    # Mapping royaume -> dossier
    realm_map = {"Albion": "Alb", "Hibernia": "Hib", "Midgard": "Mid"}
    realm_folder = realm_map.get(realm, realm)
    
    # Nom fichier en minuscules
    class_filename = class_name.lower().replace(" ", "_")
    
    # Chemins possibles (.jpg puis .png)
    banner_path = f"Img/Banner/{realm_folder}/{class_filename}.jpg"
    if not os.path.exists(banner_path):
        banner_path = f"Img/Banner/{realm_folder}/{class_filename}.png"
    
    if os.path.exists(banner_path):
        # Charger et afficher l'image
        pixmap = QPixmap(banner_path)
        scaled_pixmap = pixmap.scaledToWidth(150, Qt.SmoothTransformation)
        self.banner_label.setPixmap(scaled_pixmap)
    else:
        # Bannière non trouvée
        self._set_banner_placeholder(f"Banner\nnot found:\n{realm}\n{class_name}")
```

### Mise à Jour Dynamique

```python
def _on_realm_changed_sheet(self):
    """Hook lors du changement de royaume"""
    self._populate_classes_sheet()
    self._populate_races_sheet()
    self.character_data['realm'] = self.realm_combo.currentText()
    self._update_class_banner()  # ← Mise à jour bannière

def _on_class_changed_sheet(self):
    """Hook lors du changement de classe"""
    self._populate_races_sheet()
    class_data = self.class_combo.currentData()
    if class_data:
        self.character_data['class'] = class_data
        self._update_class_banner()  # ← Mise à jour bannière
```

## 🎨 Génération des Bannières

### Script Automatique

**Scripts/create_class_banners.py** :
- Génère automatiquement des bannières placeholder pour toutes les classes
- Couleurs par royaume : Rouge (Alb), Vert (Hib), Bleu (Mid)
- Dégradé vertical + bordure dorée
- Texte avec ombre portée
- Qualité JPEG 95%

### Utilisation

```bash
python Scripts/create_class_banners.py
```

### Résultat

- ✅ 41 bannières créées automatiquement
- ⏭️ 3 bannières existantes préservées (druid, animist, warden)
- 📁 Total: 44 bannières (toutes les classes DAOC)

### Caractéristiques des Placeholders

- **Dimensions** : 150x400px
- **Format** : JPEG
- **Dégradé** : Couleur royaume (sombre en bas)
- **Texte** : Royaume (haut) + Classe (centre)
- **Bordure** : 3px dorée

## 📝 Gestion des Cas Limites

### Pas de Classe Assignée
```
Affichage: "No\nClass\nSelected" (texte gris italique centré)
```

### Bannière Manquante
```
Affichage: "Banner\nnot found:\n{Realm}\n{Class}" (texte gris italique)
Solution: Exécuter create_class_banners.py ou ajouter manuellement
```

### Image Invalide
```
Affichage: "Invalid\nimage:\n{Class}" (texte gris italique)
Solution: Remplacer par une image valide (JPG/PNG)
```

### Changement de Royaume/Classe
```
Comportement: Mise à jour immédiate de la bannière
Performances: Instantané (cache Qt)
```

## 🔄 Workflow Utilisateur

### Création Manuelle de Personnage
1. Utilisateur ouvre dialogue "Nouveau Personnage"
2. Sélectionne Royaume → Placeholder "No Class Selected"
3. Sélectionne Classe → Bannière apparaît instantanément
4. Change Classe → Bannière se met à jour
5. Change Royaume → Bannière change de dossier + mise à jour

### Import Simple/Masse
1. Données importées depuis Herald/CSV
2. Fiche personnage ouverte
3. Classe/Royaume déjà définis
4. Bannière affichée automatiquement au chargement

### Modification Ultérieure
1. Utilisateur ouvre fiche personnage existant
2. Bannière affichée selon classe/royaume enregistrés
3. Modification classe/royaume → Mise à jour instantanée
4. Sauvegarde → Bannière reste affichée

## 📊 Statistiques

### Classes Par Royaume
- **Albion** : 15 classes
- **Hibernia** : 15 classes
- **Midgard** : 14 classes
- **Total** : 44 classes uniques

### Taille des Fichiers
- **Placeholder JPG** : ~15-20 KB chacun
- **Total placeholders** : ~700 KB
- **Bannières custom** : Variable selon source

## 🚀 Améliorations Futures Possibles

### Court Terme
- [ ] Ajouter bannières haute résolution personnalisées
- [ ] Support du drag & drop pour changer bannières
- [ ] Bouton "Changer bannière" dans fiche personnage

### Moyen Terme
- [ ] Galerie de bannières intégrée
- [ ] Téléchargement bannières depuis communauté
- [ ] Animations de transition lors du changement

### Long Terme
- [ ] Bannières animées (GIF/WebP)
- [ ] Thèmes de bannières (classique, moderne, fantasy)
- [ ] Bannières par serveur (Eden vs Blackthorn)

## 🔗 Liens Utiles

- **Documentation utilisateur** : `Img/Banner/README.md`
- **Script génération** : `Scripts/create_class_banners.py`
- **Code source** : `UI/dialogs.py` (lignes ~80-100, ~690-750)

## 📋 Checklist de Test

- [x] Bannière affichée pour personnage avec classe
- [x] Placeholder pour personnage sans classe
- [x] Mise à jour lors changement classe
- [x] Mise à jour lors changement royaume
- [x] Support JPG et PNG
- [x] Mise à l'échelle conserve ratio
- [x] Placeholder pour bannière manquante
- [x] Génération automatique placeholders
- [x] Toutes les classes (44) ont une bannière

---

**Version** : 0.107  
**Date** : 10 novembre 2025  
**Auteur** : DAOC Character Management Team
