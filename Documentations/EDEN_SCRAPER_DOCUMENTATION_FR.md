# Documentation Complète du Scraper Eden Herald

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du système](#architecture-du-système)
3. [Flux de fonctionnement détaillé](#flux-de-fonctionnement-détaillé)
4. [Composants principaux](#composants-principaux)
5. [Gestion des cookies](#gestion-des-cookies)
6. [Interface utilisateur](#interface-utilisateur)
7. [Traitement des données](#traitement-des-données)
8. [Gestion des erreurs](#gestion-des-erreurs)

---

## 🎯 Vue d'ensemble

Le scraper Eden Herald permet de rechercher et d'importer automatiquement des personnages depuis le site Herald du serveur Eden DAOC. Il utilise Selenium pour naviguer sur le site web et BeautifulSoup pour analyser les résultats HTML.

### Fonctionnalités principales

- ✅ **Recherche de personnages** par nom avec filtre de royaume optionnel
- ✅ **Vérification automatique** de l'accessibilité du Herald
- ✅ **Gestion des cookies** pour contourner le bot check
- ✅ **Import simple ou en masse** de personnages trouvés
- ✅ **Détection automatique** du royaume selon la classe
- ✅ **Calcul automatique** du rang de royaume (Realm Rank)
- ✅ **Filtrage intelligent** des résultats de recherche
- ✅ **Interface multilingue** (FR, EN, DE)

---

## 🏗️ Architecture du système

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION PRINCIPALE                        │
│                         (main.py)                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├─── UI Manager (Functions/ui_manager.py)
                 │    └─── Barre de statut Eden Herald
                 │         ├─── Label statut
                 │         ├─── Bouton Actualiser
                 │         ├─── Bouton Recherche Herald
                 │         └─── Bouton Gérer (cookies)
                 │
                 ├─── Cookie Manager (Functions/cookie_manager.py)
                 │    ├─── Stockage sécurisé des cookies
                 │    ├─── Chiffrement des données
                 │    ├─── Import/Export
                 │    └─── Validation
                 │
                 ├─── Eden Scraper (Functions/eden_scraper.py)
                 │    ├─── Configuration Selenium
                 │    ├─── Navigation Herald
                 │    ├─── Extraction données
                 │    └─── Gestion bot check
                 │
                 └─── Herald Search Dialog (UI/dialogs.py)
                      ├─── Interface de recherche
                      ├─── Affichage des résultats
                      ├─── Sélection des personnages
                      └─── Import dans la base
```

---

## 🔄 Flux de fonctionnement détaillé

### 1. Vérification initiale du Herald

```
┌──────────────┐
│  Démarrage   │
│ Application  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.create_eden_status_bar()      │
│ - Crée l'interface de statut            │
│ - Désactive boutons Actualiser/Recherche│
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.check_eden_status()           │
│ - Crée EdenStatusThread                 │
│ - Lance vérification en arrière-plan    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│ EdenStatusThread.run()                  │
│ - Charge cookies depuis CookieManager   │
│ - Tente accès https://eden-daoc.net     │
│ - Vérifie présence Herald               │
└──────┬──────────────────────────────────┘
       │
       ├─── ✅ Succès
       │    └──▶ Signal: status_updated(True, "")
       │
       └─── ❌ Échec
            └──▶ Signal: status_updated(False, "message")
       │
       ▼
┌─────────────────────────────────────────┐
│ UIManager.update_eden_status()          │
│ - Met à jour label (✅/❌)              │
│ - Réactive boutons Actualiser/Recherche │
└─────────────────────────────────────────┘
```

### 2. Recherche de personnages

```
┌──────────────────┐
│ Clic utilisateur │
│ "🔍 Recherche     │
│    Herald"       │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ CharacterApp.open_herald_search()          │
│ - Ouvre HeraldSearchDialog                 │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.__init__()              │
│ - Crée interface de recherche              │
│ - Champ texte nom personnage               │
│ - Dropdown filtre royaume (avec logos)     │
│ - Tableau résultats avec checkboxes        │
│ - Boutons Import sélection/tout            │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Utilisateur entre nom (min 3 caractères)  │
│ + sélectionne royaume optionnel            │
│ + clique "Rechercher"                      │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.start_search()          │
│ - Valide longueur >= 3 caractères          │
│ - Récupère realm_filter du dropdown        │
│ - Désactive interface pendant recherche    │
│ - Crée SearchThread                        │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ SearchThread.run()                         │
│ - Appelle eden_scraper.search_herald_...()│
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ eden_scraper.search_herald_character()     │
│ 1. Configure Chrome (off-screen)          │
│ 2. Charge cookies                          │
│ 3. Construit URL avec paramètres           │
│    - name={character_name}                 │
│    - &r={realm} (si filtre actif)          │
│ 4. Navigue vers Herald                     │
│ 5. Extrait données des 28 tables HTML      │
│ 6. Nettoie dossier temporaire              │
│ 7. Sauvegarde JSON dans temp folder        │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Signal: search_finished(success, message,  │
│                         json_path)         │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.on_search_finished()    │
│ - Charge JSON depuis fichier temporaire    │
│ - Filtre: garde seulement noms commençant  │
│   par la requête (startswith)              │
│ - Remplit tableau avec résultats           │
│ - Colorie lignes selon royaume             │
│ - Réactive interface                       │
└────────────────────────────────────────────┘
```

### 3. Import de personnages

```
┌──────────────────┐
│ Utilisateur coche│
│ personnages et   │
│ clique "Import"  │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog.import_selected_...()   │
│ - Récupère lignes cochées                  │
│ - Demande confirmation                     │
│ - Appelle _import_characters()             │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ HeraldSearchDialog._import_characters()    │
│ Pour chaque personnage:                    │
│   1. Récupère données (nom, classe, etc.)  │
│   2. Détecte royaume via CLASS_TO_REALM    │
│   3. Vérifie si déjà existant (doublon)    │
│   4. Crée dict character_data              │
│   5. Appelle save_character()              │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ character_manager.save_character()         │
│ - Sauvegarde dans fichier JSON             │
│   Characters/{realm}/{name}.json           │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Rafraîchissement automatique               │
│ - parent().tree_manager.refresh_...()      │
│ - Affiche nouveaux personnages dans liste  │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ Affiche résultat                           │
│ - ✅ X personnage(s) importé(s)            │
│ - ⚠️ Y erreur(s) (doublons, etc.)         │
└────────────────────────────────────────────┘
```

---

## 🧩 Composants principaux

### 1. UIManager (`Functions/ui_manager.py`)

**Rôle** : Gère l'interface de statut Eden dans la fenêtre principale

#### Méthodes clés

```python
create_eden_status_bar(parent_layout)
```
- Crée le groupe "Statut Eden Herald"
- Initialise les boutons et le label de statut
- Lance la vérification initiale

```python
check_eden_status()
```
- Désactive les boutons pendant la vérification
- Crée un thread de vérification (EdenStatusThread)
- Lance la vérification en arrière-plan

```python
update_eden_status(accessible, message)
```
- Met à jour l'affichage du statut
- Réactive les boutons après vérification
- Affiche ✅ ou ❌ selon le résultat

#### Classe EdenStatusThread

Thread qui vérifie l'accessibilité du Herald sans bloquer l'interface.

**Signal** : `status_updated(bool accessible, str message)`

---

### 2. CookieManager (`Functions/cookie_manager.py`)

**Rôle** : Gère le stockage sécurisé des cookies Eden

#### Structure de stockage

```json
{
  "cookies": [
    {
      "name": "nom_cookie",
      "value": "valeur_chiffrée",
      "domain": ".eden-daoc.net",
      "path": "/",
      "secure": true,
      "httpOnly": false,
      "sameSite": "Lax"
    }
  ],
  "created_at": "2025-01-29T10:30:00",
  "last_used": "2025-01-29T14:45:00"
}
```

#### Méthodes clés

```python
load_cookies_for_selenium(driver)
```
- Charge les cookies depuis le fichier chiffré
- Les injecte dans le navigateur Selenium
- Retourne True si succès, False sinon

```python
import_cookies_from_file(file_path)
```
- Importe cookies depuis un fichier JSON externe
- Valide le format
- Chiffre et sauvegarde

```python
export_cookies_to_file(file_path)
```
- Exporte les cookies actuels vers un fichier
- Déchiffre les valeurs pour l'export

---

### 3. Eden Scraper (`Functions/eden_scraper.py`)

**Rôle** : Scraper principal qui extrait les données du Herald

#### Configuration Selenium

```python
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--window-position=-2400,-2400")  # Off-screen
```

**Important** : Le navigateur est positionné hors écran (`-2400,-2400`) pour rester invisible tout en étant techniquement "visible" (contourne le bot check).

#### Fonction principale

```python
search_herald_character(character_name, realm_filter="")
```

**Paramètres** :
- `character_name` : Nom du personnage à rechercher
- `realm_filter` : "albion", "midgard", "hibernia" ou "" (tous)

**Retour** : `(success: bool, message: str, json_path: str)`

**Processus** :

1. **Nettoyage** : Supprime anciens fichiers temporaires
2. **Configuration** : Configure Chrome avec options spécifiques
3. **Cookies** : Charge les cookies via CookieManager
4. **Navigation** : Accède à `https://eden-daoc.net/herald/character/search`
5. **Requête** : Envoie les paramètres de recherche
6. **Extraction** : Parse 28 tables HTML avec BeautifulSoup
7. **Sauvegarde** : Crée JSON dans `tempfile.gettempdir()/EdenSearchResult/`
8. **Nettoyage** : Ferme le navigateur

#### Structure des tables HTML extraites

Le Herald retourne les données dans 28 tables HTML distinctes :
- Tables 0-27 contiennent chacune des informations de personnages

**Format d'une table** :
```html
<table>
  <tr><td>Rang</td><td>Nom</td><td>Classe</td><td>Race</td>...</tr>
  <tr><td>1</td><td>Ewoline</td><td>Cleric</td><td>Briton</td>...</tr>
</table>
```

#### Colonnes extraites

1. **rank** : Position dans le classement
2. **name** : Nom complet du personnage
3. **clean_name** : Nom nettoyé (sans balises HTML)
4. **class** : Classe du personnage
5. **race** : Race du personnage
6. **guild** : Guilde (ou "Unguilded")
7. **level** : Niveau (1-50)
8. **realm_points** : Points de royaume (format "331 862")
9. **realm_rank** : Rang de royaume (ex: "12L3")
10. **realm_level** : Niveau de rang (ex: "12")
11. **url** : Lien vers la page du personnage

#### Fichiers temporaires générés

```
%TEMP%/EdenSearchResult/
├── search_20250129_143045.json      # Données brutes
└── characters_20250129_143045.json  # Données formatées
```

**Nettoyage** : Les fichiers sont supprimés à la fermeture du dialog de recherche.

---

### 4. Herald Search Dialog (`UI/dialogs.py`)

**Rôle** : Interface de recherche et d'import

#### Classe HeraldSearchDialog

##### Interface

```
┌────────────────────────────────────────────────────┐
│  Recherche de personnages - Eden Herald            │
├────────────────────────────────────────────────────┤
│  Nom du personnage: [___________]                  │
│  Royaume: [Tous les royaumes ▼]                    │
│  [Rechercher]                                      │
├────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐ │
│  │ ☑ │ 🏰 │ Nom    │ Classe │ Race │ Guilde  │ │ │
│  ├───┼────┼────────┼────────┼──────┼─────────┤ │ │
│  │ ☑ │ 🔴 │ Ewoline│ Cleric │Briton│MyGuild  │ │ │
│  │ ☐ │ 🔵 │ Olaf   │ Warrior│ Norseman│      │ │ │
│  │ ☑ │ 🟢 │ Fionn  │ Druid  │ Celt │OtherG   │ │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  [⬇️ Importer sélection] [⬇️⬇️ Importer tout]      │
└────────────────────────────────────────────────────┘
```

##### Méthodes clés

```python
_load_realm_icons_for_combo()
```
- Charge les logos des royaumes (Img/)
- Crée QComboBox avec icônes 20x20
- Options : Tous, Albion, Midgard, Hibernia

```python
start_search()
```
- Valide longueur minimale (3 caractères)
- Récupère le filtre de royaume
- Lance SearchThread

```python
on_search_finished(success, message, json_path)
```
- Charge le JSON des résultats
- **Filtre important** : `name.lower().startswith(query.lower())`
  - Évite les résultats partiels ("oli" ne trouve pas "Ewoline")
- Remplit le tableau avec colonnes colorées
- Applique couleur de fond selon royaume (alpha 50)

```python
import_selected_characters()
```
- Récupère les lignes cochées
- Demande confirmation
- Appelle `_import_characters()`

```python
import_all_characters()
```
- Importe tous les résultats sans confirmation de sélection
- Demande confirmation globale
- Appelle `_import_characters()`

```python
_import_characters(characters)
```
Pour chaque personnage :
1. Extrait `clean_name` ou `name`
2. Détermine royaume via `CLASS_TO_REALM[class]`
3. **Vérifie doublons** :
   ```python
   existing_chars = get_all_characters()
   if any(c.get('name', '').lower() == name.lower() for c in existing_chars):
       # Erreur : personnage déjà existant
   ```
4. Crée `character_data` dict complet
5. Appelle `save_character(character_data)`
6. Compte succès/erreurs
7. Rafraîchit l'interface principale
8. Affiche résultat dans QMessageBox

##### Mapping Classe → Royaume

```python
CLASS_TO_REALM = {
    # Albion
    "Armsman": "Albion", "Cabalist": "Albion", "Cleric": "Albion",
    "Friar": "Albion", "Heretic": "Albion", "Infiltrator": "Albion",
    "Mauler": "Albion", "Mercenary": "Albion", "Minstrel": "Albion",
    "Necromancer": "Albion", "Paladin": "Albion", "Reaver": "Albion",
    "Scout": "Albion", "Sorcerer": "Albion", "Theurgist": "Albion",
    "Wizard": "Albion",
    
    # Midgard
    "Berserker": "Midgard", "Bonedancer": "Midgard", "Healer": "Midgard",
    "Hunter": "Midgard", "Runemaster": "Midgard", "Savage": "Midgard",
    "Shadowblade": "Midgard", "Shaman": "Midgard", "Skald": "Midgard",
    "Spiritmaster": "Midgard", "Thane": "Midgard", "Valkyrie": "Midgard",
    "Warlock": "Midgard", "Warrior": "Midgard",
    
    # Hibernia
    "Animist": "Hibernia", "Bainshee": "Hibernia", "Bard": "Hibernia",
    "Blademaster": "Hibernia", "Champion": "Hibernia", "Druid": "Hibernia",
    "Eldritch": "Hibernia", "Enchanter": "Hibernia", "Hero": "Hibernia",
    "Mentalist": "Hibernia", "Nightshade": "Hibernia", "Ranger": "Hibernia",
    "Valewalker": "Hibernia", "Vampiir": "Hibernia", "Warden": "Hibernia"
}
```

##### Couleurs de royaume (tableau)

```python
REALM_COLORS = {
    "Albion": QColor(204, 0, 0, 50),      # Rouge alpha 50
    "Midgard": QColor(0, 102, 204, 50),   # Bleu alpha 50
    "Hibernia": QColor(0, 170, 0, 50)     # Vert alpha 50
}
```

---

## 🍪 Gestion des cookies

### Pourquoi des cookies ?

Le site Eden Herald utilise un système anti-bot qui nécessite une validation initiale. Les cookies permettent de contourner cette vérification en réutilisant une session authentifiée.

### Processus de récupération des cookies

#### Méthode 1 : Import depuis navigateur

1. Ouvrir Firefox/Chrome
2. Se connecter à https://eden-daoc.net
3. Ouvrir les DevTools (F12)
4. Aller dans l'onglet "Stockage" / "Application"
5. Copier les cookies du domaine `.eden-daoc.net`
6. Créer un fichier JSON :

```json
[
  {
    "name": "__cf_bm",
    "value": "votre_valeur_ici",
    "domain": ".eden-daoc.net",
    "path": "/",
    "secure": true,
    "httpOnly": true,
    "sameSite": "Lax"
  }
]
```

7. Dans l'application : **Menu Actions → Gérer les cookies Eden → Importer**

#### Méthode 2 : Génération automatique (TODO)

Fonctionnalité prévue pour automatiser la récupération.

### Structure du fichier de cookies

**Emplacement** : `%APPDATA%/DAOCCharacterManager/eden_cookies.json`

**Format** :
```json
{
  "cookies": [
    {
      "name": "__cf_bm",
      "value": "VALEUR_CHIFFREE_BASE64",
      "domain": ".eden-daoc.net",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax"
    }
  ],
  "created_at": "2025-01-29T10:00:00",
  "last_used": "2025-01-29T14:30:00"
}
```

### Sécurité

- ✅ Valeurs chiffrées avec cryptography (Fernet)
- ✅ Clé de chiffrement unique par installation
- ✅ Permissions fichier restrictives
- ✅ Validation du format avant utilisation

---

## 🎨 Interface utilisateur

### Fenêtre principale

#### Barre de statut Eden Herald

```
┌──────────────────────────────────────────────────────┐
│ Statut Eden Herald                                   │
├──────────────────────────────────────────────────────┤
│ ⏳ Vérification en cours...                          │
│ [🔄 Actualiser] [🔍 Recherche Herald] [⚙️ Gérer]    │
└──────────────────────────────────────────────────────┘
```

**États possibles** :
- `⏳ Vérification en cours...` (gris) → Boutons désactivés
- `✅ Herald accessible` (vert gras) → Boutons activés
- `❌ Herald inaccessible: <raison>` (rouge) → Boutons activés

#### Liste des personnages (coloration)

Les lignes sont colorées selon le royaume avec un fond subtil (alpha 25) :
- 🔴 **Albion** : Fond rouge clair
- 🔵 **Midgard** : Fond bleu clair
- 🟢 **Hibernia** : Fond vert clair

**Implémentation** : Delegates personnalisés dans `UI/delegates.py`
- `NormalTextDelegate` : Texte normal + fond coloré
- `CenterIconDelegate` : Icône centrée + fond coloré
- `CenterCheckboxDelegate` : Checkbox centrée + fond coloré

### Dialog de recherche Herald

#### Composants

1. **Champ de recherche** : QLineEdit avec validation 3+ caractères
2. **Filtre royaume** : QComboBox avec logos (20x20px)
3. **Bouton Rechercher** : Lance la recherche
4. **Tableau résultats** : QTableWidget avec 9 colonnes
5. **Boutons d'import** : Import sélection / Import tout

#### Colonnes du tableau

| Colonne | Type | Description |
|---------|------|-------------|
| ☑ | Checkbox | Sélection pour import |
| Royaume | Icon | Logo du royaume |
| Nom | Texte | Nom du personnage |
| Classe | Texte | Classe |
| Race | Texte | Race |
| Guilde | Texte | Nom de la guilde |
| Niveau | Nombre | Niveau (1-50) |
| RP | Nombre | Realm Points formatés |
| Realm Rank | Texte | Rang (ex: 12L3) |

#### Validation de recherche

```python
def start_search(self):
    query = self.search_input.text().strip()
    
    # Validation longueur minimale
    if len(query) < 3:
        QMessageBox.warning(
            self,
            "Recherche invalide",
            "Veuillez entrer au moins 3 caractères."
        )
        return
    
    # Récupération filtre royaume
    realm_filter = ""
    realm_index = self.realm_combo.currentIndex()
    if realm_index > 0:  # 0 = "Tous"
        realm_filter = ["albion", "midgard", "hibernia"][realm_index - 1]
    
    # Lancement recherche
    self.search_thread = SearchThread(query, realm_filter)
    # ...
```

#### Filtrage des résultats

Après récupération depuis le Herald, filtrage local pour précision :

```python
def on_search_finished(self, success, message, json_path):
    # ...
    search_query = self.search_input.text().strip().lower()
    
    # Filtre : seulement les noms commençant par la requête
    filtered_characters = [
        char for char in all_characters
        if char.get('clean_name', '').lower().startswith(search_query)
        or char.get('name', '').lower().startswith(search_query)
    ]
    
    # Affichage dans tableau
    self._populate_results_table(filtered_characters)
```

**Exemple** :
- Recherche : `"Ewo"`
- Herald retourne : `["Ewoline", "Ewolinette", "NewoB", "Aewo"]`
- Filtre local garde : `["Ewoline", "Ewolinette"]`
- Élimine : `["NewoB", "Aewo"]` (ne commencent pas par "Ewo")

---

## 📊 Traitement des données

### Structure de données d'un personnage

#### Données brutes du Herald

```json
{
  "rank": "1",
  "name": "Ewoline",
  "clean_name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_points": "331 862",
  "realm_rank": "12L3",
  "realm_level": "12",
  "url": "/herald/character/view/Ewoline"
}
```

#### Données après import (character_data)

```json
{
  "name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "realm": "Albion",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_rank": "12L3",
  "realm_points": 331862,
  "realm_level": "12",
  "server": "Eden",
  "mlevel": "0",
  "clevel": "0",
  "notes": "Importé depuis le Herald le 2025-01-29 14:30"
}
```

#### Transformations appliquées

1. **Détection du royaume** :
   ```python
   realm = CLASS_TO_REALM.get(class_name, "Unknown")
   ```

2. **Conversion realm_points** :
   ```python
   # Format Herald: "331 862" (string avec espaces)
   # Format final: 331862 (integer)
   if isinstance(realm_points, str):
       realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
   ```

3. **Calcul automatique du Realm Rank** :
   ```python
   rank_info = data_manager.get_realm_rank_info(realm, realm_points)
   # Retourne: {rank, title, level, realm_points}
   ```

### Calcul du Realm Rank

Le système utilise les fichiers `Data/realm_ranks_*.json` pour déterminer le rang.

**Exemple Albion** (`Data/realm_ranks_albion.json`) :
```json
{
  "1": {
    "1": {"title": "Guardian", "rp": 0},
    "2": {"title": "Guardian", "rp": 125},
    ...
  },
  "12": {
    "1": {"title": "General", "rp": 309000},
    "2": {"title": "General", "rp": 318000},
    "3": {"title": "General", "rp": 327000}
  }
}
```

**Algorithme** (`data_manager.py::get_realm_rank_info()`) :
```python
def get_realm_rank_info(realm, realm_points):
    # Conversion si string
    if isinstance(realm_points, str):
        realm_points = int(realm_points.replace(' ', '').replace('\xa0', ''))
    
    # Parcours des rangs de haut en bas
    for rank in range(max_rank, 0, -1):
        for level in range(max_level, 0, -1):
            required_rp = rank_data[rank][level]['rp']
            if realm_points >= required_rp:
                return {
                    'rank': rank,
                    'level': f"{rank}L{level}",
                    'title': rank_data[rank][level]['title'],
                    'realm_points': required_rp
                }
    
    # Par défaut : 1L1
    return {'rank': 1, 'level': '1L1', 'title': 'Guardian', 'realm_points': 0}
```

### Sauvegarde des personnages

**Structure de fichiers** :
```
Characters/
├── Albion/
│   ├── Ewoline.json
│   └── Paladin42.json
├── Midgard/
│   ├── Olaf.json
│   └── Berserker99.json
└── Hibernia/
    ├── Fionn.json
    └── Druidess.json
```

**Format du fichier** (`Ewoline.json`) :
```json
{
  "id": "uuid-unique",
  "name": "Ewoline",
  "class": "Cleric",
  "race": "Briton",
  "realm": "Albion",
  "guild": "Phoenix Rising",
  "level": "50",
  "realm_rank": "12L3",
  "realm_points": 331862,
  "realm_level": "12",
  "server": "Eden",
  "mlevel": "0",
  "clevel": "0",
  "notes": "Importé depuis le Herald le 2025-01-29 14:30",
  "page": "1",
  "armor": {
    "head": {"name": "", "type": "", "af": 0, "abs": 0, ...},
    "hands": {...},
    "arms": {...},
    "torso": {...},
    "legs": {...},
    "feet": {...}
  },
  "resists": {
    "crush": 0, "slash": 0, "thrust": 0, "heat": 0, "cold": 0, "matter": 0,
    "body": 0, "spirit": 0, "energy": 0
  }
}
```

---

## ⚠️ Gestion des erreurs

### Erreurs courantes et solutions

#### 1. "❌ Herald inaccessible: Cookies manquants ou invalides"

**Cause** : Aucun cookie configuré ou cookies expirés

**Solution** :
1. Cliquer sur "⚙️ Gérer"
2. Importer des cookies valides depuis un navigateur
3. Cliquer sur "🔄 Actualiser" pour re-vérifier

---

#### 2. "Aucun résultat trouvé pour 'xxx'"

**Causes possibles** :
- Personnage inexistant sur le serveur Eden
- Filtre de royaume incorrect
- Nom mal orthographié

**Solution** :
- Vérifier l'orthographe
- Essayer sans filtre de royaume
- Vérifier que le personnage existe bien sur Eden

---

#### 3. "Veuillez entrer au moins 3 caractères"

**Cause** : Validation de longueur minimale

**Solution** : Entrer au moins 3 caractères dans le champ de recherche

---

#### 4. "X: personnage déjà existant"

**Cause** : Tentative d'import d'un doublon

**Comportement** :
- Le personnage existant n'est pas écrasé
- Comptabilisé comme erreur dans le rapport d'import
- Les autres personnages continuent d'être importés

**Solution** : Si vous voulez mettre à jour, supprimez d'abord l'ancien personnage

---

#### 5. "Erreur lors du scraping"

**Causes possibles** :
- Page Herald modifiée (structure HTML changée)
- Timeout réseau
- Bot check activé malgré les cookies

**Solution** :
1. Vérifier la connexion Internet
2. Re-générer/importer des cookies récents
3. Attendre quelques minutes avant de réessayer
4. Consulter les logs : `Logs/app.log`

---

### Logs et débogage

#### Emplacement des logs

```
%APPDATA%/DAOCCharacterManager/Logs/
└── app.log
```

#### Niveaux de log

```python
logging.DEBUG    # Détails techniques (scraping, parsing)
logging.INFO     # Informations générales (import réussi)
logging.WARNING  # Avertissements (doublon détecté)
logging.ERROR    # Erreurs (échec scraping)
logging.CRITICAL # Erreurs critiques (crash application)
```

#### Exemple de logs lors d'une recherche

```
2025-01-29 14:30:15 [INFO] Recherche Herald: nom='Ewoline', realm='albion'
2025-01-29 14:30:16 [DEBUG] Configuration Chrome avec options off-screen
2025-01-29 14:30:17 [DEBUG] Chargement de 3 cookies depuis CookieManager
2025-01-29 14:30:18 [INFO] Navigation vers Herald: https://eden-daoc.net/herald/character/search?name=Ewoline&r=albion
2025-01-29 14:30:20 [DEBUG] Extraction de 28 tables HTML
2025-01-29 14:30:21 [INFO] Trouvé 2 personnages : ['Ewoline', 'Ewolinette']
2025-01-29 14:30:21 [DEBUG] Filtrage: garde seulement noms commençant par 'ewoline'
2025-01-29 14:30:21 [INFO] Résultats filtrés: 2 personnages
2025-01-29 14:30:22 [INFO] Sauvegarde temporaire: C:\Users\...\Temp\EdenSearchResult\characters_20250129_143022.json
2025-01-29 14:30:22 [INFO] Recherche terminée avec succès
```

#### Exemple de logs lors d'un import

```
2025-01-29 14:32:10 [INFO] Import de 2 personnages sélectionnés
2025-01-29 14:32:10 [DEBUG] Import 'Ewoline' : classe=Cleric, royaume=Albion
2025-01-29 14:32:10 [DEBUG] Vérification doublons : 45 personnages existants
2025-01-29 14:32:10 [WARNING] Doublon détecté: 'Ewoline' existe déjà
2025-01-29 14:32:10 [DEBUG] Import 'Ewolinette' : classe=Cleric, royaume=Albion
2025-01-29 14:32:10 [INFO] Sauvegarde: Characters/Albion/Ewolinette.json
2025-01-29 14:32:10 [INFO] Import terminé: 1 succès, 1 erreur
2025-01-29 14:32:10 [INFO] Rafraîchissement interface principale
```

---

## 🔧 Configuration technique

### Prérequis système

- **Python** : 3.9+
- **Selenium** : 4.15.2+
- **BeautifulSoup4** : 4.12.2+
- **Chrome/Chromium** : Version récente
- **ChromeDriver** : Compatible avec la version de Chrome

### Dépendances Python

```
selenium>=4.15.2
beautifulsoup4>=4.12.2
PySide6>=6.6.0
cryptography>=41.0.0
requests>=2.31.0
```

### Variables d'environnement (optionnelles)

```bash
# Forcer un ChromeDriver spécifique
CHROMEDRIVER_PATH=/path/to/chromedriver

# Timeout personnalisé (secondes)
HERALD_TIMEOUT=30

# Niveau de log
LOG_LEVEL=DEBUG
```

---

## 📈 Performances et limitations

### Temps de réponse moyens

| Opération | Durée moyenne | Notes |
|-----------|---------------|-------|
| Vérification statut | 2-4 secondes | Dépend de la latence réseau |
| Recherche 1 personnage | 5-8 secondes | Charge 28 tables HTML |
| Import 1 personnage | < 1 seconde | Opération locale |
| Import 10 personnages | < 2 secondes | Vérification doublons incluse |

### Limitations connues

1. **Recherche partielle** : Le Herald ne supporte pas les wildcards
   - `"Ewo*"` ne fonctionne pas
   - Solution : Entrer le début du nom exact

2. **Nombre de résultats** : Maximum ~100 personnages par recherche
   - Le Herald limite les résultats affichés
   - Solution : Utiliser des noms plus spécifiques

3. **Cookies expirés** : Durée de vie limitée (quelques heures/jours)
   - Solution : Ré-importer régulièrement

4. **Bot check** : Peut se réactiver aléatoirement
   - Solution : Attendre 5-10 minutes, ré-importer cookies

---

## 🔐 Sécurité et confidentialité

### Données sensibles

- ✅ **Cookies chiffrés** : Utilisation de Fernet (AES-128)
- ✅ **Clé unique** : Générée à l'installation
- ✅ **Stockage local** : Aucune donnée envoyée à des tiers
- ✅ **Fichiers temporaires** : Supprimés automatiquement

### Bonnes pratiques

1. **Ne pas partager** le fichier `eden_cookies.json`
2. **Ne pas commit** les cookies dans Git (`.gitignore` configuré)
3. **Exporter régulièrement** vos personnages (backup)
4. **Mettre à jour** les cookies en cas de problème d'accès

---

## 🆘 Support et dépannage

### Checklist de diagnostic

Si la recherche ne fonctionne pas :

- [ ] Vérifier la connexion Internet
- [ ] Tester l'accès manuel à https://eden-daoc.net
- [ ] Vérifier que Chrome/Chromium est installé
- [ ] Réimporter des cookies récents
- [ ] Cliquer sur "🔄 Actualiser" pour re-vérifier
- [ ] Consulter `Logs/app.log` pour les erreurs
- [ ] Essayer avec un nom de personnage connu

### Réinitialisation complète

Si rien ne fonctionne :

1. Fermer l'application
2. Supprimer `%APPDATA%/DAOCCharacterManager/eden_cookies.json`
3. Relancer l'application
4. Ré-importer des cookies frais
5. Tester la recherche

---

## 📝 Historique des versions

### Version actuelle : 0.105

**Fonctionnalités** :
- ✅ Recherche Herald avec filtre de royaume
- ✅ Import simple et en masse
- ✅ Détection automatique du royaume
- ✅ Calcul automatique du Realm Rank
- ✅ Interface colorée par royaume
- ✅ Validation des doublons
- ✅ Rafraîchissement automatique
- ✅ Gestion sécurisée des cookies
- ✅ Filtrage précis des résultats (startswith)
- ✅ Boutons grisés pendant vérification

**Corrections récentes** :
- 🐛 Fix realm_points string/int conversion
- 🐛 Fix texte en gras dans vue principale
- 🐛 Fix colonne Titre en couleur (maintenant normal)
- 🐛 Fix coloration des cellules vides
- 🐛 Fix centrage colonnes Nom et Guilde

---

## 🎓 Glossaire

**Bot check** : Système anti-automatisation du site Eden

**Cookie** : Petit fichier de session pour identifier le navigateur

**Delegate** : Composant Qt pour personnaliser le rendu des cellules

**Herald** : Site web officiel affichant les statistiques DAOC

**Realm** : Royaume (Albion, Midgard, Hibernia)

**Realm Points (RP)** : Points accumulés en RvR (combat entre royaumes)

**Realm Rank (RR)** : Rang de royaume (ex: 12L3 = Rank 12, Level 3)

**Scraper** : Programme qui extrait des données d'un site web

**Selenium** : Outil d'automatisation de navigateur web

**Thread** : Processus parallèle pour ne pas bloquer l'interface

---

## 📚 Ressources

### Documentation technique

- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [PySide6 Docs](https://doc.qt.io/qtforpython/)

### Liens Eden DAOC

- [Site principal](https://eden-daoc.net)
- [Herald](https://eden-daoc.net/herald)
- [Discord](https://discord.gg/eden-daoc)

---

## 👥 Crédits

**Développement** : ChristophePelichet  
**Version** : 0.105  
**Date** : Janvier 2025  
**License** : MIT

---

*Cette documentation est maintenue à jour avec chaque version de l'application.*
