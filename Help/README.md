# 📚 Système d'Aide - Help System

## Vue d'ensemble

Ce dossier contient tous les fichiers d'aide intégrés dans l'application. Les aides sont écrites en **Markdown** et traduites en français, anglais et allemand.

## 📁 Structure

```
Help/
├── README.md                 <- Ce fichier
├── fr/                       <- Aides en français
│   ├── character_create.md   <- Créer un personnage
│   ├── character_edit.md     <- Éditer un personnage (à venir)
│   └── ...
├── en/                       <- Aides en anglais
│   ├── character_create.md   <- Create a character (à traduire)
│   └── ...
├── de/                       <- Aides en allemand
│   ├── character_create.md   <- Charakter erstellen (à traduire)
│   └── ...
└── images/                   <- Captures d'écran partagées
    └── ...
```

## 🎯 Convention de Nommage

### Fichiers
- **Format** : `nom_descriptif.md` (tout en minuscules, underscore comme séparateur)
- **Exemples** :
  - `character_create.md` : Créer un personnage
  - `character_edit.md` : Éditer un personnage
  - `character_import.md` : Importer depuis Eden
  - `cookies_management.md` : Gérer les cookies
  - `realm_ranks.md` : Rangs de royaume
  - `armor_management.md` : Gestion des armures
  - `settings.md` : Configuration
  - `troubleshooting.md` : Dépannage

### Images
- **Format** : `nom_aide_numero.png`
- **Exemples** :
  - `character_create_01.png` : Première capture pour "créer un personnage"
  - `character_create_02.png` : Deuxième capture
  - `cookies_management_01.png` : Première capture pour "gérer les cookies"

## ✍️ Format des Aides

Chaque fichier d'aide suit ce template Markdown :

```markdown
# [Titre avec Emoji]

## 📋 Résumé
[Description courte de 1-2 lignes]

## 🎯 Objectif
[Ce que l'utilisateur va apprendre]

## 📝 Étapes Détaillées

### Étape 1 : [Titre]
[Description détaillée avec captures si nécessaire]

### Étape 2 : [Titre]
[Description détaillée]

## ⚡ Raccourcis Clavier
[Table des raccourcis]

## ⚠️ Erreurs Courantes
[Liste des erreurs fréquentes et solutions]

## 💡 Astuces et Conseils
[Tips avancés]

## 🔗 Voir Aussi
[Liens vers autres aides connexes]

## 📞 Besoin d'Aide ?
[Comment obtenir plus d'aide]
```

## 🎨 Emojis Recommandés

### Par Section
- 📋 Résumé
- 🎯 Objectif
- 📝 Étapes
- ⚡ Raccourcis
- ⚠️ Attention/Erreurs
- 💡 Astuces
- 🔗 Liens
- 📞 Contact/Support

### Par Thème
- 👤 Personnages
- 🏰 Royaumes
- 🛡️ Armures
- 🌐 Eden/Herald
- 🍪 Cookies
- ⚙️ Configuration
- 🐛 Debug/Dépannage
- 📊 Statistiques
- 📥 Import
- 📤 Export
- ✅ Succès/Validation
- ❌ Erreur
- 🔧 Outils
- 📚 Documentation

## 🌍 Traduction

### Priorité des Langues
1. **Français** (FR) : Langue principale, à créer en premier
2. **Anglais** (EN) : À traduire dans les 1-2 semaines
3. **Allemand** (DE) : À traduire dans les 1-2 semaines

### Processus de Traduction
1. Créer l'aide complète en **français**
2. Copier le fichier dans `en/` et `de/`
3. Marquer `[À TRADUIRE]` dans le titre
4. Traduire le contenu
5. Vérifier les images (certaines peuvent contenir du texte)

### Traduction des Titres
| FR | EN | DE |
|----|----|----|
| Créer un personnage | Create a Character | Charakter erstellen |
| Éditer un personnage | Edit a Character | Charakter bearbeiten |
| Importer depuis Eden | Import from Eden | Von Eden importieren |
| Gérer les cookies | Manage Cookies | Cookies verwalten |
| Configuration | Settings | Einstellungen |
| Dépannage | Troubleshooting | Fehlerbehebung |

