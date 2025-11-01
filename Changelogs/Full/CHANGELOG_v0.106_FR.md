# CHANGELOG v0.106 - Correction Eden Scraping & Auto-Update

**Date** : 2025-11-01  
**Version** : 0.106

## 🐛 Corrections

### Chemin de sauvegarde des cookies Eden (PyInstaller fix)
- **Problème** : Les cookies ne se sauvegardaient pas dans le dossier `Configuration/` par défaut
- **Cause** : Le `CookieManager` utilisait `Path(__file__).parent.parent` qui causait des problèmes avec PyInstaller
- **Solution** : Utilisation de `get_config_dir()` depuis `config_manager.py` pour une cohérence globale
- **Résultat** : Les cookies sont maintenant correctement sauvegardés dans le dossier défini par `config_folder` dans `config.json`
- **Compatibilité** : Compatible avec l'application compilée et l'exécution normale
- **Fichier modifié** : `Functions/cookie_manager.py` (ligne 22-34)

### Configuration des colonnes corrigée
- **Problème 1** : La colonne URL Herald (index 11) n'était pas incluse dans le redimensionnement (`range(11)` au lieu de `range(12)`)
- **Problème 2** : L'ordre des colonnes Class et Level était inversé dans le menu de configuration
- **Problème 3** : Le mapping de visibilité utilisait un ordre incorrect et la colonne URL était absente
- **Solution** : 
  * `apply_column_resize_mode()` traite maintenant les 12 colonnes correctement
  * Ordre du menu de configuration aligné avec le TreeView (Class avant Level)
  * Mapping `column_map` corrigé avec le bon ordre et inclusion de la colonne URL
- **Impact** : Toutes les 12 colonnes (0-11) sont maintenant correctement configurables pour le redimensionnement et la visibilité
- **Fichiers modifiés** : `Functions/tree_manager.py`, `UI/dialogs.py`

## ✨ Améliorations

### Auto-update lors de l'import de personnages
- **Avant** : Si un personnage existe → Erreur "personnage déjà existant"
- **Maintenant** : Si un personnage existe → Mise à jour automatique depuis Herald 🔄
- **Données conservées** : name, realm, season, server, données personnalisées
- **Données mises à jour** : class, race, guild, level, realm_rank, realm_points, url, notes
- **Rapport détaillé** : Affiche le nombre de créations, mises à jour et erreurs
- **Cas d'usage** : Idéal pour garder les personnages à jour via l'import Herald
- **Fichier modifié** : `UI/dialogs.py` - Fonction `_import_characters()` (ligne 2422)

### Dossier des cookies Herald configurable
- **Nouvelle option** : Fenêtre Paramètres → "Répertoire des cookies Herald"
- **Fonctionnalité** : Spécifier un dossier personnalisé pour la sauvegarde des cookies du scraping Eden
- **Interface** : Bouton "Parcourir..." pour faciliter la sélection du dossier
- **Valeur par défaut** : Dossier `Configuration/` (comportement préservé si non configuré)
- **Application portable** : Les chemins sont absolus, pas de dépendance à `__file__`
- **Persistance** : La configuration est sauvegardée dans `config.json` sous la clé `"cookies_folder"`
- **Fallback logique** : Si `cookies_folder` n'est pas défini, utilise `config_folder` (assure la rétrocompatibilité)
- **Fichiers modifiés** : `UI/dialogs.py`, `main.py`, `Functions/cookie_manager.py`

### Unification des labels des répertoires
- **Avant** : Labels mixtes ("Dossier des...", "Répertoire des...")
- **Maintenant** : Tous les chemins de dossiers commencent par "Répertoire"
- **Labels** : 
  * Répertoire des personnages
  * Répertoire de configuration
  * Répertoire des logs
  * Répertoire des armures
  * Répertoire des cookies Herald
- **Suppression des `:` : Plus de deux-points à la fin des labels (ajoutés automatiquement par QFormLayout)
- **Localization** : Traductions complètes en FR, EN, DE
- **Fichiers modifiés** : `UI/dialogs.py`, `Language/fr.json`, `Language/en.json`, `Language/de.json`

### Affichage du début des chemins
- **Avant** : Le curseur était au début mais le texte était aligné sur la fin (affichage de "...Configuration/" dans les QLineEdit)
- **Maintenant** : `setCursorPosition(0)` appliqué à tous les champs de chemins
- **Résultat** : Affichage du début du chemin (ex: "d:\Projets\Python\..." au lieu de "...Configuration/")
- **Fichier modifié** : `UI/dialogs.py` - Méthode `update_fields()` (ligne 1260+)

### Système de diagnostic robuste pour arrêts inattendus
- **Gestionnaire global d'exceptions** : Capture et log toutes les exceptions non gérées
- **Gestionnaire de signaux système** : Détecte SIGTERM, SIGINT et autres interruptions du système d'exploitation
- **Logging des erreurs CRITICAL/ERROR toujours actif** : Même avec debug_mode = OFF, les erreurs sont enregistrées
- **Traçage du démarrage** : Enregistre heure (ISO 8601), version Python, threads actifs
- **Traçage de la fermeture** : Enregistre exactement quand et comment l'app s'arrête
- **Code de sortie** : Affiche le code retourné par la boucle d'événements Qt
- **Fichiers modifiés** : `main.py`, `Functions/logging_manager.py`

### Nettoyage et réorganisation du système CHANGELOGs
- **Ancien système** : CHANGELOGs monolithiques dans `Documentation/` mixant toutes les versions (difficile à naviguer)
- **Nouveau système** : Structure hiérarchique à `Changelogs/` avec séparation claire par version et langage
- **Structure créée** :
  - `Changelogs/Full/` : CHANGELOGs détaillés (~150 lignes) pour v0.106, v0.104 et versions antérieures
  - `Changelogs/Simple/` : Listes concises pour navigation rapide de toutes les 7 versions (v0.1 à v0.106)
  - Support tri-lingual : FR, EN, DE pour chaque fichier
- **Accès centralisé** : Nouveau `CHANGELOG.md` à la racine avec index et navigation vers toutes les versions
- **Ancien contenu** : CHANGELOGs monolithiques supprimés de `Documentation/` (CHANGELOG_FR.md, CHANGELOG_EN.md, CHANGELOG_DE.md)
- **Fichiers créés** : 27 fichiers au total (6 Full + 21 Simple)
- **Résultat** : Système beaucoup plus clair et maintenable pour retrouver les changements par version et langue

## 📊 Impact Général

✅ **Workflow d'import plus intuitif et fluide** - Pas besoin de supprimer/réimporter un personnage existant  
✅ **Mise à jour transparente des stats depuis le Herald** - Les personnages se mettent à jour automatiquement  
✅ **Gestion propre des erreurs avec rapport détaillé** - Nombre de créations, mises à jour et erreurs  
✅ **Flexibilité accrue pour la gestion des cookies** - Chemins personnalisables pour le scraping  
✅ **Portabilité complète de l'application** - Configuration centralisée sans dépendances __file__  
✅ **Capacité à diagnostiquer les arrêts inattendus** - Logs détaillés de tous les événements critiques  
✅ **Interface cohérente et consistante** - Labels uniformisés et affichage optimal des chemins  

## 🔗 Fichiers Modifiés

- `main.py`
- `UI/dialogs.py`
- `Functions/cookie_manager.py`
- `Functions/tree_manager.py`
- `Functions/logging_manager.py`
- `Language/fr.json`
- `Language/en.json`
- `Language/de.json`
