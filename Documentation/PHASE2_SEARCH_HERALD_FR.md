# Phase 2 - Recherche de Personnages Herald

## Date de réalisation
29 octobre 2025

## Objectif
Ajouter une fonctionnalité de recherche de personnages sur le Herald Eden-DAOC avec sauvegarde des résultats en JSON.

## Fonctionnalités implémentées

### 1. Interface utilisateur

#### Bouton de recherche Herald
- **Emplacement** : Barre de statut Eden Herald (entre "Actualiser" et "Gérer")
- **Icône** : 🔍 Recherche Herald
- **Action** : Ouvre une fenêtre de dialogue de recherche

#### Fenêtre de recherche (HeraldSearchDialog)
- **Composants** :
  - Champ de saisie pour le nom du personnage
  - Support de la touche Entrée pour lancer la recherche
  - Barre de statut affichant la progression
  - Boutons : Rechercher, Fermer
- **Comportement** :
  - Recherche en arrière-plan via QThread
  - Interface non bloquante pendant le scraping
  - Messages de succès/erreur avec chemin du fichier JSON

### 2. Backend de scraping

#### Fonction `search_herald_character()` dans `Functions/eden_scraper.py`
- **URL de recherche** : `https://eden-daoc.net/herald?n=search&s={character_name}`
- **Méthode** : Selenium headless avec BeautifulSoup
- **Fonctionnalités** :
  - Vérification des cookies avant la recherche
  - Initialisation du driver Chrome en mode headless
  - Injection des cookies d'authentification
  - Scraping des tableaux de résultats
  - Extraction des données avec headers et cellules
  - Détection des liens dans les cellules
  - Sauvegarde en JSON avec timestamp

#### Structure du fichier JSON
```json
{
  "character_name": "NomPersonnage",
  "search_url": "https://eden-daoc.net/herald?n=search&s=NomPersonnage",
  "timestamp": "2025-10-29T19:26:18.902059",
  "results": [
    {
      "Name": "NomPersonnage",
      "Level": "50",
      "Class": "Classe",
      "Realm": "Royaume",
      "Name_links": ["lien1", "lien2"]
    }
  ]
}
```

#### Stockage des résultats
- **Dossier** : `Configuration/SearchResults/`
- **Nom de fichier** : `search_{character_name}_{timestamp}.json`
- **Format** : JSON avec indentation 2, UTF-8 sans échappement ASCII
- **Création automatique** : Le dossier est créé s'il n'existe pas

### 3. Visualisation des résultats

#### Script `Scripts/view_search_results.py`
- **Fonctionnalités** :
  - Liste tous les fichiers de recherche disponibles
  - Tri par date de modification (plus récent en premier)
  - Affichage des métadonnées (date, taille)
  - Menu interactif pour sélectionner un fichier
  - Deux modes d'affichage :
    1. **Formaté** : Affichage structuré et lisible des résultats
    2. **JSON brut** : Dump JSON complet avec indentation

- **Utilisation** :
  ```bash
  # Mode interactif
  python Scripts/view_search_results.py
  
  # Affichage direct d'un fichier
  python Scripts/view_search_results.py path/to/file.json
  ```

### 4. Tests

#### Script de test `Scripts/test_herald_search.py`
- Vérification des cookies
- Saisie du nom du personnage
- Lancement de la recherche
- Affichage du résultat (succès/échec)
- Indication du chemin du fichier JSON généré

## Fichiers modifiés

### Nouveaux fichiers
1. `UI/dialogs.py` - Ajout de `HeraldSearchDialog` et `SearchThread`
2. `Scripts/view_search_results.py` - Visualiseur de résultats JSON
3. `Scripts/test_herald_search.py` - Script de test de la recherche
4. `Documentation/PHASE2_SEARCH_HERALD_FR.md` - Cette documentation

### Fichiers modifiés
1. `Functions/ui_manager.py`
   - Ajout du bouton "🔍 Recherche Herald" dans `create_eden_status_bar()`