## 📸 Captures d'Écran

### Recommandations
- **Format** : PNG (compression optimale)
- **Largeur maximale** : 800px
- **Annotations** : Utiliser des flèches et numéros rouges
- **Zones sensibles** : Flouter les informations personnelles
- **Cohérence** : Toujours le même thème Windows

### Outils Recommandés
- **Windows** : Outil Capture d'écran (Win+Shift+S)
- **Annotations** : Paint.NET, GIMP, ou Greenshot
- **Optimisation** : TinyPNG, ImageOptim

## 🔗 Liens Internes

Pour faire référence à une autre aide :
```markdown
[Texte du lien](nom_fichier.md)
```

Exemples :
```markdown
- Voir aussi : [Importer depuis Eden](character_import.md)
- Pour plus d'infos : [Configuration](settings.md)
```

## 📊 Statistiques

### Aides Disponibles
- ✅ `character_create.md` (FR) - Créer un personnage
- ⬜ `character_edit.md` - À créer
- ⬜ `character_import.md` - À créer
- ⬜ `cookies_management.md` - À créer
- ⬜ `settings.md` - À créer

### Progression
- **FR** : 1/20 (5%)
- **EN** : 0/20 (0%)
- **DE** : 0/20 (0%)

## 🚀 Feuille de Route

### Phase 1 (v0.106) - Essentiels
- [x] Infrastructure (HelpManager, HelpWindow)
- [x] Aide : Créer un personnage (FR)
- [ ] Aide : Créer un personnage (EN/DE)
- [ ] Captures d'écran pour création
- [ ] Aide : Importer depuis Eden (FR/EN/DE)
- [ ] Aide : Gérer les cookies (FR/EN/DE)

### Phase 2 (v0.107) - Expansion
- [ ] Aide : Éditer un personnage
- [ ] Aide : Rangs de royaume
- [ ] Aide : Gestion des armures
- [ ] Aide : Configuration
- [ ] Index des aides

### Phase 3 (v0.108) - Avancé
- [ ] Aide contextuelle (F1)
- [ ] Recherche dans les aides
- [ ] Tutoriels interactifs
- [ ] Vidéos tutoriels

## 🐛 Problèmes Connus

Aucun pour le moment.

## 📝 Notes pour les Développeurs

### Ajouter une Nouvelle Aide

1. **Créer le fichier Markdown**
   ```bash
   # Dans Help/fr/
   touch nouvelle_aide.md
   ```

2. **Remplir avec le template**
   - Copier la structure depuis un fichier existant
   - Adapter le contenu

3. **Ajouter dans HelpManager**
   ```python
   # Dans help_manager.py, méthode _get_default_title()
   'nouvelle_aide': {
       'fr': 'Titre FR',
       'en': 'Title EN',
       'de': 'Titel DE'
   }
   ```

4. **Ajouter dans le menu**
   ```python
   # Dans ui_manager.py, méthode create_menu_bar()
   help_action = QAction(lang.get("menu_help_nouvelle_aide"), self.main_window)
   help_action.triggered.connect(self.main_window.show_help_nouvelle_aide)
   help_menu.addAction(help_action)
   ```

5. **Ajouter la méthode dans main.py**
   ```python
   def show_help_nouvelle_aide(self):
       from Functions.help_manager import HelpManager
       help_manager = HelpManager(language=self.current_language)
       help_manager.show_help('nouvelle_aide', parent=self)
   ```

6. **Ajouter les traductions**
   ```json
   // Dans Language/fr.json
   "menu_help_nouvelle_aide": "📖 Titre de l'aide"
   ```

### Tester une Aide

```python
# Test simple
from Functions.help_manager import HelpManager

help_manager = HelpManager(language='fr')
help_manager.show_help('character_create')
```

## 📞 Contact

Pour toute question sur le système d'aide :
- Ouvrir une issue GitHub
- Consulter la documentation complète : [HELP_SYSTEM_PLAN.md](../Documentation/HELP_SYSTEM_PLAN.md)

---

**Dernière mise à jour** : 30 octobre 2025  
**Version** : 1.0  
**Mainteneur** : Ewoline