2. `Functions/eden_scraper.py`
   - Ajout de la fonction `search_herald_character(character_name)`
   - Implémentation du scraping de la page de recherche
   - Sauvegarde automatique en JSON

3. `main.py`
   - Ajout de la méthode `open_herald_search()`
   - Connexion au bouton de recherche

## Tests effectués

### Test 1 : Recherche sans résultat
- **Nom** : Testchar
- **Résultat** : 0 résultat trouvé
- **Fichier** : `search_Testchar_20251029_192618.json`
- **Statut** : ✅ Succès

### Test 2 : Visualisation
- **Script** : `view_search_results.py`
- **Fichiers listés** : 1
- **Affichage** : ✅ Formaté et JSON brut fonctionnels
- **Menu interactif** : ✅ Opérationnel

### Test 3 : Script de test
- **Cookies** : ✅ 4 cookies valides jusqu'au 29/10/2026
- **Recherche** : ✅ Terminée avec succès
- **JSON** : ✅ Créé correctement

## Architecture technique

### Thread de recherche (SearchThread)
```python
class SearchThread(QThread):
    search_finished = Signal(bool, str, str)  # (success, message, json_path)
    
    def run(self):
        success, message, json_path = search_herald_character(self.character_name)
        self.search_finished.emit(success, message, json_path)
```

### Workflow complet
1. Utilisateur clique sur "🔍 Recherche Herald"
2. `HeraldSearchDialog` s'ouvre
3. Utilisateur saisit un nom et appuie sur Entrée ou clique sur Rechercher
4. `SearchThread` se lance en arrière-plan
5. `search_herald_character()` :
   - Vérifie les cookies
   - Initialise Selenium headless
   - Charge les cookies
   - Navigue vers l'URL de recherche
   - Scrape les tableaux HTML
   - Sauvegarde en JSON
6. Signal `search_finished` émis
7. Dialog affiche le résultat
8. Utilisateur peut fermer ou faire une nouvelle recherche
9. Visualisation via `view_search_results.py`

## Dépendances utilisées
- **PySide6** : Interface Qt (QDialog, QThread, Signal)
- **Selenium** : Automation du navigateur
- **BeautifulSoup4** : Parsing HTML
- **webdriver_manager** : Gestion automatique de ChromeDriver
- **json** : Sauvegarde et lecture des résultats
- **pathlib** : Gestion des chemins de fichiers

## Améliorations possibles (Phase 3+)

### Court terme
1. Filtres de recherche (realm, level range)
2. Historique des recherches récentes
3. Recherche multiple (plusieurs noms)
4. Export en CSV

### Moyen terme
1. Import direct depuis les résultats de recherche
2. Comparaison avec personnages existants
3. Détection des doublons
4. Statistiques de recherche

### Long terme
1. Cache des résultats de recherche
2. Recherche avancée (guilde, équipement, stats)
3. Graphiques de progression
4. Synchronisation automatique

## Notes techniques

### Gestion des erreurs
- Vérification des cookies avant recherche
- Messages d'erreur détaillés
- Gestion des timeouts Selenium
- Validation de la structure JSON

### Performance
- Recherche en arrière-plan (non bloquante)
- Driver Chrome optimisé (headless)
- Délai de 3 secondes pour le chargement JS
- Fermeture automatique du driver

### Sécurité
- Cookies stockés localement
- Pas d'exposition des credentials
- Validation des entrées utilisateur
- Logs des erreurs

## Conclusion

✅ Phase 2 complète et fonctionnelle

La fonctionnalité de recherche Herald est maintenant intégrée à l'application avec :
- Interface utilisateur intuitive
- Scraping robuste avec Selenium
- Sauvegarde structurée en JSON
- Outil de visualisation dédié
- Tests validés

Le système est prêt pour la Phase 3 : Import et synchronisation des personnages.
